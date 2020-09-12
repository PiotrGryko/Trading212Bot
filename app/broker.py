import time
import asyncio
from logger import Logger
import threading
import queue
import market_analysis

logger = Logger()


class Broker(object):

    def __init__(self, collection):
        self.collection = collection
        self.queue = queue.Queue()
        self.running = True
        self.profit_dict = {}
        self.founds = 1500
        self.max_loss = 100
        self.wishlist = []

    def monitor_stop_loss(self, opened_positions):
        logger.open_segment(f"MONITOR STOP LOSS, positions count: {len(opened_positions)}")
        events = market_analysis.monitor_stop_loss(self.max_loss, opened_positions)
        for event in events:
            self.queue.put(event)
        logger.close_segment()

    async def main(self):
        self.running = True
        while self.running:
            names = [x['name'] for x in self.wishlist]
            for name in names:
                result = market_analysis.test_analysis3(self.founds, name, self.collection)
                if result:
                    self.queue.put(result)
            time.sleep(15)


    def close(self):
        self.running = False

    def run(self):
        logger.debug("broker run")
        loop = asyncio.get_event_loop()
        thread = threading.Thread(target=loop.run_until_complete, args=(self.main(),))
        thread.start()
