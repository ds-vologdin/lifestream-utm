import psycopg2
from collections import namedtuple
import requests
import json
import logging

from private_settings import DATEBASE, URL_LIFESTREAM


def get_status_tv_users_utm():
    con = psycopg2.connect(
        'host={host} port={port} dbname={db} user={user} password={passwd}'.format(
            **DATEBASE
        )
    )
    cur = con.cursor()

    # Ищем пользователей с тарифными связками:
    # 1303, 1309, 1310, 1515, 1516, 1517, 1518
    sql = '''SELECT DISTINCT t5.login, t5.full_name, t1.balance, t2.block_type,
    t2.start_date, t2.expire_date, t2.is_deleted, t5.id, t9.value
    FROM accounts t1
    LEFT JOIN blocks_info t2 ON (t1.id = t2.account_id AND
    t2.id = (SELECT MAX(id)
             FROM blocks_info WHERE account_id = t1.id))
    LEFT JOIN users_accounts t3 ON t1.id = t3.account_id
    LEFT JOIN users t5 ON t5.id = t3.uid
    LEFT JOIN service_links t6 ON t6.user_id = t5.id
    LEFT JOIN tariffs_services_link t7 ON t6.service_id = t7.service_id
    LEFT JOIN tariffs t8 ON t8.id = t7.tariff_id
    LEFT JOIN user_additional_params t9 ON t9.userid = t5.id
    WHERE t7.tariff_id IN (1515, 1516, 1517, 1518, 1594, 1662) AND
    t6.is_deleted = 0
    '''
    cur.execute(sql)
    logging.debug(cur.query)
    users_status = cur.fetchall()
    UserStatus = namedtuple(
        'UserStatus',
        ['login', 'full_name', 'balance', 'block_type', 'start_date',
         'expire_date', 'is_deleted', 'user_id', 'lifestream_id'],
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
        if user_lifestream['info']['fio'] == utm_user.full_name:
            found_users_utm.add((utm_user.login, utm_user.user_id))
        # часть логинов в lifestrem вида gtsXXXXX, где XXXXX - логин в utm
        if user_lifestream['username'][3:] == utm_user.login:
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
    con = psycopg2.connect(
        'host={host} port={port} dbname={db} user={user} password={passwd}'.format(
            **DATEBASE
        )
    )
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


def find_change_status_to_lifestream(utm_status_users,
                                     lifestream_status_users): ...


def apply_change_status_lifestream(status_change): ...


def main():
    logging.basicConfig(level=logging.INFO)
    utm_status_users = get_status_tv_users_utm()
    # print(utm_status_users)
    lifestream_status_users = get_status_tv_users_lifestream()
    # for user in lifestream_status_users:
    #     print(user)
    set_id_lifestream_to_utm(utm_status_users, lifestream_status_users)
    status_change = find_change_status_to_lifestream(
        utm_status_users, lifestream_status_users
    )
    apply_change_status_lifestream(status_change)


if __name__ == '__main__':
    main()
