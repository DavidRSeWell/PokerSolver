# -*- coding: utf-8 -*-
"""
Created on Fri Jul 04 11:06:46 2014

@author: Befeltingu
"""

import os
import numpy
import pokereval
2 + 2
numCards = 52
numRanks = 13
numSuits = 4
numHands = 1326
numVillianHand = 1225

suits = ['h', 'd','c','s']
ranks = ['A', 'K','Q','J','T','9','8','7','6','5','4','3','2']

cards = ['Ah', 'Kh','Qh','Jh','Th','9h','8h','7h','6h','5h','4h','3h','2h',
         'Ad', 'Kd','Qd','Jd','Td','9d','8d','7d','6d','5d','4d','3d','2d',
         'Ac', 'Kc','Qc','Jc','Tc','9c','8c','7c','6c','5c','4c','3c','2c',
         'As', 'Ks','Qs','Js','Ts','9s','8s','7s','6s','5s','4s','3s','2s']


pe = pokereval.PokerEval()


def conflics(cards1, cards2):
    for i in cards1:
        for j in cards2:
            if i == j and i < numCards:
                return True
    return False


def getEquityVsHand(hand1,hand2,board):

    peresult = pe.poker_eval(game='holdem',pockets=[hand1,hand2],board=board)
    numWins = peresult['eval'][0]['winhi']
    numTies = peresult['eval'][0]['tiehi']
    numRunouts = peresult['info'][0]
    return (numWins + numTies/2.0) /numRunouts

class EquityArray:

    def __init__(self,b):
        self.board = b
        self.eArray = numpy.zeros((numCards,numCards,numCards,numCards))

        if os.path.isfile(self.getFilename()):
            self.eArray = numpy.load(self.getFilename())

        else:
            self.makeArray()

    def makeArray(self):
        for i in range(numCards):
            for j in range(numCards):
                for a in range(numCards):
                    for b in range(numCards):
                        hand = [i,j]
                        villianHand = [a,b]
                        self.eArray[i][j][a][b]= getEquityVsHand(hand, villianHand, self.board)
        numpy.save(self.getFilename(), self.eArray)

    #ouput: filename builf from self.board
    def getFilename(self):


        boardStr = ''
        boardAsStrings = pe.card2string(self.board)
        for i in boardAsStrings:
            if i != '__':
                boardStr = boardStr + i

        if boardStr == '': # for the preflop board
            boardStr = 'preflop'
        boardStr = boardStr + '.ea.npy'
        return boardStr
