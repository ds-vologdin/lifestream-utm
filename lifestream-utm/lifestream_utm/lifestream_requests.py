import logging
import requests
import json
from typing import List, Dict, Any


from settings.private_settings import URL_LIFESTREAM
from settings.utm_tariffs import UTM_TARIFFS_LIFESTREAM_SUBSCRIPTIONS


logger = logging.getLogger(__name__)


def post_requests_to_lifestream(
        user_id: str,
        json_requests: List[Dict[str, Any]],
        url_lifestream: str=URL_LIFESTREAM
) -> List[requests.Response]:
    result = []  # type: List[requests.Response]
    for json_request in json_requests:
        logger.debug(json_request)
        url = '{}/v2/accounts/{}/subscriptions'.format(
            url_lifestream, user_id)
        r = requests.post(url, json=json_request)
        logger.info('{} ({}) - {}: {}'.format(
            url, json_request, r.status_code, r.text))
        result.append(r)
    return result


def remove_subscriptions_user(
        id_lifestream: str, subscriptions: List[Dict[str, Any]]) -> List[requests.Response]:
    subscriptions_json = []  # type: List[Dict[str, Any]]
    for subscription in subscriptions:
        subscription['valid'] = False
        subscriptions_json.append(subscription)
    return post_requests_to_lifestream(id_lifestream, subscriptions_json)


def add_subscriptions_user(
        id_lifestream: str, subscriptions_id: List[int]) -> List[requests.Response]:
    subscriptions_lifestream = [
        UTM_TARIFFS_LIFESTREAM_SUBSCRIPTIONS[subscription]
        for subscription in subscriptions_id
        if subscription in UTM_TARIFFS_LIFESTREAM_SUBSCRIPTIONS
    ]  # type: List[str]
    subscriptions_json = [
        {'id': subscription, 'valid': True}
        for subscription in subscriptions_lifestream
    ]  # type: List[Dict[str, Any]]
    return post_requests_to_lifestream(id_lifestream, subscriptions_json)


def get_status_tv_users_lifestream(
        url_lifestream: str=URL_LIFESTREAM) -> List[Dict[str, Any]]:
    url = '{}/v2/accounts?page_size=100&page='.format(url_lifestream)  # type: str
    accounts_json = requests.get(url + '0')
    accounts_request = json.loads(accounts_json.text)  # type: Dict[str, Any]
    accounts = accounts_request['accounts']  # type: List[Dict[str, Any]]
    for page in range(1, accounts_request['pagination']['pages']):
        accounts_json_page = requests.get(url + str(page))
        accounts += json.loads(accounts_json_page.text)['accounts']
    return accounts


def get_subscriptions_tv_user_lifestream(
        user_id: str, url_lifestream: str=URL_LIFESTREAM) -> List[Dict[str, Any]]:
    url = '{}/v2/accounts/{}/subscriptions'.format(
        url_lifestream, user_id)  # type: str
    subscriptions_json = requests.get(url)  # type: requests.Response
    return json.loads(subscriptions_json.text)


def apply_change_status_lifestream(
        status_change: List[Dict[str, Any]]) -> List[requests.Response]:
    result = []  # type: List[requests.Response]
    for user_change in status_change:
        user = user_change['user']
        if user_change['status_utm']:
            result += add_subscriptions_user(user.lifestream_id, user.tariffs_id)
        else:
            result += remove_subscriptions_user(
                user.lifestream_id, user_change['subscriptions'])
    return result
