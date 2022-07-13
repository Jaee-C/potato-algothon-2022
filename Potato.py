#pairs first then ema

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

NUM_STOCKS = 100

global pairs_trading_pairs #stocks used for pair trading
pairs_trading_pairs = [(61, 35), (49, 60), (25, 69), (59, 9), (81, 38), (92, 88), (68, 80), (90, 39), (11, 76), (43, 53), (12, 18), (31, 70), (8, 91), (99, 58), (42, 33), (51, 89), (83, 20), (71, 66), (17, 16), (74, 44), (57, 36), (96, 47), (13, 62), (6, 97), (26, 10), (78, 15), (45, 93), (55, 41), (23, 52), (87, 34), (64, 75), (2, 63), (56, 84), (86, 0)]

global ema_stocks #stocks used for ema (basically all the stocks not used for pairs trading)
ema_stocks = [1, 3, 4, 5, 7, 14, 19, 21, 22, 24, 27, 28, 29, 30, 32, 37, 40, 46, 48, 50, 54, 65, 67, 72, 73, 77, 79, 82, 85, 94, 95, 98]

#computations for determining ema_stocks and pairs_trading_pairs were done offline on price data from day 0-250. to see how it was done view ___.ipynb
#^is this legal

#initialize variable to store position of stocks the day before
global prev_positions
prev_positions = {}
for stock in range(NUM_STOCKS):
    prev_positions[stock] = 0

def getMyPosition(stock_prices):
    """Takes as input a NumPy array of the shape nInst x nt. nInst = 100 is the number of instruments. nt is the number of days for which the prices have been provided. Returns a vector of desired positions."""

    stock_prices_df = pd.DataFrame(stock_prices).T
    curr_day = len(stock_prices[0]) - 1
    curr_pos = np.zeros(100)
    
    # curr_pos = getPairsPosition(stock_prices_df, curr_day, curr_pos, pairs_trading_pairs)
    curr_pos = getEMAPosition(stock_prices_df[ema_stocks], curr_day, curr_pos)

    return curr_pos

def getEMAPosition(stock_prices_df, curr_day, curr_pos):
    ema5 = stock_prices_df.ewm(span=10, adjust=False).mean()
    ema20 = stock_prices_df.ewm(span=30, adjust=False).mean()
    ema50 = stock_prices_df.ewm(span=60, adjust=False).mean()
    # ema100 = stock_prices_df.ewm(span=100, adjust=False).mean()

    buy_signals = ema5.gt(ema20) & (stock_prices_df.gt(ema50) & ema5.gt(ema50) & ema20.gt(ema50))
    sell_signals = ema5.lt(ema20) #& (stock_prices_df.lt(ema50) & ema5.lt(ema50) & ema20.lt(ema50))

    buy_signals = buy_signals.replace({True: 1, False: 0})
    sell_signals = sell_signals.replace({True: -1, False: 0})
    trading_positions = (buy_signals + sell_signals) * 10

    last_day = trading_positions.iloc[-1:]
    transposed_trading_positions = last_day.T
    trading_positions_final = transposed_trading_positions.iloc[:, 0]
    new_positions = trading_positions_final.mask(trading_positions_final == 0, curr_pos)
    new_positions = trading_positions_final.shift(1)
    new_positions = new_positions.replace({np.nan: 0})

    #update current position
    for i in new_positions.index:
        curr_pos[i] = new_positions[i]

    return curr_pos

    # OLD
    ema = stock_prices_df.ewm(span=100, adjust=False).mean()

    trading_positions_raw = stock_prices_df - ema
    trading_positions = trading_positions_raw.apply(np.sign) * 10
    trading_positions_final = trading_positions.shift(1)
    new_positions = trading_positions_final.iloc[-1:].fillna(0)

    # update current position
    for i in new_positions.columns:
        curr_pos[i] = new_positions[i].iloc[-1]

    return curr_pos

def getPairsPosition(stock_prices_df, curr_day, curr_pos, pairs_trading_pairs):
    WINDOW = 30

    for pair in pairs_trading_pairs:
        stock_1 = pair[0]
        stock_1_prices = stock_prices_df[stock_1]
        
        stock_2 = pair[1]
        stock_2_prices = stock_prices_df[stock_2]
        
        #spread between stock 1 and 2
        pair_spread = stock_1_prices - stock_2_prices
        
        #most current mean and standard deviation values of the pair spread
        pair_spread_mean = pair_spread.ewm(WINDOW).mean().iloc[curr_day]
        pair_spread_stdev = pair_spread.ewm(WINDOW).std().iloc[curr_day]

        #upper bound and lower bound for going short and long respectively
        pair_upper_bound = pair_spread_mean + 2 * pair_spread_stdev
        pair_lower_bound = pair_spread_mean - 2 * pair_spread_stdev

        #current spread and current stock prices
        curr_pair_spread = pair_spread.iloc[curr_day]
        curr_stock_1 = stock_1_prices.iloc[curr_day]
        curr_stock_2 = stock_2_prices.iloc[curr_day]
        
        #if pair spread exceeds upper bound, stock_1 is overvalued and stock_2 undervalued. go short on the pair
        if (curr_pair_spread >= pair_upper_bound) and (prev_positions[stock_1] >= 0):
            curr_pos = pair_to_short(curr_pos, stock_1, stock_2, curr_stock_1, curr_stock_2)
            prev_positions[stock_1] = curr_pos[stock_1]
            prev_positions[stock_2] = curr_pos[stock_2]
        #if pair spread exceeds lower bound, stock_1 is undervalued and stock_2 overvalued. go long on the pair
        elif (curr_pair_spread <= pair_lower_bound) and (prev_positions[stock_1] <= 0):
            curr_pos = pair_to_long(curr_pos, stock_1, stock_2, curr_stock_1, curr_stock_2)
            prev_positions[stock_1] = curr_pos[stock_1]
            prev_positions[stock_2] = curr_pos[stock_2]
        #if spread is within thresholds continue to maintain previous position
        else:
            curr_pos[stock_1] = prev_positions[stock_1]
            curr_pos[stock_2] = prev_positions[stock_2]

    return curr_pos

def pair_to_long(curr_pos, stock_1, stock_2, curr_stock_1, curr_stock_2):
    "conduct pair trade in the long position. go long on stock_1 and short on stock_2. return new positions"
    MAX_POSITION_VALUE = 10000
    curr_pos[stock_1] = (MAX_POSITION_VALUE/curr_stock_1)
    curr_pos[stock_2] = -(MAX_POSITION_VALUE/curr_stock_2)

    return curr_pos

def pair_to_short(curr_pos, stock_1, stock_2, curr_stock_1, curr_stock_2):
    "conduct pair trade in the short position. go short on stock_1 and long on stock_2 return new positions"
    MAX_POSITION_VALUE = 10000
    curr_pos[stock_1] = -(MAX_POSITION_VALUE/curr_stock_1)
    curr_pos[stock_2] = (MAX_POSITION_VALUE/curr_stock_2)
    
    return curr_pos