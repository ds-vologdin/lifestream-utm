
import logging

from lifestream_requests import get_status_tv_users_lifestream
from lifestream_requests import apply_change_status_lifestream

from utm_requests import get_status_tv_users_utm

from relation_utm_lifestream import check_relations_utm_lifestream
from relation_utm_lifestream import find_change_status_to_lifestream


def main():
    logging.basicConfig(level=logging.INFO)
    utm_status_users = get_status_tv_users_utm()
    logging.info('Получили список пользователей из utm ({})'.format(
        len(utm_status_users)
    ))
    lifestream_status_users = get_status_tv_users_lifestream()
    logging.info('Получили список пользователей из lifestream ({})'.format(
        len(lifestream_status_users)
    ))
    # set_id_lifestream_to_utm(utm_status_users, lifestream_status_users)
    logging.info('Приступаем к проверке корректности связей utm и lifestream')
    check_relations_utm_lifestream(utm_status_users, lifestream_status_users)
    status_change = find_change_status_to_lifestream(
        utm_status_users, lifestream_status_users
    )
    for user in status_change:
        logging.info(
            '{0[user].login} {0[user].full_name}: utm|lifestream {0[status_utm]}|{0[status_lifestrem]}'.format(user)
        )
    logging.info('Примененяем изменения статуса на lifestream')
    apply_change_status_lifestream(status_change)


if __name__ == '__main__':
    main()
