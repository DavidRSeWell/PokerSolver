

import pydot



class DecesionTree(object):

    '''
    Dec pts: [A,B,C,D]
    children = []
    parents = [4,3,3,None]
    S = effective stack size
    '''

    def __init__(self,S,root):

        self.effStack = S
        self.decPts = [] # list of alll dec points in the tree
        self.children = []
        self.parents = []
        self.addDecPt(root,None)


    def getNumPoints(self):
        return len(self.decPts)


    def getEffStack(self):
        '''
        Eff stack refers to stacks at beginning of decesion tree
            when CIP = 0
        :return:
        '''
        return self.effStack

    def addDecPt(self,point,parent):

        self.decPts.append(point)
        self.children.append([])
        if parent is None:
            self.parents.append(None)

        else:
            parentIndex = self.decPts.index(parent)
            self.children[parentIndex].append(self.getNumPoints() - 1)
            self.parents.append(parentIndex)


    def _repr_png_(self):

        g = pydot.Dot(graph_type="digraph")

        for i in range(self.getNumPoints()):

            node_label = str(i) + ": " + self.decPts[i].player \
                        + ' ( ' + str(self.decPts[i].initial_sb_cip) + ',' \
                        + str(self.decPts[i].initial_bb_cip) + ' ) '

            g.add_node(pydot.Node('node%d'%i,label=node_label))

        for i in range(self.getNumPoints()):
            for j in self.children[i]:
                edge = pydot.Edge('node%d'%i, 'node%d'%j,label=self.decPts[j].parentAction)
                g.add_edge(edge)


        write_path = 'FP/tree.png'
        g.write(write_path,format="png")

        return g.create(g.prog,'png')