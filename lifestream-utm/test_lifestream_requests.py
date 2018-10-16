from lifestream_requests import get_status_tv_users_lifestream


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

