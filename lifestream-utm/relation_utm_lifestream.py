import logging
from datetime import datetime


logger = logging.getLogger(__name__)


def find_users_in_utm(user_lifestream, utm_status_users):
    found_users_utm = set()
    for utm_user in utm_status_users:
        # Сравниваем ФИО на полное соответствие
        # часть логинов в lifestream вида gtsXXXXX, где XXXXX - логин в utm
        if any((user_lifestream['info']['fio'] == utm_user.full_name,
                user_lifestream['username'][3:] == utm_user.login)):
            found_users_utm.add((utm_user.login, utm_user.user_id))
    return found_users_utm


def find_user_in_lifestream(utm_user, lifestream_status_users):
    for lifestream_user in lifestream_status_users:
        # Сравниваем ФИО на полное соответствие
        # часть логинов в lifestream вида gtsXXXXX, где XXXXX - логин в utm
        if any((lifestream_user['info']['fio'] == utm_user.full_name,
                lifestream_user['username'][3:] == utm_user.login)):
            # id уникальный в lifestream, потому можно найти только одно
            # соответствие
            return lifestream_user


def _check_relations_utm_lifestream(utm_status_users, lifestream_status_users):
    no_relations_in_utm = []
    for user_lifestream in lifestream_status_users:
        found_users_utm = find_users_in_utm(user_lifestream, utm_status_users)
        if not len(found_users_utm) != 1:
            continue
        no_relations_in_utm.append((user_lifestream, found_users_utm))

    no_relations_in_lifestream = []
    for user_utm in utm_status_users:
        if not find_user_in_lifestream(user_utm, lifestream_status_users):
            no_relations_in_lifestream.append(user_utm)
    return no_relations_in_utm, no_relations_in_lifestream


def check_relations_utm_lifestream(utm_status_users, lifestream_status_users):
    no_relations_in_utm, no_relations_in_lifestream = _check_relations_utm_lifestream(
        utm_status_users, lifestream_status_users)
    for user_lifestream, users_utm in no_relations_in_utm:
        user_info_str = 'id: {} ; username: {} ({})'.format(
            user_lifestream['id'],
            user_lifestream['username'],
            user_lifestream['info']['fio'],
        )
        if users_utm:
            user_info_str += ' -> {}'.format(', '.join(map(str, users_utm)))
        else:
            user_info_str += ' -> не найдено'
        logger.warning(user_info_str)

    for user_utm in no_relations_in_lifestream:
        logger.warning(
            'id: %s ; utm full name: %s (%s) -> не найден в lifestream',
            user_utm.lifestream_id, user_utm.full_name, user_utm.login
        )


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


def find_change_status_to_lifestream(
        utm_status_users, lifestream_status_users):
    utm_users = get_users_utm_with_id_lifestream(utm_status_users)

    change_status_users = []
    for utm_user in utm_users:
        logger.debug(utm_user.full_name)
        lifestream_user = get_lifestream_user(
            utm_user.lifestream_id, lifestream_status_users
        )
        logger.debug(lifestream_user)
        if not lifestream_user:
            continue
        status_user_in_utm = is_active_utm_user(utm_user)
        status_user_in_lifestream = is_active_lifestream_user(lifestream_user)
        if status_user_in_utm != status_user_in_lifestream:
            change_status_users.append({
                'user': utm_user,
                'status_utm': status_user_in_utm,
                'status_lifestream': status_user_in_lifestream,
                'subscriptions': lifestream_user['subscriptions'],
            })
    return change_status_users
