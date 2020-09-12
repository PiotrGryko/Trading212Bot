from pymongo import MongoClient

from analysis import Analysis
from market_analysis import draw_trends, compare_current_price
import datetime

if __name__ == "__main__":
    client = MongoClient()
    db = client.test_database
    collection = db.test_collection

    name ="Gold"
    '''
    end = datetime.datetime.now()
    start = end - datetime.timedelta(hours=2)
    data = collection.find({'name': name, 'time': {'$lt': end, '$gte': start}})
    print(data.count())
    draw_trends(data,40)

    end = datetime.datetime.now()
    start = end - datetime.timedelta(hours=6)
    data = collection.find({'name': name, 'time': {'$lt': end, '$gte': start}})
    print(data.count())
    draw_trends(data,40)

  '''
    end = datetime.datetime.now()-datetime.timedelta(hours=40)
    start = end - datetime.timedelta(hours=12)
    data = collection.find({'name': name, 'time': {'$lt': end, '$gte': start}})
    print(data.count())
    #draw_trends(data,40)

    #data = collection.find({'name': name})
    #print(data.count())
    #draw_trends(data,80)
    #compare_current_price(list(data))

    analysis = Analysis(name,list(data))
    analysis.load_data()
    #analysis.draw_naive()
    #analysis.draw_simple_average()
    #analysis.draw_moving_average()
    #analysis.draw_simple_exponential_smoothing()
    #analysis.draw_holt_linear_trend_method()
    #analysis.draw_holt_winters_method()
    #analysis.draw_arima()
    analysis.run_forecast(10,True)
    analysis.run_forecast(30,True)
    analysis.run_forecast(60,True)
