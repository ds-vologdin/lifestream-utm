import psycopg2
from collections import namedtuple
import requests
import json
import logging
from datetime import datetime

from private_settings import DATEBASE, URL_LIFESTREAM, URL_LIFESTREAM_TEST
from utm_tariffs import utm_tariffs_lifestream_subscriptions


def get_status_tv_users_utm():
    con = psycopg2.connect(**DATEBASE)
    cur = con.cursor()

    # Ищем пользователей с тарифными связками:
    # 1303, 1309, 1310, 1515, 1516, 1517, 1518
    sql = '''SELECT DISTINCT t5.login, t5.full_name, t1.balance, t2.block_type,
    t2.start_date, t2.expire_date, t2.is_deleted, t5.id, t9.value,
    array(
        SELECT tariff_id
        FROM tariffs tt1
        LEFT JOIN tariffs_services_link tt2 ON tt1.id = tt2.tariff_id
        LEFT JOIN service_links tt3 ON tt3.service_id = tt2.service_id
        WHERE tt3.user_id = t5.id AND tt3.is_deleted = 0
    )
    FROM accounts t1
    LEFT JOIN blocks_info t2 ON (t1.id = t2.account_id AND
    t2.id = (SELECT MAX(id)
             FROM blocks_info WHERE account_id = t1.id))
    LEFT JOIN users_accounts t3 ON t1.id = t3.account_id
    LEFT JOIN users t5 ON t5.id = t3.uid
    LEFT JOIN service_links t6 ON t6.user_id = t5.id
    LEFT JOIN tariffs_services_link t7 ON t6.service_id = t7.service_id
    LEFT JOIN tariffs t8 ON t8.id = t7.tariff_id
    LEFT JOIN user_additional_params t9 ON t9.userid = t5.id AND t9.paramid = 3
    WHERE t7.tariff_id IN (1515, 1516, 1517, 1518, 1594, 1662) AND
    t6.is_deleted = 0
    '''
    cur.execute(sql)
    logging.debug(cur.query)
    users_status = cur.fetchall()
    UserStatus = namedtuple(
        'UserStatus',
        ['login', 'full_name', 'balance', 'block_type',
         'last_block_start_date', 'last_block_expire_date',
         'last_block_is_deleted', 'user_id', 'lifestream_id', 'tarifs_id'],
        verbose=False
    )
    cur.close()
    con.close()
    return list(map(UserStatus._make, users_status))


def get_status_tv_users_lifestream():
    accounts_json = requests.get('{}/v2/accounts?page_size=100&page=0'.format(
        URL_LIFESTREAM
    ))
    accounts_request = json.loads(accounts_json.text)
    accounts = accounts_request['accounts']
    for i in range(1, accounts_request['pagination']['pages']):
        accounts_json_page = requests.get(
            '{}/v2/accounts?page_size=100&page={}'.format(
                URL_LIFESTREAM, i
            )
        )
        accounts += json.loads(accounts_json_page.text)['accounts']
    return accounts


def find_users_in_utm(user_lifestream, utm_status_users):
    found_users_utm = set()
    for utm_user in utm_status_users:
        # Сравниваем ФИО на полное соответствие
        # часть логинов в lifestrem вида gtsXXXXX, где XXXXX - логин в utm
        if any((user_lifestream['info']['fio'] == utm_user.full_name,
                user_lifestream['username'][3:] == utm_user.login)):
            found_users_utm.add((utm_user.login, utm_user.user_id))
    return found_users_utm


def fetch_parameter_id_lifestream_from_utm(cur, utm_userid):
    # paramid = 3 - параметр c информацией об id lifestream
    sql = '''SELECT value, id FROM user_additional_params
        WHERE userid = %s AND paramid = 3;
    '''
    cur.execute(sql, (utm_userid, ))
    logging.debug(cur.query)
    return cur.fetchone()


def update_parameter_id_lifestream_into_utm(cur, utm_userid, id_lifestream):
    sql = '''UPDATE user_additional_params SET value=%s WHERE id = %s;'''
    cur.execute(sql, (id_lifestream, utm_userid))
    logging.info(cur.query)


def insert_parameter_id_lifestream_into_utm(
    cur, utm_parameter_id, id_lifestream
):
    # paramid = 3 - параметр c информацией об id lifestream
    sql = '''INSERT INTO user_additional_params(
        paramid, userid, value)
        VALUES (3, %s, %s);'''
    cur.execute(sql, (utm_parameter_id, id_lifestream))
    logging.info(cur.query)


def set_id_lifestream_to_utm_user(cur, utm_userid, id_lifestream):
    lifestream_in_utm = fetch_parameter_id_lifestream_from_utm(
        cur, utm_userid
    )
    if not lifestream_in_utm:
        insert_parameter_id_lifestream_into_utm(
            cur, utm_userid, id_lifestream
        )
        return

    if lifestream_in_utm[0] != id_lifestream:
        logging.error(
            'Не совпадают id lifestream с данными в utm: {} - {}'.format(
                lifestream_in_utm[0], id_lifestream
            )
        )
        update_parameter_id_lifestream_into_utm(
            cur, utm_userid, id_lifestream
        )


