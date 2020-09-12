import smtplib
from api import Api
import sendgrid
import time
from sendgrid.helpers.mail import *
import sys
from logger import Logger
from pymongo import MongoClient
from broker import Broker
from market_analysis import TYPE_BUY, TYPE_SELL, TYPE_CLOSE_POSITION, CLOSE_CHANGE_TREND, CLOSE_TAKE_PROFIT, \
    CLOSE_STOP_LOSS

api = Api()
logger = Logger()
client = MongoClient()
db = client.test_database
collection = db.test_collection
broker = Broker(collection)


summary = {
    'result': 0,
    'actions_count': 0,
    "stop_loss_count": 0,
    "take_profit_count": 0,
    "change_trend_count": 0
}


def send_email(exception):
    sg = sendgrid.SendGridAPIClient(api_key='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')
    from_email = Email("piogryko@gmail.com")
    to_email = To("piogryko@gmail.com")
    subject = "New trading error!"
    content = Content("text/plain", f"trading error {exception}")
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)


def buy(name, quantity):
    opened_positions = api.get_opened_positions()
    for position in opened_positions:
        if position['name'] == name:
            logger.debug(f"cannot buy {name}, position already opened")
            return

    api.buy(name, quantity)


def sell(name, quantity):
    opened_positions = api.get_opened_positions()
    for position in opened_positions:
        if position['name'] == name:
            logger.debug(f"cannot sell {name}, position already opened")
            return

    api.sell(name, quantity)


def collect_data():
    wishlist = api.get_wishlisth()
    broker.wishlist=wishlist
    collection.insert_many(wishlist)
    logger.info(f'data inserted, total count: {collection.estimated_document_count()}')


def monitor_stop_loss():
    opened_positions = api.get_opened_positions()
    broker.monitor_stop_loss(opened_positions)


def process_queue(event):
    action_type = event['type']
    instrument_name = event['name']
    quantity = event['quantity']
    if action_type == TYPE_BUY:
        buy(instrument_name, quantity)
    elif action_type == TYPE_SELL:
        sell(instrument_name, quantity)
    elif action_type == TYPE_CLOSE_POSITION:
        result = api.close_position_by_name(instrument_name)
        if result:
            profit = event['profit']
            reason = event['reason']
            summary['result'] += profit
            summary['actions_count'] += 1
            if reason == CLOSE_CHANGE_TREND:
                summary['change_trend_count'] += 1
            if reason == CLOSE_STOP_LOSS:
                summary['stop_loss_count'] += 1
            if reason == CLOSE_TAKE_PROFIT:
                summary['take_profit_count'] += 1


def start_trading(driver_path):
    # collection.drop()
    api.launch(driver_path)
    api.login("piogryko+tradiing@gmail.com", "glodnyiseta")
    start = time.time()
    duration = 60 * 60 * 16

    monitor_loss_latency = 10
    collect_data_latency = 20

    monitor_loss_last_update = 0
    collect_data_last_update = 0

    # api.close_all_positions()
    clock = time.time()
    while clock < start + duration:
        if monitor_loss_last_update+monitor_loss_latency<clock:
            monitor_stop_loss()
            logger.critical(summary)
            logger.open_segment(f"PROCESS QUEUE size:{broker.queue.qsize()}")
            while not broker.queue.empty():
                process_queue(broker.queue.get())
            logger.close_segment()
            monitor_loss_last_update=clock
        if collect_data_last_update+collect_data_latency<clock:
            collect_data()
            collect_data_last_update=clock


        #collect_data()
        # api.get_bottom_info()
        time.sleep(1)
        clock = time.time()
    logger.debug("FINISHED")

def main(driver):
    try:

        broker.run()
        start_trading(driver)
        broker.close()
        api.logout()
    except Exception as e:
        print(e)
        # send_email(e)
        api.logout()
        broker.close()
        raise e
        # main(driver_path)


if __name__ == "__main__":
    # '/Users/piotrgryko/develop/chromedriver'
    print(sys.argv)
    driver_path = sys.argv[1]
    main(driver_path)
