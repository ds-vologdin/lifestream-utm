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


@pytest.fixture(
    params=[
        ('567bc88ce2a6fe09ce000111', True),
        ('567bc88ce2a6fe09ce000110', False),
    ],
    ids=[
        'find id in lifestream user',
        'not find id in lifestream user',
    ]
)
def id_lifestream_params(request):
    return request.param


@pytest.fixture
def lifestream_status_users():
    return [
        {
            'updated': '2018-10-09 08:01:07.197000+03:00',
            'id': '567bc88ce2a6fe09ce000111', 'city': '',
            'email': 'anton@mail.ru', 'username': 'test1',
            'info': {
                'fio': 'Учетка для теста', 'activation_date': '24.12.15', 'period': '',
                'address': 'г.Киров'
            },
            'subscriptions': [{'id': '109'}], 'is_blocked': False,
            'created': '2015-12-24 13:27:24.189000+03:00'
        },
        {
            'updated': '2018-10-09 08:01:07.197000+03:00',
            'id': '567bc88ce2a6fe09ce000112', 'city': '',
            'email': 'anton@mail.ru', 'username': 'test2',
            'info': {
                'fio': 'Учетка для теста', 'activation_date': '24.12.15', 'period': '',
                'address': 'г.Киров'
            },
            'subscriptions': [{'id': '109'}], 'is_blocked': False,
            'created': '2015-12-24 13:27:24.189000+03:00'
        },
    ]


def test_get_lifestream_user(id_lifestream_params, lifestream_status_users):
    id_lifestream, result = id_lifestream_params
    user = relation_utm_lifestream.get_lifestream_user(
        id_lifestream, lifestream_status_users)
    assert bool(user) == result


def test_get_lifestream_user_correct(lifestream_status_users):
    user = relation_utm_lifestream.get_lifestream_user(
        '567bc88ce2a6fe09ce000112', lifestream_status_users)
    assert user['username'] == 'test2'
