

import numpy as np
from FP.Range import Range
from FP.StrategyPair import StrategyPair

numCards = 52



def setHandsWithConflicts(handArray,cardslist,n):

    for c in cardslist:
        if c < numCards:
            handArray[c, :] = n
            handArray[:, c] = n

def getEquityVsRange(hand, r, ea):
    herocard1, herocard2 = hand
    eqs = ea.eArray[herocard1, herocard2, :, :]

    # avoid including in the calculation hands in r that conflict with the board

    villianRange = np.copy(r.r)
    zeroHandsWithConflics(villianRange, hand + ea.board)
    return sum(sum(np.multiply(eqs, villianRange))) / sum(sum(villianRange))

def conflics(cards1, cards2):
    for i in cards1:
        for j in cards2:
            if i == j and i < numCards:
                return True
    return False

def getEquityVsHandFast(hand, villianHand, ea):
    return ea.eArray[hand[0]][hand[1]][villianHand[0]][villianHand[1]]

def zeroHandsWithConflics(handArray, cardslist):
    for c in cardslist:
        if c < numCards:
            handArray[c, :] = 0
            handArray[:, c] = 0

############### MAX EXPLOIT SECTION ################

def setMaxExplEv(tree,strats,hero,villian):

    '''
    Review chapter 2 for this

    Steps are something like:
       - recursively find the evs of all the children
       - at leaf do the normal stuff
       - at Hero ev is the max over all the choices
       - at Villian ev is the average over all our evs after hero makes his action weighted
            by how often he makes that action

       - at Nature or ev is the average over all possible future cards (card removal)

    Method for running max exploit strategy
    :param tree:
    :param strats:
    :param hero:
    :param villian:
    :return:

    '''
    setMaxExplEvHelper(tree, 0, strats, hero, villian)

def setMaxExplEvHelper(tree,iDecPt,strats,hero,villian):

    '''

    :param tree:
    :param iDecPt:
    :param strats:
    :param hero:
    :param villian:
    :return:
    '''

    currDecPt = tree.decPts[iDecPt]

    if (currDecPt == "Leaf"):
        setMaxExplEVsAtLeaf(tree,iDecPt,strats,hero,villian)

    elif (currDecPt == hero):
        setMaxExplEVsAtHero(tree,iDecPt,strats,hero,villian)

    elif (currDecPt == villian):
        setMaxExplEVsAtVillian(tree,iDecPt,strats,hero,villian)

    else:
        setMaxExplEVsAtNature(tree,iDecPt,strats,hero,villian)

def setMaxExplEVsAtLeaf(tree,iDecPt,strats,hero,villian):

    currDecPt = tree.decPts[iDecPt]

    if currDecPt.parentAction == "fold":

        if (tree.decPts[tree.parents[iDecPt]].player == hero): # hero folded

            strats.evs[hero][iDecPt] = np.ones_like(strats.evs[hero][iDecPt])*(tree.effStack - currDecPt.getPlayerCIP(hero))

        elif (tree.decPts[tree.parents[iDecPt]].player == villian): # hero folded

            strats.evs[hero][iDecPt] = np.ones_like(strats.evs[hero][iDecPt])*(tree.effStack + currDecPt.getPlayerCIP(villian))


    elif currDecPt.parentAction == "call":

        currentPot = currDecPt.getPlayerCIP(hero) + currDecPt.getPlayerCIP(villian)

        for i in range(numCards):

            for j in range(i + 1,numCards):

                strats.evs[hero][iDecPt] = (tree.effStack - currDecPt.getPlayerCIP(hero)) + \
                                          (currentPot*getEquityVsRange([i,j],strats.getMostRecentRangeOf(villian,iDecPt)),currDecPt.eArray)


    else:
        print "error"

    setHandsWithConflicts(strats.evs[hero][iDecPt],currDecPt.eArray.board,-1)

def setMaxExplEVsAtHero(tree,iDecPt,strats,hero,villian):

    strats.evs[hero][iDecPt] = np.zeros_like(strats.evs[hero][iDecPt])

    for ichild in tree.children[iDecPt]:

        setMaxExplEvHelper(tree, ichild, strats, hero, villian)

        strats.evs[hero][iDecPt] = np.maximum(strats.evs[hero][iDecPt],strats.evs[hero][ichild])

def setMaxExplEVsAtVillian(tree,iDecPt,strats,hero,villian):

    for ichild in tree.children[iDecPt]:

        setMaxExplEvHelper(tree, ichild, strats, hero, villian)

        for i in range(numCards):

            for j in range(i + 1,numCards):

                strats.evs[hero][iDecPt][i][j] = 0

                comboCounts = {}

                comboSum = 0

                for iChild in tree.children[iDecPt]:

                    comboCounts[iChild] = strats.ranges[iChild].getNumHandsWithoutConflicts([i,j])

                    comboSum += comboCounts[iChild]

                for iChild in tree.children[iDecPt]:


                    strats.evs[hero][iDecPt][i][j] += strats.evs[hero][iDecPt][i][j] * (comboCounts[iChild] / comboSum)

