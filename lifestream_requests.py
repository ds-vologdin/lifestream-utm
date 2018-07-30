import logging
import requests
import json


from private_settings import URL_LIFESTREAM, URL_LIFESTREAM_TEST
from utm_tariffs import utm_tariffs_lifestream_subscriptions


def post_requests_to_lifestream(user_id, json_requests):
    # тестовая учётка
    user_id = '5b585202861ff302647e5e52'
    for json_request in json_requests:
        # Посылаем на тестовый урл. Пока этап отладки...
        url = '{}/v2/accounts/{}/subscriptions'.format(
            URL_LIFESTREAM_TEST, user_id
        )
        r = requests.post(url, data=json_request)
        logging.info('{} ({}) - {}: {}'.format(
            url, json_request, r.status_code, r.text
        ))


def remove_subscriptions_user(id_lifestream, subscriptions):
    subscriptions_json = [
        json.dumps({'id': '{}'.format(subscription), 'valid': False})
        for subscription in subscriptions
    ]
    post_requests_to_lifestream(id_lifestream, subscriptions_json)


def add_subscriptions_user(id_lifestream, subscriptions_id):
    subscriptions_json = []
    subscriptions_lifestream = [
        utm_tariffs_lifestream_subscriptions[subscription]
        for subscription in subscriptions_id
        if subscription in utm_tariffs_lifestream_subscriptions
    ]
    subscriptions_json = [
        json.dumps({'id': '{}'.format(subscription), 'valid': True})
        for subscription in subscriptions_lifestream
    ]
    post_requests_to_lifestream(id_lifestream, subscriptions_json)


def get_status_tv_users_lifestream():
    accounts_json = requests.get('{}/v2/accounts?page_size=100&page=0'.format(
        URL_LIFESTREAM
    ))
    accounts_request = json.loads(accounts_json.text)
    accounts = accounts_request['accounts']
    for i in range(1, accounts_request['pagination']['pages']):
        accounts_json_page = requests.get(
            '{}/v2/accounts?page_size=100&page={}'.format(
                URL_LIFESTREAM, i
            )
        )
        accounts += json.loads(accounts_json_page.text)['accounts']
    return accounts


def apply_change_status_lifestream(status_change):
    for user_change in status_change:
        user = user_change['user']
        # remove_subscriptions_user(user.lifestream_id, (101, 102, 103))
        # continue
        if user_change['status_utm']:
            add_subscriptions_user(user.lifestream_id, user.tarifs_id)
        else:
            remove_subscriptions_user(user.lifestream_id,
                                      user_change['subscriptions'])
