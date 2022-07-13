import pandas as pd
import numpy as np

NUM_STOCKS = 100

STOP_LOSS_PERCENT = 10

global stop_loss_book
stop_loss_book = [0 for i in range(NUM_STOCKS)]

def getEMAPosition(stock_prices_df, curr_day, curr_pos, BUY_AMOUNT, SELL_AMOUNT):

    curr_day = stock_prices_df.shape[0]-1

    ema10 = stock_prices_df.ewm(span=10, adjust=False).mean()
    ema30 = stock_prices_df.ewm(span=30, adjust=False).mean()
    ema60 = stock_prices_df.ewm(span=60, adjust=False).mean()

    # Calculate buy and sell signals
    buy_signals = ema10.gt(ema30) & (stock_prices_df.gt(ema60) & ema10.gt(ema60) & ema30.gt(ema60))
    buy_signals = buy_signals.replace({True: BUY_AMOUNT, False: 0})
    sell_signals = ema10.lt(ema30)
    sell_signals = sell_signals.replace({True: SELL_AMOUNT, False: 0})
    trading_positions_final = buy_signals.loc[curr_day] + sell_signals.loc[curr_day]

    # Add new buys to stop-loss book
    prev_day = curr_day-1 if curr_day>0 else 0
    new_buys = buy_signals.loc[curr_day] - buy_signals.loc[prev_day]
    new_buys[new_buys < 0] = 0
    new_buys[new_buys > 0] = 1
    new_prices = new_buys * stock_prices_df.loc[curr_day]

    for i in new_prices.loc[new_prices > 0].index:
        stop_loss_book[i] = new_prices[i] * (100 - STOP_LOSS_PERCENT)

    # Add stop-losses to sells
    for i in stock_prices_df.columns:
        if curr_pos[i] and stock_prices_df.loc[curr_day, i] <= stop_loss_book[i]:
            trading_positions_final[i] = 0
    
    new_positions = trading_positions_final.mask(trading_positions_final == 0, curr_pos)
    new_positions = new_positions.replace({np.nan: 0})

    #update current position
    for i in new_positions.index:
        curr_pos[i] = new_positions[i]

    return curr_pos
