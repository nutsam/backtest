from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime
import backtrader as bt

from strategies import EmptyStrategy, SMAStrategy, RSIStrategy

def timeFrame(datapath):
    """
    Select the write compression and timeframe.
    """
    sepdatapath = datapath.split(sep='_') # ignore name file 'data/' and '.csv'
    tf = sepdatapath[-1].split(sep='.')[0]

    if tf == '1mth':
        compression = 1
        timeframe = bt.TimeFrame.Months
    elif tf == '12h':
        compression = 720
        timeframe = bt.TimeFrame.Minutes
    elif tf == '15m':
        compression = 15
        timeframe = bt.TimeFrame.Minutes
    elif tf == '30m':
        compression = 30
        timeframe = bt.TimeFrame.Minutes
    elif tf == '1d':
        compression = 1
        timeframe = bt.TimeFrame.Days
    elif tf == '1h':
        compression = 60
        timeframe = bt.TimeFrame.Minutes
    elif tf == '3m':
        compression = 3
        timeframe = bt.TimeFrame.Minutes
    elif tf == '2h':
        compression = 120
        timeframe = bt.TimeFrame.Minutes
    elif tf == '3d':
        compression = 3
        timeframe = bt.TimeFrame.Days
    elif tf == '1w':
        compression = 1
        timeframe = bt.TimeFrame.Weeks
    elif tf == '4h':
        compression = 240
        timeframe = bt.TimeFrame.Minutes
    elif tf == '5m':
        compression = 5
        timeframe = bt.TimeFrame.Minutes
    elif tf == '6h':
        compression = 360
        timeframe = bt.TimeFrame.Minutes
    elif tf == '8h':
        compression = 480
        timeframe = bt.TimeFrame.Minutes
    else:
        print('dataframe not recognized')
        exit()
    
    return compression, timeframe


def getWinLoss(analyzer):
    return analyzer.won.total, analyzer.lost.total, analyzer.pnl.net.total


def getSQN(analyzer):
    return round(analyzer.sqn,2)


def runbacktest(datapath, start, end, period, strategy, commission_val=None, portofolio=10000.0, percents=5, quantity=0.01, plt=False):
    """_summary_

    Args:
        datapath (str): input .csv path
        start (str): start datetime, ex: '2022-01-01'
        end (str): end datatime, ex: '2022-08-01'
        period (list): list of indicator period to test
        strategy (str): strtegy name
        commission_val (float, optional): persontage of commission. Defaults to None.
        portofolio (float, optional): start cash. Defaults to 10000.0.
        percents (float, optional): persontage to account balance per transaction. Defaults to 5.
        quantity (float, optional): Defaults to 0.01.
        plt (bool, optional): Defaults to False.

    Returns:
        _type_: _description_
    """
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a FixedSize sizer according to the stake
    # cerebro.addsizer(bt.sizers.PercentSizer, percents=percents)

    cerebro.broker.setcash(portofolio)

    if commission_val:
        cerebro.broker.setcommission(commission=commission_val/100) # divide by 100 to remove the %

    cerebro.addstrategy(strategy, maperiod=period, quantity=quantity)
    
    compression, timeframe = timeFrame(datapath)

    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
        dataname = datapath,
        dtformat = 2, 
        compression = compression, 
        timeframe = timeframe,
        fromdate = datetime.datetime.strptime(start, '%Y-%m-%d'),
        todate = datetime.datetime.strptime(end, '%Y-%m-%d'),
        reverse = False)


    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    strat = cerebro.run()
    stratexe = strat[0]

    try:
        totalwin, totalloss, pnl_net = getWinLoss(stratexe.analyzers.ta.get_analysis())
    except KeyError:
        totalwin, totalloss, pnl_net = 0, 0, 0

    sqn = getSQN(stratexe.analyzers.sqn.get_analysis())

    if plt:
        cerebro.plot(style='candle', barup='green', bardown='red')


    return cerebro.broker.getvalue(), totalwin, totalloss, pnl_net, sqn