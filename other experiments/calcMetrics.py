"""
Calculate metric to determine which stocks to use (for EMA)
"""

import numpy as np
import pandas as pd

from emaStrategy import getEMAPosition

# Commission rate
commRate = 0.0025 # was 0.0050

# Dollar position limit (maximum absolute dollar value of any individual stock position)
dlrPosLimit = 10000

def calcPL(prcHist, start_day, end_day):
    global tStart
    cash = 0
    curPos = np.zeros(1)
    value = 0
    todayPLL = []
    (_,nt) = prcHist.shape
    for t in range(start_day, end_day): 
        prcHistSoFar = prcHist[:,:t]
        # no trades on the very last price update, only before the last update
        newPosOrig = curPos
        #print ("tRunning: %.4lf" % tRunning)
        newPosOrig = getEMAPosition(pd.DataFrame(prcHistSoFar).T, t, curPos, 10, -10)
        curPrices = prcHistSoFar[:,-1] #prcHist[:,t-1]
        posLimits = np.array([int(x) for x in dlrPosLimit / curPrices])
        newPos = np.array([int(p) for p in np.clip(newPosOrig, -posLimits, posLimits)])
        deltaPos = newPos - curPos
        dvolumes = curPrices * np.abs(deltaPos)
        dvolume = np.sum(dvolumes)
        comm = dvolume * commRate
        cash -= curPrices.dot(deltaPos) + comm
        curPos = np.array(newPos)
        posValue = curPos.dot(curPrices)
        todayPL = cash + posValue - value
        todayPLL.append(todayPL)
        value = cash + posValue
    pll = np.array(todayPLL)
    (plmu,plstd) = (np.mean(pll), np.std(pll))
    return plmu
