import logging
import argparse

from lifestream_requests import get_status_tv_users_lifestream
from lifestream_requests import apply_change_status_lifestream

from utm_requests import get_status_tv_users_utm

from relation_utm_lifestream import check_relations_utm_lifestream
from relation_utm_lifestream import find_change_status_to_lifestream

from send_email import send_report_to_email


logger = logging.getLogger(__file__)


def convert_str_to_logging_level(level_str=None):
    level_logging = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }
    return level_logging.get(level_str, logging.WARNING)


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
    parser.add_argument(
        '--log-file', default=None,
        help='default: None (print log to stdin)'
    )
    parser.add_argument(
        '--log-level',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        default='warning',
        help='default: warning'
    )
    parser.add_argument(
        '--email-report', default=None,
        help='default: None (report not send to email). Use: --email-report "a@test.com, b@test.com"'
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    logging.basicConfig(
        filename=args.log_file,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=convert_str_to_logging_level(args.log_level)
    )

    utm_status_users = get_status_tv_users_utm()
    logger.info('Получили список пользователей из utm (%s)', len(utm_status_users))

    lifestream_status_users = get_status_tv_users_lifestream()
    logger.info('Получили список пользователей из lifestream (%s)', len(lifestream_status_users))

    if args.check_relations:
        logger.info('Приступаем к проверке корректности связей utm и lifestream')
        check_relations_utm_lifestream(
            utm_status_users, lifestream_status_users
        )

    status_change = find_change_status_to_lifestream(
        utm_status_users, lifestream_status_users
    )
    logger.info('Список изменившихся статусов')
    for user in status_change:
        logger.info(
            '%s %s %s: utm|lifestream tariffs %s|%s status %s|%s',
            user['user'].login,
            user['user'].lifestream_id,
            user['user'].full_name,
            user['user'].tariffs_id,
            user['subscriptions'],
            user['status_utm'],
            user['status_lifestream']
        )
        logger.debug(user['user'])
        logger.debug(user['lifestream_user'])

    if args.no_apply_change:
        return

    logger.info('Примененяем изменения статуса на lifestream')
    apply_change_status_lifestream(status_change)

    send_report_to_email(args.email_report, status_change)


if __name__ == '__main__':
    main()
