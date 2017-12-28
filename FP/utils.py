

import numpy as np

numCards = 52


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

        if (tree.decPts[tree.parents[iDecPt]].parent == hero): # hero folded

            strats.ev[hero][iDecPt] = np.ones_like(strats.ev[hero][iDecPt])*(tree.effStack - currDecPt.getPlayerCIP(hero))

        elif (tree.decPts[tree.parents[iDecPt]].parent == villian): # hero folded

            strats.ev[hero][iDecPt] = np.ones_like(strats.ev[hero][iDecPt])*(tree.effStack + currDecPt.getPlayerCIP(villian))


    elif currDecPt.parentAction == "call":

        currentPot = currDecPt.getPlayerCIP(hero) + currDecPt.getPlayerCIP(villian)

        for i in range(numCards):

            for j in range(i + 1,numCards):

                strats.ev[hero][iDecPt] = (tree.effStack - currDecPt.getPlayerCIP(hero)) + \
                                          (currentPot*getEquityVsRange([i,j],strats.getMostRecentRangeOf(villian,iDecPt)),currDecPt.eArray)

def setMaxExplEVsAtHero(tree,iDecPt,strats,hero,villian):

    strats.ev[hero][iDecPt] = np.zeros_like(strats.ev[hero][iDecPt])

    for ichild in tree.children[iDecPt]:

        setMaxExplEvHelper(tree, ichild, strats, hero, villian)

        strats.ev[hero][iDecPt] = np.maximum(strats.ev[hero][iDecPt],strats.ev[hero][ichild])

def setMaxExplEVsAtVillian(tree,iDecPt,strats,hero,villian):

    for ichild in tree.children[iDecPt]:

        setMaxExplEvHelper(tree, ichild, strats, hero, villian)

        for i in range(numCards):

            for j in range(i + 1,numCards):

                strats.ev[hero][iDecPt][i][j] = 0

                comboCounts = {}

                totalNumHands = 0

                for iChild in tree.children[iDecPt]:

                    comboCounts[iChild] = strats.ranges[iChild].getNumHandsWithoutConflicts([i,j])

                    totalNumHands += comboCounts[iChild]

                for iChild in tree.children[iDecPt]:


                    strats.ev[hero][iDecPt][i][j] += strats.ev[hero][iDecPt][i][j] * (comboCounts[iChild] / totalNumHands)

def setMaxExplEVsAtNature(tree,iDecPt,strats,hero,villian):
    pass