def set_id_lifestream_to_utm(utm_status_users, lifestream_status_users):
    con = psycopg2.connect(**DATEBASE)
    cur = con.cursor()

    for user_lifestream in lifestream_status_users:
        user_info_str = 'id: {} ; username: {} ({})'.format(
            user_lifestream['id'],
            user_lifestream['username'],
            user_lifestream['info']['fio'],
        )
        found_users_utm = find_users_in_utm(user_lifestream, utm_status_users)

        user_info_str += ' -> {}'.format(', '.join(map(str, found_users_utm)))
        logging.debug(user_info_str)

        if len(found_users_utm) != 1:
            logging.error('{} не найдено соответствие в utm ({})'.format(
                user_info_str, ', '.join(map(str, found_users_utm))
            ))
            continue

        found_user_utm = found_users_utm.pop()
        set_id_lifestream_to_utm_user(
            cur, found_user_utm[1], user_lifestream['id']
        )
    con.commit()
    cur.close()
    con.close()


def get_users_utm_with_id_lifestream(utm_status_users):
    return [user for user in utm_status_users if user.lifestream_id]


def get_lifestream_user(lifestream_id, lifestream_status_users):
    for user in lifestream_status_users:
        if user['id'] == lifestream_id:
            return user


def is_active_utm_user(user):
    if (user.last_block_expire_date > datetime.now().timestamp() and
            not user.last_block_is_deleted):
        return False
    return True


def is_active_lifestream_user(user):
    return bool(user['subscriptions'])


def find_change_status_to_lifestream(utm_status_users,
                                     lifestream_status_users):
    utm_users = get_users_utm_with_id_lifestream(utm_status_users)

    change_status_users = []
    for utm_user in utm_users:
        logging.debug(utm_user.full_name)
        lifestrem_user = get_lifestream_user(
            utm_user.lifestream_id, lifestream_status_users
        )
        logging.debug(lifestrem_user)
        status_user_in_utm = is_active_utm_user(utm_user)
        status_user_in_lifestream = is_active_lifestream_user(lifestrem_user)
        if status_user_in_utm != status_user_in_lifestream:
            change_status_users.append({
                'user': utm_user,
                'status_utm': status_user_in_utm,
                'status_lifestrem': status_user_in_lifestream,
                'subscriptions': lifestrem_user['subscriptions'],
            })
    return change_status_users


def post_requests_to_lifestream(user_id, json_requests):
    # тестовая учётка
    user_id = '5b585202861ff302647e5e52'
    for json_request in json_requests:
        # Посылаем на тестовый урл. Пока этап отладки...
        url = '{}/v2/accounts/{}/subscriptions'.format(
            URL_LIFESTREAM_TEST, user_id
        )
        r = requests.post(url, data=json_request)
        logging.info('{} ({}) - {}: {}'.format(
            url, json_request, r.status_code, r.text
        ))


def remove_subscriptions_user(id_lifestream, subscriptions):
    subscriptions_json = [
        json.dumps({'id': '{}'.format(subscription), 'valid': False})
        for subscription in subscriptions
    ]
    post_requests_to_lifestream(id_lifestream, subscriptions_json)


def add_subscriptions_user(id_lifestream, subscriptions_id):
    subscriptions_json = []
    subscriptions_lifestream = [
        utm_tariffs_lifestream_subscriptions[subscription]
        for subscription in subscriptions_id
        if subscription in utm_tariffs_lifestream_subscriptions
    ]
    subscriptions_json = [
        json.dumps({'id': '{}'.format(subscription), 'valid': True})
        for subscription in subscriptions_lifestream
    ]
    post_requests_to_lifestream(id_lifestream, subscriptions_json)


def apply_change_status_lifestream(status_change):
    for user_change in status_change:
        user = user_change['user']
        # remove_subscriptions_user(user.lifestream_id, (101, 102, 103))
        # continue
        if user_change['status_utm']:
            add_subscriptions_user(user.lifestream_id, user.tarifs_id)
        else:
            remove_subscriptions_user(user.lifestream_id,
                                      user_change['subscriptions'])


def main():
    logging.basicConfig(level=logging.INFO)
    utm_status_users = get_status_tv_users_utm()
    lifestream_status_users = get_status_tv_users_lifestream()
    set_id_lifestream_to_utm(utm_status_users, lifestream_status_users)
    status_change = find_change_status_to_lifestream(
        utm_status_users, lifestream_status_users
    )
    for user in status_change:
        logging.info(
            '{0[user].login} {0[user].full_name}: utm|lifestream {0[status_utm]}|{0[status_lifestrem]}'.format(user)
        )
    apply_change_status_lifestream(status_change)


if __name__ == '__main__':
    main()
