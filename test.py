# -*- coding: utf-8 -*-
"""
Created on Fri Jul 04 10:04:34 2014

@author: Befeltingu
"""
import os
import pokereval
import numpy
import matplotlib.pyplot as plt

from Range import *

# board = ['__','__','__','__','__']

board = (['8d', '6s', '3h', 'Kd', 'Jd'])

pe = pokereval.PokerEval()
board = pe.string2card(board)
hand = pe.string2card(['4d', '5d'])


def plotEqDistn(r1, r2, board):
    xs = []
    ys = []

    handCount = 0.0
    for hand in r1.getHandsSortedAndEquities(r2, board):
        # plot hand at (handCount, equity)
        xs.append(handCount)
        handCount += r1.getFrac(hand[0])
        xs.append(handCount)
        ys.append(hand[1])
        ys.append(hand[1])

    plt.plot(xs, ys)
    plt.show()


# meEArray = EquityArray.EquityArray(board)

# %timeit ipython function for knowing time it takes to run function

# equity = getEquityVsHandFast(hand,villianHand,meEArray)



range1 = Range()
range1.setAllFracs(1.0)

display(range1)




