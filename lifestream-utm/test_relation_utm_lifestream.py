import pytest
import datetime

import relation_utm_lifestream
from utm_requests import UserStatus


@pytest.fixture(
    params=[
        ((datetime.datetime.now().timestamp()-600, 0), True),
        ((datetime.datetime.now().timestamp()-600, 1), True),
        ((datetime.datetime.now().timestamp()+600, 0), False),
        ((datetime.datetime.now().timestamp()+600, 1), True),
    ],
    ids=[
        'last_block_expire_date < now and not deleted',
        'last_block_expire_date < now and deleted',
        'last_block_expire_date > now and not deleted',
        'last_block_expire_date > now and deleted',
    ]
)
def active_user_params(request):
    return request.param


def test_is_active_lifestream_user(active_user_params):
    params, result = active_user_params
    user = UserStatus(
        login='11278', full_name='User1', balance=184.62, block_type=1,
        last_block_start_date=1538342370, last_block_expire_date=params[0],
        last_block_is_deleted=params[1], user_id=1146, lifestream_id='59e76927eea9ae0ce20c222e',
        tarifs_id=[1311, 1517]
    )
    assert relation_utm_lifestream.is_active_utm_user(user) is result


def test_get_users_utm_with_id_lifestream():
    users = [
        UserStatus(
            login='11278', full_name='User1', balance=184.62, block_type=1,
            last_block_start_date=1538342370, last_block_expire_date=datetime.datetime.now().timestamp(),
            last_block_is_deleted=True, user_id=1146, lifestream_id='59e76927eea9ae0ce20c222e',
            tarifs_id=[1311, 1517]
        ),
        UserStatus(
            login='11272', full_name='User2', balance=184.62, block_type=1,
            last_block_start_date=1538342370, last_block_expire_date=datetime.datetime.now().timestamp(),
            last_block_is_deleted=True, user_id=1146, lifestream_id=None,
            tarifs_id=[1311, 1517]
        ),
    ]
    user_with_id_lifestream =  relation_utm_lifestream.get_users_utm_with_id_lifestream(users)
    assert len(user_with_id_lifestream) == 1
    assert user_with_id_lifestream[0].login == '11278'
    assert user_with_id_lifestream[0].lifestream_id == '59e76927eea9ae0ce20c222e'
