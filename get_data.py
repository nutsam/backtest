import csv
import os
import shutil

import yaml
from binance.client import Client

from secret import API_KEY, API_SECRET
from utils import INTERVAL

with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Params
pair = config['data']['pair']
start = config['data']['start']
end = config['data']['end']
freq = config['data']['freq']

def download_data(path, pair, start, end):
    csvfile = open(path, 'w', newline='')

    candlestick_writer = csv.writer(csvfile, delimiter=',')
    candlesticks = client.get_historical_klines(pair, INTERVAL[freq], start, end)

    for candlestick in candlesticks:
        candlestick[0] = candlestick[0] / 1000 # divide timestamp to ignore miliseconds
        print(candlestick[0])
        candlestick_writer.writerow(candlestick)

    csvfile.close()

if __name__ == '__main__':
    client = Client(API_KEY, API_SECRET)
    path = f'data/{pair}_{start}_{end}_{freq}.csv'
    shutil.rmtree(os.path.dirname(path), ignore_errors=True)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    download_data(path, pair, start, end)
