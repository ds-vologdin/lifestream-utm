import pytest
import datetime

from lifestream_utm import relation_utm_lifestream
from lifestream_utm.utm_requests import UserStatus


@pytest.fixture(
    params=[
        ((datetime.datetime.now().timestamp()-600, False), True),
        ((datetime.datetime.now().timestamp()-600, True), True),
        ((datetime.datetime.now().timestamp()+600, False), False),
        ((datetime.datetime.now().timestamp()+600, True), True),
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


@pytest.fixture
def utm_users():
    return [
        UserStatus(
            login='11278', full_name='User1', balance=184.62, block_type=1,
            last_block_start_date=1538342370, last_block_expire_date=datetime.datetime.now().timestamp()+600,
            last_block_is_deleted=False, user_id=1146, lifestream_id='567bc88ce2a6fe09ce000111',
            tariffs_id=[1311, 1517], deleted_tariffs_id=[]
        ),
        UserStatus(
            login='11272', full_name='User2', balance=184.62, block_type=1,
            last_block_start_date=1538342370, last_block_expire_date=datetime.datetime.now().timestamp(),
            last_block_is_deleted=True, user_id=1146, lifestream_id=None,
            tariffs_id=[1311, 1517], deleted_tariffs_id=[]
        ),
        UserStatus(
            login='11233', full_name='User3', balance=184.62, block_type=1,
            last_block_start_date=1538342370, last_block_expire_date=datetime.datetime.now().timestamp(),
            last_block_is_deleted=True, user_id=1146, lifestream_id='567bc88ce2a6fe09ce000112',
            tariffs_id=[1311, 1517, 1716], deleted_tariffs_id=[]
        ),
        UserStatus(
            login='12433', full_name='User4', balance=184.62, block_type=1,
            last_block_start_date=1538342370, last_block_expire_date=datetime.datetime.now().timestamp(),
            last_block_is_deleted=True, user_id=1146, lifestream_id='567bc88ce2a6fe09ce000113',
            tariffs_id=[1311, 1517, 1716], deleted_tariffs_id=[]
        ),
        UserStatus(
            login='12433', full_name='User5', balance=184.62, block_type=1,
            last_block_start_date=1538342370, last_block_expire_date=datetime.datetime.now().timestamp(),
            last_block_is_deleted=True, user_id=1146, lifestream_id='567bc88ce2a6fe09ce000114',
            tariffs_id=[1311], deleted_tariffs_id=[]
        ),
    ]


def test_is_active_utm_user(active_user_params):
    params, result = active_user_params
    user = UserStatus(
        login='11278', full_name='User1', balance=184.62, block_type=1,
        last_block_start_date=1538342370, last_block_expire_date=params[0],
        last_block_is_deleted=params[1], user_id=1146, lifestream_id='59e76927eea9ae0ce20c222e',
        tariffs_id=[1311, 1517], deleted_tariffs_id=[]
    )
    assert relation_utm_lifestream.is_active_utm_user(user) is result


def test_get_users_utm_with_id_lifestream(utm_users):
    user_with_id_lifestream = relation_utm_lifestream.get_users_utm_with_id_lifestream(utm_users)
    assert len(user_with_id_lifestream) == 4
    assert user_with_id_lifestream[0].login == '11278'
    assert user_with_id_lifestream[0].lifestream_id == '567bc88ce2a6fe09ce000111'


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
def lifestream_users():
    return [
        {
            'updated': '2018-10-09 08:01:07.197000+03:00',
            'id': '567bc88ce2a6fe09ce000111', 'city': '',
            'email': 'anton@mail.ru', 'username': 'test1',
            'info': {
                'fio': 'User1', 'activation_date': '24.12.15', 'period': '',
                'address': 'г.Киров'
            },
            'subscriptions': [{'id': '109'}], 'is_blocked': False,
            'created': '2015-12-24 13:27:24.189000+03:00'
        },
        {
            'updated': '2018-10-09 08:01:07.197000+03:00',
            'id': '567bc88ce2a6fe09ce000112', 'city': '',
            'email': 'anton@mail.ru', 'username': 'gts11272',
            'info': {
                'fio': 'Учетка для теста', 'activation_date': '24.12.15', 'period': '',
                'address': 'г.Киров'
            },
            'subscriptions': [], 'is_blocked': False,
            'created': '2015-12-24 13:27:24.189000+03:00'
        },
        {
            'updated': '2018-10-09 08:01:07.197000+03:00',
            'id': '567bc88ce2a6fe09ce000113', 'city': '',
            'email': 'anton@mail.ru', 'username': 'test3',
            'info': {
                'fio': 'Учетка для теста', 'activation_date': '24.12.15', 'period': '',
                'address': 'г.Киров'
            },
            'subscriptions': [{'id': '110'}], 'is_blocked': False,
            'created': '2015-12-24 13:27:24.189000+03:00'
        },
    ]


def test_get_lifestream_user(id_lifestream_params, lifestream_users):
    id_lifestream, result = id_lifestream_params
    user = relation_utm_lifestream.get_lifestream_user(
        id_lifestream, lifestream_users)
    assert bool(user) == result


def test_get_lifestream_user_correct(lifestream_users):
    user = relation_utm_lifestream.get_lifestream_user(
        '567bc88ce2a6fe09ce000112', lifestream_users)
    assert user['username'] == 'gts11272'


def test_is_active_lifestream_user(lifestream_users):
    user_0, user_1, *_ = lifestream_users
    is_active = relation_utm_lifestream.is_active_lifestream_user(user_0)
    assert is_active is True
    is_active = relation_utm_lifestream.is_active_lifestream_user(user_1)
    assert is_active is False


def test_find_change_status_to_lifestream(utm_users, lifestream_users):
    change = relation_utm_lifestream.find_change_status_to_lifestream(
        utm_users, lifestream_users)
    assert len(change) == 2
    assert change[0]['user'].full_name == 'User1'
    assert change[0]['status_lifestream'] is True
    assert change[0]['status_utm'] is False
    assert len(change[0]['subscriptions']) == 1
    assert change[0]['subscriptions'][0]['id'] == '109'

    assert change[1]['user'].full_name == 'User3'
    assert change[1]['status_lifestream'] is False
    assert change[1]['status_utm'] is True
    assert len(change[1]['subscriptions']) == 0
    assert change[1]['user'].tariffs_id == [1311, 1517, 1716]


def test_check_relations_utm_lifestream(utm_users, lifestream_users):
    no_relations_in_utm, no_relations_in_lifestream = relation_utm_lifestream._check_relations_utm_lifestream(
        utm_users, lifestream_users)
    assert len(no_relations_in_utm) == 1
    assert no_relations_in_utm[0][0]['username'] == 'test3'

    assert len(no_relations_in_lifestream) == 3
    assert no_relations_in_lifestream[0].full_name == 'User3'
    assert no_relations_in_lifestream[1].full_name == 'User4'
