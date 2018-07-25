import psycopg2
from collections import namedtuple

from private_settings import DATEBASE


def get_status_tv_users_utm():

    con = psycopg2.connect(
        'host={host} port={port} dbname={db} user={user} password={passwd}'.format(
            **DATEBASE
        )
    )
    cur = con.cursor()
    # группа с id 5003 - абоненты с услугой ТВ
    sql = '''SELECT t5.login, t5.full_name, t1.balance, t2.block_type,
    t2.start_date, t2.expire_date, t2.is_deleted
    FROM accounts t1
    LEFT OUTER JOIN blocks_info t2 ON (t1.id = t2.account_id AND
    t2.start_date = (SELECT MAX(start_date)
                     FROM blocks_info WHERE account_id = t1.id))
    LEFT JOIN users_accounts t3 ON t1.id = t3.account_id
    LEFT JOIN users_groups_link t4 ON t3.uid = t4.user_id
    LEFT JOIN users t5 ON t5.id = t3.uid
    WHERE t4.group_id = 5003;
    '''
    cur.execute(sql)
    users_status = cur.fetchall()
    UserStatistic = namedtuple(
        'UserStatistic',
        ['login', 'full_name', 'balance', 'block_type', 'start_date',
         'expire_date', 'is_deleted'],
        verbose=True)
    users_status = list(map(UserStatistic._make, users_status))
    return users_status


def get_status_tv_users_lifestream(): ...


def find_change_status_to_lifestream(utm_status_users, lifestream_status_user):
    ...


def apply_change_status_lifestream(status_change): ...


def main():
    utm_status_users = get_status_tv_users_utm()
    print(utm_status_users)
    lifestream_status_user = get_status_tv_users_lifestream()
    status_change = find_change_status_to_lifestream(
        utm_status_users, lifestream_status_user
    )
    apply_change_status_lifestream(status_change)


if __name__ == '__main__':
    main()
