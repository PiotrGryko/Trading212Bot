import os

from api import Api

brow = os.getenv('DRIVER')
api = Api()


def test_launch():
    api.launch('/Users/piotrgryko/develop/chromedriver')


def test_login():
    assert api.login("piogryko+tradiing@gmail.com", "glodnyiseta")


def test_bottom_info():
    assert api.get_bottom_info()


def test_monitor_wishlist():
    api.monitor_wishlist()


def test_sell():
    api.sell("GOLD")


def test_buy():
    api.buy("GOLD")


def test_get_opened_positions():
    api.get_opened_positions()


def test_close_position():
    api.close_position(0)


def test_close_all():
    api.close_all_positions()


def test_addPrefs():
    assert api.addPrefs(["bitcoin", "ethereum"])


def test_logout():
    assert api.logout()
