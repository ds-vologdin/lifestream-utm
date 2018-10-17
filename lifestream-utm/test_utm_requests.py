import pytest
import psycopg2

from private_settings import DATEBASE
from utm_requests import fetch_parameter_id_lifestream_from_utm
from utm_requests import get_status_tv_users_utm
from utm_requests import UserStatus


@pytest.fixture(scope='module')
def cursor_psycopg2():
    con = psycopg2.connect(**DATEBASE)
    cur = con.cursor()
    yield cur
    cur.close()
    con.close()


def test_connect_to_utm(cursor_psycopg2):
    sql = 'SELECT 1;'
    cursor_psycopg2.execute(sql)
    result = cursor_psycopg2.fetchone()
    assert result == (1,)


def test_fetch_parameter_id_lifestream_from_utm(cursor_psycopg2):
    result = fetch_parameter_id_lifestream_from_utm(cursor_psycopg2, 13)
    assert result is None
    id_lifestream, id_utm = fetch_parameter_id_lifestream_from_utm(
        cursor_psycopg2, 1146)
    assert id_lifestream == '59e76927eea9ae0ce20c28fe'
    assert id_utm == 24659


def test_get_status_tv_users_utm():
    users = get_status_tv_users_utm()
    assert isinstance(users, list)
    assert len(users) > 0
    assert isinstance(users[0], UserStatus)
