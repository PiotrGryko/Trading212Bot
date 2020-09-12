import statsmodels.api as sm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from math import sqrt
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
from scipy import stats
import datetime

'''
class Trend(object):
    TREND_UP = "UP"
    TREND_DOWN = "DOWN"

    def __init__(self, element_from, element_to):

        self.time_from = element_from['time']
        self.price_from = float(element_from["buy_price"])
        self.price_to = float(element_to['buy_price'])
        self.time_tp = element_to['time']
        self.direction = None

        if self.price_from < self.price_to:
            self.direction = self.TREND_UP
        elif self.price_from > self.price_to:
            self.direction = self.TREND_DOWN

    def is_up(self):
        return self.direction == self.TREND_UP

    def is_down(self):
        return self.direction == self.TREND_DOWN


class MovingWindow(object):
    def __init__(self):
        self.trends = {}
        self.trends_intervals = [1, 2, 5, 10, 30, 60, 120, 240]

    def build_trends(self, data_set):
        current_element = data_set[-1]
        trend_index = 0
        self.trends = {}
        for element in reversed(data_set):
            if trend_index >= len(self.trends_intervals):
                break
            period = self.trends_intervals[trend_index]
            self.trends[period] = Trend(element, current_element)

    def general_trend(self, intervals=None):
        if not intervals:
            intervals = self.trends_intervals
        trend_up = True
        trend_down = True
        for key in intervals:
            trend = self.trends[key]
            if trend.is_up():
                trend_down = False
            elif trend.is_down():
                trend_up = False

        if trend_up:
            return Trend.TREND_UP
        elif trend_down:
            return Trend.TREND_DOWN
        else:
            return None
'''


class Analysis(object):
    TREND_UP = "UP"
    TREND_DOWN = "DOWN"

    def __init__(self, name, data):
        self.data = data
        self.data_set = []
        self.name = name
        self.FORECAST_PERIOD = 10

    def load_data(self):
        self.data_set = pd.DataFrame.from_records(self.data, index='time', columns=['buy_price', 'time'],
                                                  coerce_float=True)
        self.data_set['buy_price'] = pd.to_numeric(self.data_set['buy_price'])
        self.data_set = self.data_set.resample('min').mean()
        self.data_set.dropna()

    def to_ordinal(self, dt):
        return datetime.datetime.timestamp(dt)

    def get_slope(self, data_frame):

        index = []
        data = []
        for i, element in enumerate(data_frame.values):
            index.append(i)
            data.append(float(element))

        # coeffs = np.polyfit(index, list(data), 1)
        # slope = coeffs[-2]
        slope = (data[-1] - data[0]) / (index[-1] - index[0])
        angle = np.rad2deg(np.arctan2(data[-1] - data[0], index[-1] - index[0]))

        resultent = float(slope)
        return angle

    def get_empty_series(self, minutes):
        index = []
        values = []
        now = self.data_set.index[-1]
        for minute in range(minutes):
            index.append(now + datetime.timedelta(minutes=minute))
            values.append(0)
        return pd.DataFrame.from_records({"time": index, "buy_price": values}, index='time',
                                         columns=['buy_price', 'time'], coerce_float=True)

    def naive_forecast(self, minutes, draw=False):
        dd = np.asarray(self.data_set.buy_price)
        y_hat = self.get_empty_series(minutes)
        y_hat['naive'] = dd[len(dd) - 1]
        if draw:
            self.draw_forecast(y_hat, 'naive', f'naive forecast for {minutes}min')
        return y_hat

    def simple_average_forecast(self, minutes, draw=False):
        y_hat_avg = self.get_empty_series(minutes)
        y_hat_avg['avg_forecast'] = self.data_set['buy_price'].mean()
        if draw:
            self.draw_forecast(y_hat_avg, 'avg_forecast', f'avg_forecast forecast for {minutes}min')
        return y_hat_avg

    def moving_average_forecast(self, minutes, draw=False):
        y_hat_avg = self.get_empty_series(minutes)
        y_hat_avg['moving_avg_forecast'] = self.data_set['buy_price'].rolling(5).mean().iloc[-1]
        if draw:
            self.draw_forecast(y_hat_avg, 'moving_avg_forecast', f'moving_avg_forecast forecast for {minutes}min')
        return y_hat_avg

    def simple_exponential_smoothing_forecast(self, minutes, draw):
        y_hat_avg = self.get_empty_series(minutes)
        fit2 = SimpleExpSmoothing(np.asarray(self.data_set['buy_price'])).fit(smoothing_level=0.6, optimized=False)
        y_hat_avg['SES'] = fit2.forecast(len(y_hat_avg))
        if draw:
            self.draw_forecast(y_hat_avg, 'SES', f'SES forecast for {minutes}min')
        return y_hat_avg

    def holt_linear_trend_method_forecast(self, minutes, draw=False):
        y_hat_avg = self.get_empty_series(minutes)
        fit1 = Holt(np.asarray(self.data_set['buy_price'])).fit(smoothing_level=0.3, smoothing_slope=0.1)
        y_hat_avg['Holt_linear'] = fit1.forecast(len(y_hat_avg))
        if draw:
            self.draw_forecast(y_hat_avg, 'Holt_linear', f'Holt_linear forecast for {minutes}min')
        return y_hat_avg

    def holt_winters_method_forecast(self, minutes, draw=False):
        y_hat_avg = self.get_empty_series(minutes)
        fit1 = ExponentialSmoothing(np.asarray(self.data_set['buy_price']), seasonal_periods=7, trend='add',
                                    seasonal='add', ).fit()
        y_hat_avg['Holt_Winter'] = fit1.forecast(len(y_hat_avg))

        if draw:
            self.draw_forecast(y_hat_avg, 'Holt_Winter', f'Holt_Winter forecast for {minutes}min')

        return y_hat_avg

    def arima_forecast(self, minutes, draw=False):
        y_hat_avg = self.get_empty_series(minutes)
        fit1 = sm.tsa.statespace.SARIMAX(self.data_set['buy_price'],
                                         order=(2, 1, 4),
                                         seasonal_order=(0, 1, 1, 7)).fit(disp=0)
        y_hat_avg['SARIMA'] = fit1.predict(start=0, end=len(self.data_set) + len(y_hat_avg), dynamic=False)

        if draw:
            self.draw_forecast(y_hat_avg, 'SARIMA', f'SARIMA forecast for {minutes}min')

        return y_hat_avg

    def draw_forecast(self, forecast_result, key, title):
        plt.figure(figsize=(16, 8))
        plt.plot(self.data_set['buy_price'], label='Train')
        plt.plot(forecast_result[key], label=key)
        plt.legend(loc='best')
        plt.title(title)
        plt.show()
        # rms = sqrt(mean_squared_error(self.test_set.buy_price, y_hat_avg.SARIMA))
        # print(f"RMSE = {rms}")

    def run_forecast(self, minutes, draw=False):
        self.FORECAST_PERIOD = minutes
        self.load_data()

        winters = self.holt_winters_method_forecast(minutes, draw)
        winters_slope_angle = self.get_slope(winters.Holt_Winter)

        arima = self.arima_forecast(minutes, draw)
        arima_slope_angle = self.get_slope(arima.SARIMA)
        #print(f"{self.name} Holts winters slope angle: {winters_slope_angle} Sarima slope angle: {arima_slope_angle}")

        if winters_slope_angle > 5 and arima_slope_angle > 5:
            return Analysis.TREND_UP
        elif winters_slope_angle < -5 and arima_slope_angle < -5:
            return Analysis.TREND_DOWN
