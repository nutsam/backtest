import backtrader as bt



if __name__ == '__main__':
    cerebro = bt.Cerebro()
    print("Start Protfolio {}".format(cerebro.broker.getvalue()))
    cerebro.run()
    print("Final portfolio {}".format(cerebro.broker.getvalue()))