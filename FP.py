
# modifys r1 to incorporate some amount of r2. The fraction of every hand in r1
#	at the end of the function will be (old amount) * (fraction) + (new amount) * (1 - fraction)
#	where fraction becomes closer to 1 the higher n is
def updateRange(r1,r2,n):

	fraction = 1 - 1 / (n + 2.0)

	for i in range(numCards):
		for j in range(i + 1, numCards):
			hand = [i,j]
			r1.setFrac(hand, (r1.getFrac(hand))* (fraction) + (r2.getFrac(hand)) * (1-fraction))




def doShoveFoldGame():

	nIter = 15 # number of iterations

	S = 10 # stack size in BBs

	ea = EquityArray(pe.string2card(['__','__','__','__','__']))

	sbJamRange = Range()
	sbJamRange.setAllFracs(0.5)

	bbCallRange = Range()

	bbCallRange.setAllFracs(0.5)

	for n in range(nIter):

		# solve for Sb max expl strat
		bestSBJamRange = Range()
		for i in range(numCards):
			for j in range(i+1,numCards):
				hand[i,j]
				bb_call_freq = bbCallRange.getNumHandsWithoutConflicts(hand) / numVilliaHand
				# evJame = (chance BB folds) * (S + 1) + (chance BB calls) * equity * 2*S

				equity = getEquityVsRange(hand, bbCallRange, ea)
				evJam = (1- bb_call_freq) * (S + 1) + (bb_call_freq) * equity * 2*S
				evFold = S - 0.5
				if(evJam > evFold):
					bestSBJamRange.setFrac(hand,1)
				else:
					bestSBJamRange.setFrac(hand,0)


		# update SB strategy
		updateRange(sbJamRange, bestSBJamRange,n)
		# solve for BB max expl strat
		bestBBCallRange = Range()
		for i in range(numCards):
			for j in range(i+1,numCards):
				hand[i,j]

				equity = getEquityVsRange(hand,sbJamRange,ea)
				evCall = 2 * S * equity
				evFold = S -1

				if (evCall > evFold):
					bestBBCallRange.setFrac(hand,1)
				else:
					bestBBCallRange.setFrac(hand,0)

		updateRange(bbCallRange, bestBBCallRange,n)