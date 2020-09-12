from analysis import Analysis
from identification import identify_df_trends2, TREND_UP, TREND_DOWN
from logger import Logger
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
import seaborn as sns

TYPE_SELL = "SELL"
TYPE_BUY = "BUY"
TYPE_CLOSE_POSITION = "CLOSE_POSITION"

logger = Logger()
profit_dict = {}

trends_dict = {}

result = {}

CLOSE_STOP_LOSS = "STOP_LOSS"
CLOSE_CHANGE_TREND = "CHANGE_TREND"
CLOSE_TAKE_PROFIT = "TAKE_PROFIT"


def draw_trends(data_set, segments_count):
    indexes = []
    prices = []
    for x in data_set:
        indexes.append(x['time'])
        prices.append({"price": float(x['buy_price']),
                       "date": x['time']})
    series = pd.DataFrame.from_records(index=indexes, data=prices)
    series['Up Trend'] = np.nan
    series['Down Trend'] = np.nan
    sns.set(style='darkgrid')
    df, trend = identify_df_trends2(df=series,
                                    column='price',
                                    segments_count=segments_count)

    df.reset_index(inplace=True)
    print(df.columns)

    plt.figure(figsize=(20, 10))

    ax = sns.lineplot(x=df.index, y=df['price'])
    ax.set(xlabel='Date')

    labels = df['Up Trend'].dropna().unique().tolist()

    for label in labels:
        sns.lineplot(x=df[df['Up Trend'] == label].index,
                     y=df[df['Up Trend'] == label]['price'],
                     color='green')

        ax.axvspan(df[df['Up Trend'] == label].index[0],
                   df[df['Up Trend'] == label].index[-1],
                   alpha=0.2,
                   color='green')

    labels = df['Down Trend'].dropna().unique().tolist()

    for label in labels:
        sns.lineplot(x=df[df['Down Trend'] == label].index,
                     y=df[df['Down Trend'] == label]['price'],
                     color='red')

        ax.axvspan(df[df['Down Trend'] == label].index[0],
                   df[df['Down Trend'] == label].index[-1],
                   alpha=0.2,
                   color='red')

    locs, _ = plt.xticks()
    labels = []

    plt.xticks(locs[1:-1], labels)
    plt.show()


def get_current_trend(data_set, segments_count):
    indexes = []
    prices = []
    for x in data_set:
        indexes.append(x['time'])
        prices.append({"price": float(x['buy_price']),
                       "date": x['time']})

    series = pd.DataFrame.from_records(index=indexes, data=prices)
    series['Up Trend'] = np.nan
    series['Down Trend'] = np.nan
    df, trend = identify_df_trends2(df=series,
                                    column='price',
                                    segments_count=segments_count)
    return trend


def numpy_trend(data_set):
    index = []
    data = []
    for i, element in enumerate(data_set):
        index.append(i)
        data.append(float(element['buy_price']))

    coeffs = np.polyfit(index, list(data), 1)
    slope = coeffs[-2]

    resultent = float(slope)
    print(resultent)


def get_time_period(name, collection, hours):
    end = datetime.datetime.now()
    start = end - datetime.timedelta(hours=hours)
    data = collection.find({'name': name, 'time': {'$lt': end, '$gte': start}})
    return data


def close_position(position, reason):
    name = position['name']
    profit = position['profit']
    profit_float = float(profit)
    return {
        "type": TYPE_CLOSE_POSITION,
        "name": name,
        "quantity": 0,
        "profit": profit_float,
        "reason": reason
    }


def build_trends(name, data_set):
    current_element = data_set[-1]
    current_buy_price = float(current_element['buy_price'])
    current_element_time = current_element['time']
    trends_mins = [1, 2, 5, 10, 30, 60, 120, 240]
    trend_index = 0

    trends = {}

    general_trend_up = True
    general_trend_down = True

    for element in reversed(data_set):

        if trend_index >= len(trends_mins):
            break

        element_time = element['time']
        element_price = float(element["buy_price"])
        period = trends_mins[trend_index]
        if element_time < current_element_time - datetime.timedelta(minutes=period):
            direction = None
            trend_index = trend_index + 1
            if current_buy_price > element_price:
                direction = TREND_UP
                general_trend_down = False
            elif current_buy_price < element_price:
                direction = TREND_DOWN
                general_trend_up = False
            trends[period] = {
                "from": element_time.strftime("%H:%M:%S"),
                "to": current_element_time.strftime("%H:%M:%S"),
                "type": direction,
                "diff": "{:.2f}".format(current_buy_price - element_price),
                "period": period,
            }

    general_direction = None
    if general_trend_up:
        general_direction = TREND_UP
    elif general_trend_down:
        general_direction = TREND_DOWN
    trends['general'] = {
        "from": 0,
        "to": 0,
        "type": general_direction,
        "diff": 0,
        "period": 0
    }

    trends_dict[name] = trends


