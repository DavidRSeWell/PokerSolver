

from FP.Range import Range
import numpy as np

numCards = 52

# at the end of the function will be (old amount) * (fraction) + (new amount) * (1 - fraction)
#    where fraction becomes closer to 1 the higher n is
def updateRange(r1, r2, n):
    fraction = 1 - 1 / (n + 2.0)

    for i in range(numCards):
        for j in range(i + 1, numCards):
            hand = [i, j]
            r1.setFrac(hand, (r1.getFrac(hand)) * (fraction) + (r2.getFrac(hand)) * (1 - fraction))


class StrategyPair(object):
    '''
    Strategy: A range for every action a player can take
    Strategy Pair: Is a Strategy for each player
    Every strategy/range is associated with a certain point

    Strategy Pair will:
        - hold a tree
        - hold starting ranges
        - hold a list of ranges s.t. range[i] is the list of hands that takes the parent action
        of decPts[i]
        - When
    '''

    def __init__(self,tree,sbStartingRange=Range(1.0),bbStartingRange=Range(1.0)):

        self.tree = tree
        self.size = self.tree.getNumPoints()
        self.ranges = [Range() for r in range(self.size)]
        self.evs = dict()
        self.evs["SB"] = np.zeros((self.size,numCards,numCards))
        self.evs["BB"] = np.zeros((self.size,numCards,numCards))

        self.sbStartingRange = sbStartingRange
        self.bbStartingRange = bbStartingRange


    def getStartingRange(self,player):
        '''

        :param player:
        :return:
        '''
        if player == "SB":
            return self.sbStartingRange
        elif player == "BB":
            return self.bbStartingRange
        else:
            print "ERROR"

    def getRange(self,n):
        return self.ranges[n]

    def updateRanges(self,player,maxExpStrat,n):

        for i in range(self.size):
            if (self.tree.decPts[i].player == player):
                for j in self.tree.children[i]:

                    updateRange(self.ranges[j],maxExpStrat[j],n)


    def getMostRecentRangeOf(self,player,iDecPt):
        curriDecPt = iDecPt
        while(self.tree.decPts[self.tree.parents[curriDecPt]].player != player):
            curriDecPt = self.tree.parents[curriDecPt]
            if curriDecPt == 0:
                return self.getStartingRange(player)

        return self.ranges[curriDecPt]



    def dump(self):
        '''
        display all ranges and actions
        :return:
        '''
        for i in range(1,self.size):
            parentActor = self.tree.decPts[self.tree.parents[i]].player
            action = self.tree.decPts[i].parentAction
            print( str(i) + ": " + parentActor + " " + str(action))

            if parentActor != "Nature":
                #display(self.ranges[i])
                pass


    def initialize(self):
        '''
        Set all ranges in Strategy pair
        :return:
        '''
        self.initializeHelper(0,1.0,1.0)


    def initializeHelper(self,icurrDecpt,sbScale,bbScale):
        children = self.tree.children[icurrDecpt]
        numChildren = len(children)
        if self.tree.decPts[icurrDecpt].player == "SB":
            sbScale /= numChildren
            for iChild in children:
                self.ranges[iChild].r = self.sbStartingRange.r.copy()
                self.ranges[iChild].scaleFracs(sbScale)
                self.ranges[iChild].removeHandsWithConflicts(self.tree.decPts[iChild].eArray.board)

        elif self.tree.decPts[icurrDecpt].player == "BB":
            bbScale /= numChildren
            for iChild in children:
                self.ranges[iChild].r = self.bbStartingRange.r.copy()
                self.ranges[iChild].scaleFracs(bbScale)
                self.ranges[iChild].removeHandsWithConflicts(self.tree.decPts[iChild].eArray.board)

        for iChild in children:
            self.initializeHelper(iChild,sbScale,bbScale)






