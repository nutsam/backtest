import csv
import os

import yaml

import backtest
from strategies import *

with open('config.yaml') as f:
    config = yaml.safe_load(f)

commission = config['setting']['commission']  # 0.04% taker fees binance usdt futures
portofolio = config['setting']['portofolio']  # amount of money we start with
persontage = 20 # 5% to total protofolio per transaction
quantity = config['setting']['quantity']  # percentage to buy based on the current portofolio amount

start = config['data']['start']
end = config['data']['end']
strategies = config['strategy']['name']
periodRange = config['strategy']['maperiod']
plot = config['plot']

os.makedirs('result', exist_ok=True)

for strategy in strategies:
    for data in os.listdir("data"):
        datapath = os.path.join('data', data)
        # ignore name file 'data/' and '.csv'
        sep = datapath[5:-4].split(sep='-')

        print('\n ------------ ', datapath)
        print()

        dataname = 'result/{}-{}-{}-{}-{}.csv'.format(
            strategy, sep[0], start.replace('-', ''), end.replace('-', ''), sep[3])
        csvfile = open(dataname, 'w', newline='')
        result_writer = csv.writer(csvfile, delimiter=',')

        result_writer.writerow(['Pair', 'Timeframe', 'Start', 'End', 'Strategy', 'Period',
                               'Final value', '%', 'Total win', 'Total loss', 'SQN'])  # init header

        for period in periodRange:

            end_val, totalwin, totalloss, pnl_net, sqn = backtest.runbacktest(
                datapath, start, end, period, eval(strategy), commission, portofolio, persontage, quantity, plot)
            profit = (pnl_net / portofolio) * 100

            # view the data in the console while processing
            print('data processed: %s, %s (Period %d) --- Ending Value: %.2f --- Total win/loss %d/%d, SQN %.2f' %
                  (datapath[5:], strategy, period, end_val, totalwin, totalloss, sqn))

            result_writer.writerow([sep[0], sep[3], start, end, strategy, period,
                                    round(end_val, 3), round(profit, 3), totalwin, totalloss, sqn])

        csvfile.close()
