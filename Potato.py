#pairs first then ema

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from statsmodels.tsa.stattools import coint
from emaStrategy import getEMAPosition
from calcMetrics import calcPL

NUM_STOCKS = 100

# functions for determining stock pairs for pairs trading
def how_cointegrated(stock1, stock2):
    """
    Determine how cointegrated stock1 and stock2 are.
    """
    pvalue = coint(stock1, stock2)[1]
    
    return pvalue

def find_top_cointegrated_pairs(stock_prices_df):
    print(f"finding cointegrated pairs...")
    P_VALUE_CUTOFF = 0.05

    # find p-values of how cointegrated each possible combination of stock pairs is
    cointegration_pairs = {}
    for i in range(len(stock_prices_df.columns)):
        for j in range(i + 1, len(stock_prices_df.columns)):
            pair = (i, j)
            cointegration_pairs[pair] = how_cointegrated(stock_prices_df[i], stock_prices_df[j])
    
    cointegration_pairs_series = pd.Series(cointegration_pairs).sort_values()

    # pairs are considered cointegrated only if their p-value is below 0.05
    cointegration_pairs_series = cointegration_pairs_series[cointegration_pairs_series < P_VALUE_CUTOFF]

    # find top possible cointegrated pairs without using the same instrument twice
    all_pairs = list(cointegration_pairs_series.index)
    top_pairs = []
    for pair in cointegration_pairs_series.index:
        if pair in all_pairs:
            top_pairs.append(pair)
            to_remove = []
            for pairs in all_pairs:
                if (pair[0] in pairs) or (pair[1] in pairs):    
                    to_remove.append(pairs)
            all_pairs = [pair for pair in all_pairs if pair not in to_remove]

    return top_pairs

# initialize variable to store position of stocks the day before
global prev_positions
prev_positions = {}
for stock in range(NUM_STOCKS):
    prev_positions[stock] = 0

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
    
    global pairs_trading_pairs
    global ema_stocks
    ema_stocks = [x for x in range(100)] #start off trading with EMA on all stocks

    CALC_EMA_DAY = 50
    if stock_prices_df.shape[0] == CALC_EMA_DAY:
        ema_stocks = []
        for i in range(100):
            prcAll = stock_prices_df[[i]]
            (meanpl, ret, sharpe, dvol) = calcPL(prcAll.values.T, i, CALC_EMA_DAY)
            if (meanpl > 0):
                ema_stocks.append(i)
        print(f"stocks for EMA: {ema_stocks}")

    CALC_PAIRS_DAY = 240
    BUY_AMOUNT = 5
    SELL_AMOUNT = -5
    calc_pairs_flag = False
    pairs_calculated = False
    if stock_prices_df.shape[0] == CALC_PAIRS_DAY or calc_pairs_flag: # calculate pairs on day 250
        pairs_trading_pairs = find_top_cointegrated_pairs(stock_prices_df)

        pairs_trading_stocks = np.array(pairs_trading_pairs).flatten()
        # ema_stocks = [stock for stock in stock_prices_df.columns if stock not in pairs_trading_stocks]
        
        calc_pairs_flag = False
        pairs_calculated = True

    if stock_prices_df.shape[0] > CALC_PAIRS_DAY:
        if not pairs_calculated: # fallback flags, just in case pairs not calculated beforehand
            calc_pairs_flag = True
        else:
            curr_pos = getPairsPosition(stock_prices_df, curr_day, curr_pos, pairs_trading_pairs)

    curr_pos = getEMAPosition(stock_prices_df[ema_stocks], curr_day, curr_pos, BUY_AMOUNT, SELL_AMOUNT)
    
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
    """
    Conduct pair trade in the long position. Go long on stock_1 and short on
    stock_2. Return new positions.
    """
    curr_pos[stock_1] = 10
    curr_pos[stock_2] = -10

    return curr_pos

def pair_to_short(curr_pos, stock_1, stock_2, curr_stock_1, curr_stock_2):
    """
    Conduct pair trade in the short position. Go short on stock_1 and long on
    stock_2 return new positions.
    """
    curr_pos[stock_1] = -10
    curr_pos[stock_2] = 10
    
    return curr_pos