def compare_current_price(data_set):
    current_price = float(data_set[-1]['buy_price'])
    lowest = current_price
    highest = current_price
    for element in data_set:
        buy_price = float(element['buy_price'])
        if buy_price < lowest:
            lowest = buy_price
        if buy_price > highest:
            highest = buy_price

    diff = highest - lowest
    low_diff = 0
    high_diff = 0
    if current_price != lowest:
        low_diff = (current_price - lowest) / diff * 100
    if current_price != highest:
        high_diff = (highest - current_price) / diff * 100

    # print(f"c {current_price} {lowest} {highest} diff {low_diff} {high_diff}")
    if high_diff < 15:
        # print("price v high")
        return True, False
    elif low_diff < 15:
        # print("price v low")
        return False, True
    return None, None


def print_trends(name):
    if name not in trends_dict:
        return None
    messge = ""
    trends = trends_dict[name]
    for key in trends.keys():
        trend = trends[key]
        messge += f"{key}:{trend['type']} "
    return messge


def combine_trends(name, keys):
    if name not in trends_dict:
        return None
    trends = trends_dict[name]
    trend_up = True
    trend_down = True
    for key in keys:
        if key in trends:
            trend = trends[key]
            if trend['type'] == TREND_UP:
                trend_down = False
            elif trend['type'] == TREND_DOWN:
                trend_up = False

    if trend_up:
        return TREND_UP
    elif trend_down:
        return TREND_DOWN
    else:
        return None


def test_analysis3(founds, name, collection):
    data_set = list(get_time_period(name, collection, 12))

    analysis = Analysis(name, data_set)
    #trend_short = analysis.run_forecast(10, False)
    trend_middle = analysis.run_forecast(30, False)
    trend_long = analysis.run_forecast(60, False)

    current_element = data_set[-1]
    current_buy_price = float(current_element['buy_price'])
    quantity = founds / current_buy_price

    logger.analysis_result(f"{name} middle {trend_middle} long {trend_long}")

    if trend_middle == TREND_UP and trend_long == TREND_UP:
        logger.analysis_critical(f"SHOULD BUY {name}")
        return {"type": TYPE_BUY, "name": name, "quantity": quantity}
    elif  trend_middle == TREND_DOWN and trend_long == TREND_DOWN:
        logger.analysis_critical(f"SHOULD SELL {name}")
        return {"type": TYPE_SELL, "name": name, "quantity": quantity}
    return None


def test_analysis2(founds, name, collection):
    data_set = list(get_time_period(name, collection, 1))

    current_element = data_set[-1]
    current_buy_price = float(current_element['buy_price'])
    current_sell_price = float(current_element['sell_price'])
    quantity = founds / current_buy_price

    price_v_high, price_v_low = compare_current_price(data_set)

    spread = current_buy_price - current_sell_price
    if spread > 0:
        spread = spread / current_buy_price * 100

    build_trends(name, data_set)
    # trends = trends_dict[name]
    long_trend = combine_trends(name, [1, 2, 5, 10, 30])
    short_trend = combine_trends(name, [1, 2, 5])

    price_message = ""
    if price_v_high:
        price_message = "price VERY HIGH"
    if price_v_low:
        price_message = "price VERY LOW"

    logger.analysis_result(
        f"{name} "
        f"price:{current_buy_price} "
        f"spread: {'{:.2f}'.format(spread)}% "
        f"trends:{print_trends(name)} "
        f"{price_message}")

    if short_trend == TREND_UP and price_v_low:
        logger.analysis_critical(f"SHOULD BUY {name}")
        return {"type": TYPE_BUY, "name": name, "quantity": quantity}
    elif short_trend == TREND_DOWN and price_v_high:
        logger.analysis_critical(f"SHOULD SELL {name}")
        return {"type": TYPE_SELL, "name": name, "quantity": quantity}
    elif long_trend == TREND_UP and spread <= 0.5 and not price_v_high:
        logger.analysis_critical(f"SHOULD BUY {name}")
        return {"type": TYPE_BUY, "name": name, "quantity": quantity}
    elif long_trend == TREND_DOWN and spread <= 0.5 and not price_v_low:
        logger.analysis_critical(f"SHOULD SELL {name}")
        return {"type": TYPE_SELL, "name": name, "quantity": quantity}
    return None


