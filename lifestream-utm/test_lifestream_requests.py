from lifestream_requests import get_status_tv_users_lifestream
from lifestream_requests import get_subscriptions_tv_user_lifestream
from lifestream_requests import add_subscriptions_user
from lifestream_requests import remove_subscriptions_user

from utm_tariffs import UTM_TARIFFS_LIFESTREAM_SUBSCRIPTIONS

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

