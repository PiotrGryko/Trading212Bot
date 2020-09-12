# -*- coding: utf-8 -*-

import re
import time
from selenium import webdriver

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import selenium.common.exceptions
from datetime import datetime

from selenium.webdriver.common.keys import Keys

from logger import Logger
from utils import expect, expect_none

logger = Logger()


class Api(object):

    def __init__(self):

        logger.debug(f"low level initialised  chrome")

    def launch(self, driver_path):
        try:
            logger.debug(f"launching  browser {driver_path}")
            chrome_options = Options()
            #chrome_options.add_argument("--headless")
            #chrome_options.add_argument('--no-sandbox')
            self.browser = webdriver.Chrome(executable_path=driver_path,
                                            options=chrome_options
                                            )
            logger.debug(f"browser chrome launched")
        except Exception as e:
            logger.debug(f"browser error ")
            raise e
        return True

    def search_id(self, id, dom=None):
        if dom is None:
            dom = self.browser
        return expect(dom.find_element_by_id, args=[id])

    def search_name(self, name, dom=None):
        if dom is None:
            dom = self.browser
        return expect(dom.find_element_by_name, args=[name])

    def search_tag(self, name, dom=None):
        if dom is None:
            dom = self.browser
        return expect(dom.find_element_by_tag_name, args=[name])

    def search_tag_array(self, name, dom=None):
        if dom is None:
            dom = self.browser
        return expect(dom.find_elements_by_tag_name, args=[name])

    def search_class_name(self, name, dom=None):
        if dom is None:
            dom = self.browser
        return expect(dom.find_element_by_class_name, args=[name])

    def search_class_name_array(self, name, dom=None):
        if dom is None:
            dom = self.browser
        return expect(dom.find_elements_by_class_name, args=[name])

    def search_class_name_none(self, name, dom=None):
        if dom is None:
            dom = self.browser
        return expect_none(dom.find_element_by_class_name, args=[name], times=10)

    def login(self, username, password):
        url = "https://trading212.com/it/login"
        try:
            logger.debug(f"visiting %s" % url)
            self.browser.get(url)
            logger.debug(f"connected to %s" % url)
        except selenium.common.exceptions.WebDriverException:
            logger.critical("connection timed out")
            raise
        try:
            self.search_name("login[username]").send_keys(username)
            self.search_name("login[password]").send_keys(password)
            self.search_class_name("button-login").click()
            # define a timeout for logging in

            general_error = self.search_class_name_none('general-error')
            if general_error:
                logger.info(f"Login error")
                raise Exception(username)
            else:
                logger.info(f"No error, logged in as {username}")

            time.sleep(1)

        except Exception as e:
            logger.critical("login failed")
            raise e
        return True

    def logout(self):
        """logout func (quit browser)"""
        try:
            self.browser.close()
        except Exception as e:
            raise e
            return False
        logger.info("logged out")
        return True

    def get_bottom_info(self):
        result = None
        try:
            statusbar = self.search_id("statusbar")
            soup = BeautifulSoup(statusbar.get_attribute('innerHTML'), 'html.parser')
            free_founds = soup.find(id='equity-free')
            account_value = soup.find(id='equity-total')
            live_result = soup.find(id='equity-ppl')
            blocked_founds = soup.find(id='equity-blocked')

            result = {
                'free_funds': free_founds.text,
                'account_value': account_value.text,
                'live_result': live_result.text,
                'blocked_founds': blocked_founds.text}

            print(result)
        except Exception as e:
            self.handle_exception(e)
            pass
        return result

    def get_opened_positions(self):
        try:
            table = self.search_class_name("dataTable")
            table_body = self.search_tag("tbody", dom=table)
            soup = BeautifulSoup(table_body.get_attribute('innerHTML'), 'html.parser')
            result = []

            names = soup.select("td.name")
            quantities = soup.select("td.quantity")
            average_prices = soup.select("td.averagePrice")
            ppls = soup.select("td.ppl")
            prices_buy = soup.select("td.currentPrice")
            directions = soup.select("td.direction")

            for index in range(len(names)):
                name = names[index]
                quantity = quantities[index]
                average_price = average_prices[index]
                ppl = ppls[index]
                current_price = prices_buy[index]
                current_price_text = current_price.text
                direction = directions[index]

                direction_sell = direction.select("span.direction-label-sell")
                direction_buy = direction.select("span.direction-label-buy")
                direction = "SELL" if len(direction_sell) > 0 else "BUY"

                result.append({
                    "name": name.text.replace("\n", "").replace(u'\xa0', ""),
                    "quantity": quantity.text.replace("\n", "").replace(u'\xa0', ""),
                    "direction": direction,
                    "average_price": average_price.text.replace("\n", "").replace(u'\xa0', ""),
                    "current_price": current_price_text.replace("\n", "").replace(u'\xa0', ""),
                    "profit": ppl.text.replace("\n", "").replace(u'\xa0', "")
                })

                '''
                logger.debug(f"############################################"
                             f"\nposition "
                             f"\nname {name.text}"
                             f"\nquantity {quantity.text}"
                             f"\ndirection {direction},
                             f"\naverage price {average_price.text}"
                             f"\ncurrent price {current_price_text}"
                             f"\nprofit {ppl.text}")
                '''
            return result
        except Exception as e:
            self.handle_exception(e)
            pass
        return []

    def close_all_positions(self):
        try:
            table = self.search_class_name("dataTable")
            table_body = self.search_tag("tbody", dom=table)
            rows = self.search_tag_array("tr", dom=table_body)

            logger.critical(f"closing all opened positions, count {len(rows)}")
            while len(rows) > 0:
                position = rows[0]
                self._close_position_row(position)
                time.sleep(1)
                rows = self.search_tag_array("tr", dom=table_body)
        except Exception as e:
            self.handle_exception(e)
            pass

    def close_position_by_name(self, name):
        try:
            table = self.search_class_name("dataTable")
            table_body = self.search_tag("tbody", dom=table)
            rows = self.search_tag_array("tr", dom=table_body)
            logger.critical(f"closing position {name}")
            for position in rows:
                position_name = self.search_class_name('name', dom=position).text
                if position_name == name:
                    self._close_position_row(position)
                    return True
        except Exception as e:
            self.handle_exception(e)
            return False

    def _close_position_row(self, position):
        name = self.search_class_name('name', dom=position).text
        close_button = self.search_class_name('close', dom=position)
        close_button.click()
        time.sleep(1)

        widget_message = self.search_class_name("widget_message")
        btn_primary = self.search_class_name("btn-primary", dom=widget_message)
        btn_primary.click()
        time.sleep(1)
        logger.critical(f"position closed {name}")

    def get_wishlisth(self):
        try:
            now = datetime.now()

            tradepanel = self.search_class_name("tradepanel-content")
            content = self.search_class_name("scrollable-area-content", dom=tradepanel)

            soup = BeautifulSoup(content.get_attribute('innerHTML'), 'html.parser')
            names = soup.select("div.tradebox span.instrument-name")
            sell_prices = soup.select("div.tradebox-price-sell")
            buy_prices = soup.select("div.tradebox-price-buy")
            result = []
            for index in range(0, len(names)):
                name = names[index].get_text().strip().replace("\n", "")
                sell_price = sell_prices[index].get_text().replace("\n", "").replace(u'\xa0', "")
                buy_price = buy_prices[index].get_text().replace("\n", "").replace(u'\xa0', "")
                sell_price = re.findall("\d+\.\d+", sell_price)[0]
                buy_price = re.findall("\d+\.\d+", buy_price)[0]
                # logger.debug(f"name {name} sell {sell_price} buy {buy_price}")
                result.append({
                    'name': name,
                    'sell_price': sell_price,
                    'buy_price': buy_price,
                    'time': now
                })
            return result
        except Exception as e:
            self.handle_exception(e)
            pass

    def buy(self, name, quantity):
        try:
            logger.debug(f"buy {quantity} of {name} ")
            trade_panel = self.search_class_name("tradepanel-content")
            content = self.search_class_name("scrollable-area-content", dom=trade_panel)
            instruments = self.search_class_name_array("tradebox", dom=content)
            for instrument in instruments:
                instrument_name = self.search_class_name("label-wrapper", dom=instrument).text
                if name == instrument_name:
                    input_button = self.search_class_name("quantity-list-input-wrapper", dom=instrument)
                    input_button.click()
                    time.sleep(1)
                    input = self.search_tag("input", dom=input_button)

                    ###### check if input accepts "."
                    input.send_keys(".")
                    time.sleep(1)
                    entered_value = input.get_attribute("value")
                    if "." in entered_value:
                        str_quantity = "{:.2f}".format(quantity)
                    else:
                        str_quantity = int(quantity)

                    input.send_keys(Keys.BACK_SPACE)
                    input.send_keys(str_quantity)

                    time.sleep(1)
                    button_container = self.search_class_name("tradebox-trade-container", dom=instrument)
                    buy_button = self.search_class_name("tradebox-buy", dom=button_container)
                    buy_button.click()
                    logger.debug(f"bought {str_quantity} of {name}")
                    time.sleep(1)
                    return
        except Exception as e:
            self.handle_exception(e)
            pass

    def sell(self, name, quantity):
        try:
            logger.debug(f"sell {quantity} of {name}")
            trade_panel = self.search_class_name("tradepanel-content")
            content = self.search_class_name("scrollable-area-content", dom=trade_panel)
            instruments = self.search_class_name_array("tradebox", dom=content)
            for instrument in instruments:
                instrument_name = self.search_class_name("label-wrapper", dom=instrument).text
                if name == instrument_name:
                    input_button = self.search_class_name("quantity-list-input-wrapper", dom=instrument)
                    input_button.click()
                    time.sleep(1)
                    input = self.search_tag("input", dom=input_button)

                    ###### check if input accepts "."
                    input.send_keys(".")
                    time.sleep(1)
                    entered_value = input.get_attribute("value")
                    if "." in entered_value:
                        str_quantity = "{:.2f}".format(quantity)
                    else:
                        str_quantity = int(quantity)

                    input.send_keys(Keys.BACK_SPACE)
                    input.send_keys(str_quantity)
                    time.sleep(1)
                    button_container = self.search_class_name("tradebox-trade-container", dom=instrument)
                    buy_button = self.search_class_name("tradebox-sell", dom=button_container)
                    buy_button.click()
                    logger.debug(f"sold  {name}")
                    time.sleep(1)
                    return
        except Exception as e:
            self.handle_exception(e)
            pass

    def handle_exception(self, exception):
        logger.critical("got exception")
        logger.critical(exception)
        # raise exception
        # send_email(exception)