def monitor_stop_loss(max_loss, opened_positions):
    results = []
    for position in opened_positions:
        name = position['name']
        profit = position['profit']
        profit_float = float(profit)
        direction = position['direction']
        quantity = position['quantity']
        short_trend = combine_trends(name, [1, 2, 5, 10, 30, 60, 120])

        if name not in profit_dict or profit_float > profit_dict[name]:
            profit_dict[name] = profit_float
        max_profit = profit_dict[name]

        threshold = -max_loss

        if profit_float > 0 and max_profit > max_loss / 10:
            threshold = max_loss / 10
        if profit_float > 0 and max_profit > max_loss / 5:
            threshold = max_profit - max_loss / 10

        logger.success_or_warrning(
            f"{name} quantity {quantity}"
            f" direction {direction} "
            f"current profit: {profit} "
            f"max profit {max_profit} "
            f"stop loss {threshold}",
            profit_float > 0)

        """
        Close if price is below max_loss
        """
        if profit_float < -max_loss:
            logger.analysis_critical(f"posting close event {name}, stop loss")
            del profit_dict[name]
            results.append(close_position(position, CLOSE_STOP_LOSS))

        """
        Close if price is above 0 and below treshold. 
        Wont close if all trends indicate further profit 
        """
        if 0 < profit_float < threshold:
            # if direction == "BUY" and very_short_trend == TREND_UP:
            #    logger.critical("Wont close position, direction BUY all trends UP")
            # elif direction == "SELL" and very_short_trend == TREND_DOWN:
            #    logger.critical("Wont close position, direction SELL all trends DOWN")
            # else:
            logger.analysis_critical(f"posting close event {name}")
            results.append(close_position(position, CLOSE_TAKE_PROFIT))
            if name in profit_dict:
                del profit_dict[name]

        """
        Close if profit is below 0 and all trends indicate further loss
        
        if profit_float < 0 and short_trend == TREND_UP and direction == "SELL":
            logger.analysis_critical(f"{name} posting close event, direction SELL all trends UP")
            if name in profit_dict:
                del profit_dict[name]
            results.append(close_position(position, CLOSE_CHANGE_TREND))
        elif profit_float < 0 and short_trend == TREND_DOWN and direction == "BUY":
            logger.analysis_critical(f"{name} posting close event, direction BUY all trends DOWN ")
            if name in profit_dict:
                del profit_dict[name]
            results.append(close_position(position, CLOSE_CHANGE_TREND))
        """
    return results


"""
def test_analysis(founds, name, collection):
    short_set = get_time_period(name, collection, 2)
    medium_set = get_time_period(name, collection, 6)
    long_set = get_time_period(name, collection, 12)

    if medium_set.count() == short_set.count():
        logger.analysis_result(f"{name} missing records, probably new instrument")
        return

    short_trend = get_current_trend(short_set, 40)
    medium_trend = get_current_trend(medium_set, 40)
    long_trend = get_current_trend(long_set, 40)

    if not short_trend or not medium_trend or not long_trend:
        logger.analysis_result(f"{name} missing trends, probably marked closed")
        return

    current_price = short_trend['price']
    quantity = founds / current_price

    logger.analysis_result(
        f"{name} s:{print_trend(short_trend)} m:{print_trend(medium_trend)} l:{print_trend(long_trend)}")

    if is_up_trend(short_trend) and is_up_trend(medium_trend) and is_up_trend(long_trend):
        trends_dict[name] = TREND_UP
        logger.analysis_critical(f"SHOULD BUY {name}")
        return {"type": TYPE_BUY, "name": name, "quantity": quantity}
    elif is_down_trend(short_trend) and is_down_trend(medium_trend) and is_down_trend(long_trend):
        trends_dict[name] = TREND_DOWN
        logger.analysis_critical(f"SHOULD SELL {name}")
        return {"type": TYPE_SELL, "name": name, "quantity": quantity}
    return None
"""
