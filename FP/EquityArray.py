

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




def getEquityVsHand(hand1,hand2,board):

    peresult = pe.poker_eval(game='holdem',pockets=[hand1,hand2],board=board)
    numWins = peresult['eval'][0]['winhi']
    numTies = peresult['eval'][0]['tiehi']
    numRunouts = peresult['info'][0]
    return (numWins + numTies/2.0) /numRunouts

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

