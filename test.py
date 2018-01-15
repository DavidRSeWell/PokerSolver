# -*- coding: utf-8 -*-
"""
Created on Fri Jul 04 10:04:34 2014

@author: Befeltingu
"""
import os
import pokereval
import numpy
import matplotlib.pyplot as plt
import pydot
from FP.EquityArray import EquityArray
from FP.utils import doFP
import pandas as pd


from FP.DTree import DecesionTree
from FP.DPoint import DecesionPoint

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

def getEquityVsHand(hand1,hand2,board):

    peresult = pe.poker_eval(game='holdem',pockets=[hand1,hand2],board=board)
    numWins = peresult['eval'][0]['winhi']
    numTies = peresult['eval'][0]['tiehi']
    numRunouts = peresult['info'][0]
    return (numWins + numTies/2.0) /numRunouts

def getHandVsAll(hand1,board):

    hand_string = pe.card2string(hand1)
    result_list = []
    for i in range(52):
        for j in range(52):
            if i != j:

                equity_result = getEquityVsHand(hand1,[i,j],board)

                hand2_string = ''.join(pe.card2string([i,j]))

                result_list.append([hand2_string,equity_result])

    return result_list

run_min_raise_shove = 0
if run_min_raise_shove:


    S = 20

    pe = pokereval.PokerEval()

    board = ['__','__','__','__','__']


    preFlopEquity = EquityArray(board=pe.string2card(board))

    point0 = DecesionPoint("SB",0.5,1.0)
    point1 = DecesionPoint("Leaf",0.5,1.0,preFlopEquity,parentAction="fold")
    point2 = DecesionPoint("BB",2.0,1.0,preFlopEquity,parentAction="bet")
    point3 = DecesionPoint("Leaf",2.0,1.0,preFlopEquity,parentAction="fold")
    point4 = DecesionPoint("SB",2.0,20.0,preFlopEquity,parentAction="bet")
    point5 = DecesionPoint("Leaf",2.0,20.0,preFlopEquity,parentAction="fold")
    point6 = DecesionPoint("Leaf",20.0,20.0,preFlopEquity,parentAction="call")



    tree = DecesionTree(S,point0)

    tree.addDecPt(point1,point0)
    tree.addDecPt(point2,point0)
    tree.addDecPt(point3,point2)
    tree.addDecPt(point4,point2)
    tree.addDecPt(point5,point4)
    tree.addDecPt(point6,point4)

    minRFoldSolution = doFP(tree,100)


test_distributions = 1
if test_distributions:

    pe = pokereval.PokerEval()

    board = ['Ah', '3s', '7d', '9h', '__']

    #turnEquity = EquityArray(board=pe.string2card(board))

    hand = ['As','4d']

    handVsAll = getHandVsAll(pe.string2card(hand),board)

    hand_df = pd.DataFrame(handVsAll,columns=['hand','equity'])

    print "ya"










