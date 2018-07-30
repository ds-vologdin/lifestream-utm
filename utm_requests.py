import psycopg2
import logging
from collections import namedtuple

from private_settings import DATEBASE


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
