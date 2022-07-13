# [SIG x UNSW FinTech Algothon] Workshop 2

## Performance and Risk metrics
* P&L
* WinRate = #WinDays/#AllDays
* Volume, DollarVolume (Turnover)
* Return = P&L/DollarVolume
* SharpeRatio = P&L/StdDev(P&L)
* ...

## Ideas
### Fair Price
* ![](./2022-06-30-15-13-20.png)
* How to calculate "Fair" price?
  * some linear combination of prices of other stocks (eg. average)
  * linear combination of other indicators
  * regression (based on history)
  * fair is non-linear function of prices and whatever other indicators (linear, poly, log, etc. or neural net)

### Pairs
* how to identify good "pairs" of stocks?
  * price difference, price ratio, correlation, imagination, etc.?
* when the discrepancy is large enough to trade?
  * threshold
* 

### Lead-Lag
* ![](./2022-06-30-15-21-12.png)
* red stock goes in the same direction of blue stock
  * blue stock is leading red stock
  * so if blue goes up, buy red (because we expect it to follow the lead)
* How to identify leaders and laggards?
  * amount of time delay to consider?
  * effect of noise?
* more general idea: stock(s) can help forecast another stock(s)

## Modelling from historic data
* ![](./2022-06-30-15-24-33.png)
* Stationarity
  * ![](./2022-06-30-15-30-02.png)
    * first and second examples are stationary
    * third one may or may not be stationary
* ![](./2022-06-30-15-32-19.png)
* Natural Log
  * ![](./2022-06-30-15-34-56.png)
  * log prices and then differences - might find stationarity

## Overfitting
* ![](./2022-06-30-15-39-50.png)
  * k-fold cross validation


## Q&A
* standard libraries like `scikit-learn`, `numpy`, `pandas` is okay
* more info about the competition will be on Monday
  * daily updates
  * horizon: over a year
* 100 instruments
  * price: 250?
* allowed to have long and short positions