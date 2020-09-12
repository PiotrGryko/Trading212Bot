import unittest

from tests import run_tests


class TestAlwaysTrue(unittest.TestCase):

    def test_user_login(self):
        run_tests.test_launch()
        run_tests.test_login()
        #run_tests.test_bottom_info()
        #run_tests.test_get_opened_positions()
        run_tests.test_close_all()
        #run_tests.test_monitor_wishlist()
        #run_tests.test_buy()
        #run_tests.test_sell()

        #run_tests.test_close_position()
        # run_tests.test_addPrefs()
        # run_tests.test_clearPrefs()
        run_tests.test_logout()
