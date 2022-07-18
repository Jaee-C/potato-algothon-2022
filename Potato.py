import pandas as pd
import numpy as np

NUM_STOCKS = 100
STOP_LOSS_PERCENT = 10
COMM_RATE = 0.0025

# initialise the stop loss book
global stop_loss_book
stop_loss_book = [0 for i in range(NUM_STOCKS)]

curr_pos = np.zeros(100)

def getMyPosition(stock_prices):
    """
    Takes as input a NumPy array of the shape nInst x nt. nInst = 100 is the
    number of instruments. nt is the number of days for which the prices have 
    been provided. Returns a vector of desired positions.
    """
    global curr_pos

    stock_prices_df = pd.DataFrame(stock_prices).T
    curr_day = len(stock_prices[0]) - 1
    
    global ema_stocks
    ema_stocks = [x for x in range(100)] #start off trading with EMA on all stocks

    BUY_AMOUNT = 5
    SELL_AMOUNT = -5
    # curr_pos = getEMAPosition(stock_prices_df[ema_stocks], curr_day, curr_pos, BUY_AMOUNT, SELL_AMOUNT)

    curr_day = stock_prices_df.shape[0]-1

    # Calculate the ema for 10days, 30days and 60days
    ema10 = stock_prices_df.ewm(span=10, adjust=False).mean()
    ema30 = stock_prices_df.ewm(span=30, adjust=False).mean()
    ema60 = stock_prices_df.ewm(span=60, adjust=False).mean()

    # Use the above to calculate buy and sell signals
    # buy when shorter term EMAs are larger then longer term EMAs
    buy_signals = ema10.gt(ema30) & (stock_prices_df.gt(ema60) & ema10.gt(ema60) & ema30.gt(ema60))
    buy_signals = buy_signals.replace({True: BUY_AMOUNT, False: 0})

    # sell when shorter term EMAs are smaller than longer term EMAs
    sell_signals = ema10.lt(ema30) | ema30.lt(ema60)
    sell_signals = sell_signals.replace({True: SELL_AMOUNT, False: 0})
    trading_positions_final = buy_signals.loc[curr_day] + sell_signals.loc[curr_day]

    prev_day = curr_day-1 if curr_day>0 else 0
    new_buys = buy_signals.loc[curr_day] - buy_signals.loc[prev_day]
    new_buys[new_buys < 0] = 0
    new_buys[new_buys > 0] = 1
    new_prices = new_buys * stock_prices_df.loc[curr_day]

    for i in new_prices.loc[new_prices > 0].index:
        stop_loss_book[i] = (new_prices[i]) * (100 - STOP_LOSS_PERCENT)

    # Add stop-losses to sell
    for i in stock_prices_df.columns:
        if curr_pos[i] and stock_prices_df.loc[curr_day, i] <= stop_loss_book[i]:
            trading_positions_final[i] = 0
    
    new_positions = trading_positions_final.mask(trading_positions_final == 0, curr_pos)
    new_positions = new_positions.replace({np.nan: 0})

    # Update current position
    for i in new_positions.index:
        curr_pos[i] = new_positions[i]

    return curr_pos
