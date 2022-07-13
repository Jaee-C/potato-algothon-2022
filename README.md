<h1 align="center"> 🥔 Team Potato 🥔 </h1>

> Our submission for Algothon 2022

---

## 🎥 [Submission Video](https://www.youtube.com/watch?v=3SUyNNUIobo&ab_channel=wafflesorpacakes)

---

## ⚖️ EMA
### Theory
* Works similarly to Simple Moving Average (SMA), which represents the average price in the past ɳ days.
* However,  this strategy has a lag time lage in terms of responding to the changes of the real-time prices
* One solution to this problem is to use exponential  moving average , which weighs recent prices more heavily.
* This reduces the time lag and tends to reflect the trends of the instrument prices more accurately.

### Implementation
* The moving average strategy is going to take advantage of the fact that a moving average time series (whether SMA or EMA) lags the actual price behaviour.
* Bearing this in mind, it is natural to assume that when a change in the long term behaviour of the asset occurs, the actual price time series will react faster than the EMA one.
* Strategy #1: consider the crossing of the two time series as potential trading signals:
  1. When the price time series  crosses the EMA time series  from below, we will close any existing short position and go long (buy) the asset.
  2. When the price time series  crosses the EMA time series from above, we will close any existing long position and go short (sell) the asset.
* Strategy #2 (this was implemented in our final algorithm): consider the crossing of shorter term EMAs with longer term EMAs
  * We first calculate multiple EMAs for evaluation, namely the 10-day (EMA10), 30-day (EMA30) and 60-day (EMA60) EMAs
  1. generally, when a shorter term EMA crosses a longer term EMA from below, we will close any existing short position and go long (buy) the asset.
    * Our specific algorithm buys and instrument if the following, specific conditions are met:
      1. EMA10 crosses EMA30 from below (ie. EMA10 > EMA30), and
      2. EMA30 > EMA60, and
      3. EMA10 > EMA60, and
      4. current price of instrument > EMA60
  2. When the shorter term EMA crosses a longer term EMA from above, we will close any existing long position and go short (sell) the asset.
  * Our specific algorithm buys and instrument if the following, specific conditions are met:
        1. EMA10 crosses EMA30 from above (ie. EMA10 <> EMA30), or
        2. EMA30 < EMA60
* Strategy 2 performed in less trades than Strategy 1 and yielded better returns
* We found that looser shorting conditions performed better than tighter ones (`or` instead of `and`)
* We also found that buying and selling 5 units of instruments resulted in the best returns and Shape Ratio, although at a slightly disadvantaged P&L, the low 
* We chose to buy and sell 5 units of instruments for every EMA trade because it minimised risk, although at the expense of lower return

### Stop-Loss
* In addition to the above long and short signals, we added an additional barrier to limit our losses and minimise our risk further by implementing Stop-Loss Ordering

### `calcMetrics.py`
* After the first 50 days, we calculate the P&L of each stock to evaluate the performance of EMA
* Following that, we only use EMA on stocks that produced positive P&L for those first 50 days

## 🧦 Pairs
### Theory
* Spread = Price of Stock 1 - Price of Stock 2
* Two stocks are cointegrated → The spread between a pair of stocks tends to revert back to the mean spread over time
* Gives us a reliable measure of when a stock is overvalued or undervalued, 
relative to its pair
* When spread is higher than the mean, it implies that:
  * Stock 1 is overvalued → Good to sell/short
  * Stock 2 is undervalued → Good to buy/long
* Overall, we would take a short position on the pairs trade
* When spread is lower than the mean, it implies that:
  * Stock 1 is undervalued→ Good to buy/long
  * Stock 2 is overvalued→ Good to sell/short
* Overall, we would take a long position on the pairs trade

### Implementation
* the pair strategy's code is located in `Potato.py`
* it takes the first 240 days of data to determine which stocks are good pairs through cointegration
* as such, this strategy only starts trading after the 240th day
1.  Determine most cointegrated stock pairs to pairs trade on
2. Whenever getMyPosition() is called, calculate the 30 day rolling mean and standard deviation of the spread of the pairs to determine moving upper and lower spread thresholds
3. The spread thresholds for when we will perform trades on a pair will be:
4. Upper threshold: Mean + 2 * standard deviation → If spread exceeds this, short the pair 5. Lower threshold: Mean - 2 * standard deviation → If spread is below this, long the pair

---

## 🌈 Group Members
* Chuah Xin Yu (Team Lead): EMA, Stop-Loss
* Aurelia Iskandar: Pairs, Video Submission
* Daniel Chin Weng Jae: EMA, EMA Metrics
* Victoria Halim: Pairs
