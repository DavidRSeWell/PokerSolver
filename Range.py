# -*- coding: utf-8 -*-
"""
Created on Mon Jul 07 10:38:09 2014

@author: Befeltingu
"""
import os
import numpy as np
import pokereval
import scipy.misc

numCards = 52
numRanks = 13
numSuits = 4
numHands = 1326
numVillianHand = 1225

suits = ['h', 'd', 'c', 's']
ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']

pe = pokereval.PokerEval()


def getEquityVsHandFast(hand, villianHand, ea):
    return ea.eArray[hand[0]][hand[1]][villianHand[0]][villianHand[1]]


def zeroHandsWithConflics(handArray, cardslist):
    for c in cardslist:
        if c < numCards:
            handArray[c, :] = 0
            handArray[:, c] = 0


def getEquityVsRange(hand, r, ea):
    herocard1, herocard2 = hand
    eqs = ea.eArray[herocard1, herocard2, :, :]

    # avoid including in the calculation hands in r that conflict with the board

    villianRange = np.copy(r.r)
    zeroHandsWithConflics(villianRange, hand + ea.board)
    return sum(sum(np.multiply(eqs, villianRange))) / sum(sum(villianRange))


class Range:
    def __init__(self, initFrac=None):
        self.r = np.zeros((numCards, numCards))
        if initFrac != None:
            self.setAllFracs(initFrac)

    def getFrac(self, hand):
        card1, card2 = hand
        if card1 > card2:
            card1, card2 = card2, card1

        return self.r[card1][card2]

    def getNumHands(self):
        return sum(self.r)

    def getNumHandsWithoutConflics(self, cardslist):
        temp = np.copy(self.r)

        zeroHandsWithConflics(temp, cardslist)

        return sum(sum(temp))

    def setFrac(self, hand, f):
        card1, card2 = hand
        if card1 > card2:
            card1, card2 = card2, card1

        self.r[card1][card2] = f

    # set the fraction of all hand combos to num
    def setAllFracs(self, num):
        for i in range(numCards):
            for j in range(i + 1, numCards):
                self.r[i][j] = num

    def scaleFracs(self, num):
        self.r = self.r * num

    # Input:
    #    - rangeString - string containing comma-seperated terms of the form XX
    #   XY,XYs,XYo,XaYb
    # Output: N/A
    # Side-effects: set hand combos specified by the range string to values
    def setRangeString(self, rangeString, value):

        handStrs = rangeString.replace(' ', '').split(',')
        for hand in handStrs:
            if len(hand) == 2:

                rank1 = hand[0]

                rank2 = hand[1]
                for i in suits:
                    for j in suits:
                        # exclude 2c2c
                        if rank1 == rank2 and i == j:
                            continue
                        self.setFrac(pe.string2card([rank1 + i, rank2 + j]), value)

            elif len(hand) == 3:

                rank1 = hand[0]
                rank2 = hand[1]
                if hand[2] == 's':  # suited hands
                    for s in suits:
                        self.setFrac(pe.string2card([rank1 + s, rank2 + s]), value)
                else:  # unsuited hands
                    for i in range(numSuits):
                        for j in range(i + 1, numSuits):
                            self.setFrac(pe.string2card([rank1 + suits[i], rank2 + suits[j]]), value)

            elif len(hand) == 4:
                card1 = hand[0:2]
                card2 = hand[2:4]
                self.setFrac(pe.string2card([card1, card2], value))
            else:
                print("Error!")

    # Input:
    #  suited - boolean
    # Output: fraction of specified ambiguous hand contained in th rank
    # side-effects: N/A
    def getAmbigFrac(self, rank1, rank2, suited):

        nHand = 0.0
        nFrac = 0.0

        for i in suits:
            for j in suits:
                card1 = rank1 + i
                card2 = rank2 + j
                if (suited and i != j) or (not suited and i == j):
                    continue
                if (card1 == card2):
                    continue
                nHand += 1
                nFrac += self.getFrac(pe.string2card([card1, card2]))

        return nFrac / nHand

    def _repr_svg_(self):

        result = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="260" height="260">'

        for i in range(numRanks):
            for j in range(numRanks):
                frac = self.getAmbigFrac(ranks[i], ranks[j], i > j)
                hexcolor = '#%02x%02x%02x' % (255 * (1 - frac), 255, 255 * (1 - frac))
                result += '<rect x="' + str(i * 20) + '"' + ' ' + 'y="' + str(j * 20) \
                          + '" width="20" height="20" fill="' + hexcolor + '"/>'
                result += '<text x="' + str(i * 20) + '"' + ' ' + 'y="' + str((j + 1) * 20) + '" font-size="12" >' \
                          + ranks[i] + ranks[j] + '</text>'
        result += '</svg>'

        return result

    def setToTop(self, fraction, board):

        rangeAllHands = Range()
        rangeAllHands.setAllFracs(1.0)
        handsSorted = getHandsSortedAndEquities(rangeAllHands, board)

        numCardsLeft = numCards
        for c in board:
            if c < numCards:
                numCardsLeft -= 1

        self.setAllFracs(0)
        for i in range(int(fraction * scipy.misc.comb(numCardsLeft, 2))):
            self.setFrac(handsSorted[i][0], 1.0)

    def getHandsSortedAndEquities(self, villianRange, board):

        ea = EquityArray(board)
        result = []
        for i in range(numCards):
            for j in range(i + 1, numCards):
                hand = [i, j]
                if not conflics(board, hand):
                    result.append((hand, getEquityVsRange(hand, villianRange, ea)))

        result.sort(key=lambda x: x[1], reverse=1)

        return result


