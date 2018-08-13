
import logging
import argparse

from lifestream_requests import get_status_tv_users_lifestream
from lifestream_requests import apply_change_status_lifestream

from utm_requests import get_status_tv_users_utm

from relation_utm_lifestream import check_relations_utm_lifestream
from relation_utm_lifestream import find_change_status_to_lifestream


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--check-relations', action='store_true',
        help='no check relation utm and lifestream records'
    )
    parser.add_argument(
        '--no-apply-change', action='store_true',
        help='no apply change statuses'
    )
    return parser.parse_args()


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_arguments()

    utm_status_users = get_status_tv_users_utm()
    logging.info('Получили список пользователей из utm ({})'.format(
        len(utm_status_users)
    ))

    lifestream_status_users = get_status_tv_users_lifestream()
    logging.info('Получили список пользователей из lifestream ({})'.format(
        len(lifestream_status_users)
    ))

    if args.check_relations:
        logging.info(
            'Приступаем к проверке корректности связей utm и lifestream'
        )
        check_relations_utm_lifestream(
            utm_status_users, lifestream_status_users
        )

    status_change = find_change_status_to_lifestream(
        utm_status_users, lifestream_status_users
    )
    logging.info('Список изменившихся статусов')
    for user in status_change:
        logging.info(
            '{0[user].login} {0[user].full_name}: utm|lifestream {0[status_utm]}|{0[status_lifestrem]}'.format(user)
        )

    if not args.no_apply_change:
        logging.info('Примененяем изменения статуса на lifestream')
        apply_change_status_lifestream(status_change)


if __name__ == '__main__':
    main()
