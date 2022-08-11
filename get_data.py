import csv
from config import API_KEY, API_SECRET
from binance.client import Client


client = Client(API_KEY, API_SECRET)


csvfile = open('data/UNFIUSDT-2022-2022-1h.csv', 'w', newline='')
candlestick_writer = csv.writer(csvfile, delimiter=',')


candlesticks = client.get_historical_klines("UNFIUSDT", Client.KLINE_INTERVAL_1HOUR, "1 May, 2022", "11 Jun, 2022")

for candlestick in candlesticks:
    candlestick[0] = candlestick[0] / 1000 # divide timestamp to ignore miliseconds
    print(candlestick[0])
    candlestick_writer.writerow(candlestick)


csvfile.close()