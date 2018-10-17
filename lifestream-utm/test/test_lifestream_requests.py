import datetime

from lifestream_utm.lifestream_requests import get_status_tv_users_lifestream
from lifestream_utm.lifestream_requests import get_subscriptions_tv_user_lifestream
from lifestream_utm.lifestream_requests import add_subscriptions_user
from lifestream_utm.lifestream_requests import remove_subscriptions_user
from lifestream_utm.lifestream_requests import apply_change_status_lifestream

from lifestream_utm.utm_requests import UserStatus

from settings.utm_tariffs import UTM_TARIFFS_LIFESTREAM_SUBSCRIPTIONS

ID_TEST_USER = '567bc88ce2a6fe09ce0008d3'


def test_get_status_tv_users_lifestream():
    users = get_status_tv_users_lifestream()

    assert isinstance(users, list)
    assert len(users) > 0

    user = users[0]
    assert isinstance(user, dict)
    assert 'username' in user
    assert 'subscriptions' in user
    assert 'info' in user
    assert 'id' in user
    assert 'email' in user
    assert 'created' in user
    assert 'is_blocked' in user
    assert 'city' in user
    assert 'updated' in user

    assert isinstance(user['subscriptions'], list)

    info = user['info']
    assert 'address' in info
    assert 'activation_date' in info
    assert 'period' in info
    assert 'fio' in info


def test_get_subscriptions_tv_user_lifestream():
    subscriptions = get_subscriptions_tv_user_lifestream(ID_TEST_USER)
    assert isinstance(subscriptions, list)

    for subscription in subscriptions:
        assert 'id' in subscription
        # У нас пока нет полного соответствия тарифов, так на тестовой учётке тариф,
        # который мы не подключаем клиентам
        # assert subscription['id'] in UTM_TARIFFS_LIFESTREAM_SUBSCRIPTIONS.values()


def get_test_subscriptions(subscriptions):
    for subscription in UTM_TARIFFS_LIFESTREAM_SUBSCRIPTIONS:
        if subscription is not subscriptions:
            return subscription, UTM_TARIFFS_LIFESTREAM_SUBSCRIPTIONS[subscription]


def is_found_subscription_id(subscriptions, subscription_id):
    for subscription_item in subscriptions:
        if subscription_id == subscription_item['id']:
            return True
    return False


def test_add_remove_subscriptions_user():
    subscriptions = get_subscriptions_tv_user_lifestream(ID_TEST_USER)
    test_subscription = get_test_subscriptions(subscriptions)
    test_subscription_id_utm, test_subscription_id_lifestream = test_subscription
    assert test_subscription_id_lifestream is not None
    assert test_subscription_id_utm is not None

    result = add_subscriptions_user(ID_TEST_USER, [test_subscription_id_utm])
    assert result[0].status_code == 200

    subscriptions = get_subscriptions_tv_user_lifestream(ID_TEST_USER)
    assert is_found_subscription_id(subscriptions, test_subscription_id_lifestream)

    result = remove_subscriptions_user(ID_TEST_USER, [{'id': test_subscription_id_lifestream}])
    assert result[0].status_code == 200

    subscriptions = get_subscriptions_tv_user_lifestream(ID_TEST_USER)
    assert not is_found_subscription_id(subscriptions, test_subscription_id_lifestream)


def test_apply_change_status_lifestream():
    subscriptions = get_subscriptions_tv_user_lifestream(ID_TEST_USER)
    test_subscription = get_test_subscriptions(subscriptions)
    test_subscription_id_utm, test_subscription_id_lifestream = test_subscription

    user_utm = UserStatus(
        login='11278', full_name='User1', balance=184.62, block_type=1,
        last_block_start_date=1538342370, last_block_expire_date=datetime.datetime.now().timestamp() + 600,
        last_block_is_deleted=False, user_id=1146, lifestream_id=ID_TEST_USER,
        tariffs_id=[1311, test_subscription_id_utm], deleted_tariffs_id=[]
    )

    user_lifestream = {
        'updated': '2018-10-09 08:01:07.197000+03:00',
        'id': ID_TEST_USER, 'city': '',
        'email': 'anton@mail.ru', 'username': 'test1',
        'info': {
            'fio': 'User1', 'activation_date': '24.12.15', 'period': '',
            'address': 'г.Киров'
        },
        'subscriptions': [{'id': test_subscription_id_lifestream}],
        'is_blocked': False,
        'created': '2015-12-24 13:27:24.189000+03:00'
    }
    status_change = [{
        'user': user_utm,
        'lifestream_user': user_lifestream,
        'status_utm': True,
        'status_lifestream': False,
        'subscriptions': user_lifestream['subscriptions'],
    }]

    result = apply_change_status_lifestream(status_change)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].status_code == 200

    subscriptions = get_subscriptions_tv_user_lifestream(ID_TEST_USER)
    assert is_found_subscription_id(subscriptions, test_subscription_id_lifestream)

    status_change[0].update({
        'status_utm': False,
        'status_lifestream': True,
    })

    result = apply_change_status_lifestream(status_change)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].status_code == 200

    subscriptions = get_subscriptions_tv_user_lifestream(ID_TEST_USER)
    assert not is_found_subscription_id(subscriptions, test_subscription_id_lifestream)
