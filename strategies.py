import backtrader as bt
import backtrader.indicators as bti
import numpy as np

class EmptyStrategy(bt.Strategy):
    params = (
        ('maperiod', None),
        ('quantity', None)
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.length = 10

        self.sma_30 = bti.SimpleMovingAverage(self.data.close, period=30)
        self.sma_45 = bti.SimpleMovingAverage(self.data.close, period=45)
        self.sma_60 = bti.SimpleMovingAverage(self.data.close, period=60)

    
    def log(self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        print("%s %s" % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

        if order.isbuy():
            self.log("買入 價格: %.2f 成本: %.2f 手續費: %.2f" % (order.executed.price, order.executed.value, order.executed.comm))
        elif order.issell():
            self.log("賣出 價格: %.2f 成本: %.2f 手續費: %.2f" % (order.executed.price, order.executed.value, order.executed.comm))

        self.order = None

    def next(self):
        if self.order:
            return 
        
        if not self.position:
            if len(self.sma_60) >= 60:
                diff30_45 = [self.sma_30[-i]-self.sma_45[-i] for i in range(1, self.length)]
                diff45_60 = [self.sma_45[-i]-self.sma_60[-i] for i in range(1, self.length)]
                if all (x > 0 for x in diff30_45) and all (x > 0 for x in diff45_60):
                    self.buy_sig = True
                    self.amount = (self.broker.getvalue() * self.params.quantity) / self.dataclose[0]
                    self.order = self.buy(size=self.amount)
        else:
            # Already in the market ... we might sell
            if self.sma_30[0] < self.sma_45[0]:

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell(size=self.amount)

class SMAStrategy(bt.Strategy):

    params = (
        ('maperiod', None),
        ('quantity', None)
    )

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.amount = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)

    def log(self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        print("%s %s" % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

        # if order.isbuy():
        #     self.log("買入 價格: %.2f 成本: %.2f 手續費: %.2f" % (order.executed.price, order.executed.value, order.executed.comm))
        # elif order.issell():
        #     self.log("賣出 價格: %.2f 成本: %.2f 手續費: %.2f" % (order.executed.price, order.executed.value, order.executed.comm))


        self.order = None


    def next(self):

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.sma[0]:
                # Keep track of the created order to avoid a 2nd order
                self.amount = (self.broker.getvalue() * self.params.quantity) / self.dataclose[0]
                self.order = self.buy(size=self.amount)
        else:
            # Already in the market ... we might sell
            if self.dataclose[0] < self.sma[0]:

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell(size=self.amount)


class RSIStrategy(bt.Strategy):

    params = (
        ('maperiod', None),
        ('quantity', None)
    )

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.amount = None

        # Add a MovingAverageSimple indicator
        self.rsi = bt.talib.RSI(self.datas[0], timeperiod=self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

        self.order = None

    def next(self):

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.rsi < 30:

                # Keep track of the created order to avoid a 2nd order
                self.amount = (self.broker.getvalue() * self.params.quantity) / self.dataclose[0]
                self.order = self.buy(size=self.amount)
        else:
            # Already in the market ... we might sell
            if self.rsi > 70:

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell(size=self.amount)
                