# The way we end up dealing with conflicts doesnt work when we artificailly restrict
# which cards can come out
def setMaxExplEVsAtNature(tree,iDecPt,strats,hero,villian):

    for iChild in tree.children[iDecPt]:
        setMaxExplEvHelper(tree,iChild,strats,hero,villian)


    villianRange = strats.getMostRecentRangeOf(villian,iDecPt)
    for i in range(numCards):
        for j in range(i + 1, numCards):

            if (conflics(tree.decPts[iDecPt].eArray.board,[i,j])):
                strats.evs[hero][iDecPt][i][j] = -1
                continue

            else:
                comboCounts = {} # number of possible combos that dont conflict with villian or with hero
                comboSum = 0.0

                for iChild in tree.children[iDecPt]:
                    newBoard = tree.decPts[iChild].eArray.board

                    if (conflics(newBoard,[i,j])):
                        comboCounts[iChild] = 0

                    else:
                        comboCounts[iChild] = villianRange.getNumHandsWithoutConflics(newBoard) * tree.decPts[iChild].newCardFreq

                    comboSum += comboCounts[iChild]

                if comboSum == 0:
                    strats.evs[hero][iDecPt][i][j] =  -1
                    continue

                else:

                    strats.evs[hero][iDecPt][i][j] = 0

                    for iChild in tree.children[iDecPt]:
                        strats.evs[hero][iDecPt][i][j] += strats.evs[hero][iDecPt][i][j] * (comboCounts[iChild] / comboSum)


############### GET MAX STRATEGY ################

def getMaxEvStrat(tree,hero,stratPair):

    '''

    IF at Hero:
        Split range to make max ev decesion for all of our hands then call recursive

    IF at villian or nature:
        Call recursively on children


    :param tree:
    :param hero:
    :param stratPair:
    :return: A mapping of decPts to ranges

    '''

    result = {}

    if hero == "SB":

        getMaxEvStratHelper(tree,hero,stratPair,0,stratPair.sbStartingRange,result)

    elif hero == "BB":

        getMaxEvStratHelper(tree,hero,stratPair,0,stratPair.bbStartingRange,result)

    else:
        print "ERROR"

    return result

def getMaxEvStratHelper(tree,hero,stratPair,icurrDecPt,currRange,result):

    '''

    :param tree:
    :param hero:
    :param stratPair:
    :param currDecPt:
    :param currRange:
    :param result:
    :return:

    '''

    currDecPt = tree.decPts[icurrDecPt]

    if  currDecPt.player == hero:

        # init child action ranges
        for iChild in tree.children[icurrDecPt]:
            result[iChild] = Range()

        # then for each hand we could have find the max ev way to play it
        for i in range(numCards):
            for j in range(i + 1,numCards):
                if currRange.r[i][j] > 0:

                    # look at every way we can play it and keep track of best
                    iMaxEv = 0 # index of max ev child action
                    maxEv = -1 # best so far
                    for k in tree.children[icurrDecPt]:
                        if (stratPair.evs[hero][k][i][j] > maxEv):
                            iMaxEv = k
                            maxEv = stratPair.evs[hero][k][i][j]

                    if (maxEv > 0):
                        result[iMaxEv].setFrac([i,j],currRange.r[i][j])

        for iChild in tree.children[currDecPt]:
            getMaxEvStratHelper(tree, hero, stratPair, iChild, result[iChild], result)

    else: # not a hero decesion point
        for iChild in tree.children[currDecPt]:
            getMaxEvStratHelper(tree, hero, stratPair, iChild, currRange, result)


############### DO FP ################

def doFP(tree,niter,sbStartingRange=Range(1.0),bbStartingRange=Range(1.0)):

    # init strategies for both players

    strategyPair = StrategyPair(tree,sbStartingRange,bbStartingRange)

    for i in range(1,niter + 1):

        setMaxExplEv(tree,strategyPair,"SB","BB")
        sbMaxEVStrat = getMaxEvStrat(tree,"SB",strategyPair)
        strategyPair.updateRanges("SB",sbMaxEVStrat,i)

        setMaxExplEv(tree, strategyPair, "BB", "SB")
        bbMaxEVStrat = getMaxEvStrat(tree, "BB", strategyPair)
        strategyPair.updateRanges("BB", bbMaxEVStrat, i)

    return strategyPair