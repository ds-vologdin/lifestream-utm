import logging
import psycopg2

from .utm_requests import fetch_parameter_id_lifestream_from_utm
from .utm_requests import insert_parameter_id_lifestream_into_utm
from .utm_requests import update_parameter_id_lifestream_into_utm
from .relation_utm_lifestream import find_users_in_utm

from settings.private_settings import DATEBASE


logger = logging.getLogger(__name__)


def set_id_lifestream_to_utm(utm_status_users, lifestream_status_users):
    """
    Функция для установки id lifestream в параметрах пользователя utm.
    Пользоваться функцией с крайней осторожностью. Может сломать логику работы UTM.
    """
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