def conflics(cards1, cards2):
    for i in cards1:
        for j in cards2:
            if i == j and i < numCards:
                return True
    return False


def getEquityVsHand(hand1, hand2, board):
    peresult = pe.poker_eval(game='holdem', pockets=[hand1, hand2], board=board)
    numWins = peresult['eval'][0]['winhi']
    numTies = peresult['eval'][0]['tiehi']
    numRunouts = peresult['info'][0]
    return (numWins + numTies / 2.0) / numRunouts


class EquityArray:
    def __init__(self, b):
        self.board = b
        self.eArray = np.zeros((numCards, numCards, numCards, numCards))

        if os.path.isfile(self.getFilename()):
            self.eArray = np.load(self.getFilename())

        else:
            self.makeArray()

    def makeArray(self):
        for i in range(numCards):
            for j in range(numCards):
                for a in range(numCards):
                    for b in range(numCards):
                        hand = [i, j]
                        villianHand = [a, b]
                        self.eArray[i][j][a][b] = getEquityVsHand(hand, villianHand, self.board)
        np.save(self.getFilename(), self.eArray)

    # ouput: filename builf from self.board
    def getFilename(self):

        boardStr = ''
        boardAsStrings = pe.card2string(self.board)
        for i in boardAsStrings:
            if i != '__':
                boardStr = boardStr + i

        if boardStr == '':  # for the preflop board
            boardStr = 'preflop'
        boardStr = boardStr + '.ea.npy'
        return boardStr

        # modifys r1 to incorporate some amount of r2. The fraction of every hand in r1


# at the end of the function will be (old amount) * (fraction) + (new amount) * (1 - fraction)
#    where fraction becomes closer to 1 the higher n is
def updateRange(r1, r2, n):
    fraction = 1 - 1 / (n + 2.0)

    for i in range(numCards):
        for j in range(i + 1, numCards):
            hand = [i, j]
            r1.setFrac(hand, (r1.getFrac(hand)) * (fraction) + (r2.getFrac(hand)) * (1 - fraction))


def doShoveFoldGame():
    nIter = 5  # number of iterations

    S = 10  # stack size in BBs

    ea = EquityArray(pe.string2card(['__', '__', '__', '__', '__']))

    sbJamRange = Range()
    sbJamRange.setAllFracs(0.5)

    bbCallRange = Range()

    bbCallRange.setAllFracs(0.5)

    for n in range(nIter):

        # solve for Sb max expl strat
        bestSBJamRange = Range()
        for i in range(numCards):
            for j in range(i + 1, numCards):
                hand = [i, j]
                bb_call_freq = bbCallRange.getNumHandsWithoutConflics(hand) / numVillianHand
                # evJame = (chance BB folds) * (S + 1) + (chance BB calls) * equity * 2*S

                equity = getEquityVsRange(hand, bbCallRange, ea)

                evJam = (1 - bb_call_freq) * (S + 1) + (bb_call_freq) * equity * 2 * S
                evFold = S - 0.5

                if (evJam > evFold):
                    bestSBJamRange.setFrac(hand, 1)
                else:
                    bestSBJamRange.setFrac(hand, 0)

        # update SB strategy
        updateRange(sbJamRange, bestSBJamRange, n)
        # solve for BB max expl strat
        bestBBCallRange = Range()
        for i in range(numCards):
            for j in range(i + 1, numCards):

                hand = [i, j]
                equity = getEquityVsRange(hand, sbJamRange, ea)
                evCall = 2 * S * equity
                evFold = S - 1

                if (evCall > evFold):
                    bestBBCallRange.setFrac(hand, 1)
                else:
                    bestBBCallRange.setFrac(hand, 0)

        updateRange(bbCallRange, bestBBCallRange, n)

    display(sbJamRange)
    display(bbCallRange)