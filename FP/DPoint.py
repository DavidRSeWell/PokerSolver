







class DecesionPoint(object):
    '''
        Attributes:
            player - whose decesion point it is
            sb chip in pot
            bb chip in pot
            eArray - EArray describing the current board
            parentAction: string describing that got us to this point
                "bet",check,fold,call or board cards

            newcardFreq: only used if parentAction was new cards being dealt
                        we dont want all new cards to have equal probab of falling
    '''

    def __init__(self, player,initial_sb_cip,initial_bb_cip,eArray=None,parentAction="",newCardFreq = 1.0):

        self.player = player

        self.initial_sb_cip = initial_sb_cip

        self.initial_bb_cip = initial_bb_cip

        self.eArray = eArray

        self.parentAction = parentAction

        self.newCardFreq = newCardFreq


    def getPlayerCIP(self,player):
        '''
        Get chips for a given player at the beginning of the decision point
        :param player:
        :return:
        '''

        if player == "SB":
            return self.initial_sb_chip

        elif player == "BB":

            return self.initial_bb_chip

        else:
            print "ERROR: DecesionPoint.getPlayerCIP given player that doesnt exist"


