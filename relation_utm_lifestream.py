import psycopg2
import logging
from datetime import datetime

from utm_requests import fetch_parameter_id_lifestream_from_utm
from utm_requests import insert_parameter_id_lifestream_into_utm
from utm_requests import update_parameter_id_lifestream_into_utm

from private_settings import DATEBASE


logger = logging.getLogger(__name__)


def find_users_in_utm(user_lifestream, utm_status_users):
    found_users_utm = set()
    for utm_user in utm_status_users:
        # Сравниваем ФИО на полное соответствие
        # часть логинов в lifestrem вида gtsXXXXX, где XXXXX - логин в utm
        if any((user_lifestream['info']['fio'] == utm_user.full_name,
                user_lifestream['username'][3:] == utm_user.login)):
            found_users_utm.add((utm_user.login, utm_user.user_id))
    return found_users_utm


def find_user_in_lifestream(utm_user, lifestream_status_users):
    for lifestream_user in lifestream_status_users:
        # Сравниваем ФИО на полное соответствие
        # часть логинов в lifestrem вида gtsXXXXX, где XXXXX - логин в utm
        if any((lifestream_user['info']['fio'] == utm_user.full_name,
                lifestream_user['username'][3:] == utm_user.login)):
            # id уникальный в lifestream, потому можно найти только одно
            # соответствие
            return lifestream_user


def set_id_lifestream_to_utm(utm_status_users, lifestream_status_users):
    '''Функция для установки id lifestream в параметрах пользователя utm'''
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
        logger.debug(user_info_str)

        if len(found_users_utm) != 1:
            logger.error('{} не найдено соответствие в utm ({})'.format(
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
        logger.error(
            'Не совпадают id lifestream с данными в utm: {} - {}'.format(
                lifestream_in_utm[0], id_lifestream
            )
        )
        update_parameter_id_lifestream_into_utm(
            cur, utm_userid, id_lifestream
        )


def check_relations_utm_lifestream(utm_status_users, lifestream_status_users):
    for user_lifestream in lifestream_status_users:
        found_users_utm = find_users_in_utm(user_lifestream, utm_status_users)
        if not len(found_users_utm) != 1:
            continue

        user_info_str = 'id: {} ; username: {} ({})'.format(
            user_lifestream['id'],
            user_lifestream['username'],
            user_lifestream['info']['fio'],
        )
        if found_users_utm:
            user_info_str += ' -> {}'.format(
                ', '.join(map(str, found_users_utm))
            )
        else:
            user_info_str += ' -> не найдено'
        logger.warning(user_info_str)

    for user_utm in utm_status_users:
        if not find_user_in_lifestream(user_utm, lifestream_status_users):
            logger.warning(
                'id: {} ; utm full name: {} ({}) -> не найден в lifestream'.format(
                    user_utm.lifestream_id, user_utm.full_name, user_utm.login
                ))


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
        logger.debug(utm_user.full_name)
        lifestrem_user = get_lifestream_user(
            utm_user.lifestream_id, lifestream_status_users
        )
        logger.debug(lifestrem_user)
        if not lifestrem_user:
            continue
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
