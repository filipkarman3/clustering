import networkx as nx
import matplotlib.pyplot as plt
from pprint import pprint

class TypeClusterer:
    consensus = 0.7
    threshold = 0.6

    def __init__(self, output=False):
        self.output = output

    def cluster(self, db, ws):
        simG = self.getSimilarities(db, ws)
        clusters = [[w] for w in ws]
        toAdd    = []
        while True:
            changed   = False
            clusters += toAdd
            toAdd     = []
            clusters  = list(filter(lambda x:len(x)>0, clusters))
            
            for i in range(len(clusters)):
                c1 = clusters[i]
                if len(c1)==0: continue
                for j in range(len(clusters)):
                    if i==j: continue
                    c2 = clusters[j]
                    if len(c2)==0: continue

                    for w in c2:
                        # get popularity of w in c1
                        similar = 0
                        for w1 in c1:
                            if simG[w][w1] > self.threshold:
                                similar+=1
                        popularityC1 = similar/len(c1)
                        
                        # get popularity of w in c2
                        similar = 0
                        for w2 in c2:
                            if w==w2: continue
                            if simG[w][w2] > self.threshold:
                                similar+=1
                        popularityC2 = 0 if len(c2)==1 else similar/(len(c2)-1)

                        # one word cluster can be subsumed into th'other
                        if len(c2)==1 and popularityC1>self.consensus:
                            changed = True
                            c1.append(w)
                            c2.remove(w)
                        elif len(c2)==1:
                            continue

                        # if unpopular in both, make own cluster
                        elif popularityC1<self.consensus and popularityC2<self.consensus:
                            toAdd.append([w])
                            c2.remove(w)
                            changed = True
                        
                        # if unpopular in 2, make cluster in 1
                        elif popularityC1 > popularityC2:
                            c1.append(w)
                            c2.remove(w)
                            changed = True

                        if changed: break
                    if changed: break
                if changed: break

            if not changed: break

        # computing centremost elem of each cluster
        out = []
        for c in clusters:
            min_word = min(c, key=lambda x:self.getSumDistance(simG, c, x))
            out.append((c,min_word))
            
        if self.output: pprint(out)
        if self.output: self.displaySimG(simG)
        return out

    def getSumDistance(self, simG, c, w):
        out = 0
        for w1 in c:
            if w==w1: continue
            out += simG[w][w1]
        return out

    def initSimilarityGraph(self, db, ws):
        simG = dict()
        for w1 in ws:
            simG[w1] = dict()
            for w2 in ws:
                if w1!=w2:
                    simG[w1][w2] = 0
        return simG

    def getSimilarities(self, db, ws):
        simG  = self.initSimilarityGraph(db, ws)

        # first db is converted to a readable dataG
        # dataG initialisation follows
        dataG = dict()
        for w1 in ws:
            dataG[w1]=dict()
            for w2 in ws:
                if w1 == w2: continue
                dataG[w1][w2]={Dir.L: [0.5,0.5,0.5], Dir.R: [0.5,0.5,0.5]}

        # populating dataG
        for hType, dType, d in db:
            key = (hType, dType, d)
            dataG[hType][dType][d] = db[key]

        # for every word pair w1, w2
        for w1 in ws:
            for w2 in ws:
                if w1==w2: continue
                if self.output: print(f"{w1}-{w2}")
                distance = 0
                numdists = 0

                # get similarity - for all words w3 and dirs d: look at dict entries n average diff
                for w3 in ws:
                    if w3 in [w1,w2]: continue
                    for d in [Dir.L, Dir.R]:
                        # get percentage diff between all values
                        if self.output: print(f"\t{w3}\t{d}\t{list(filter(lambda x:x[0]!=0.5 or x[1]!=0.5, zip(map(lambda x:round(x,2), dataG[w1][w3][d]+dataG[w3][w1][d]), map(lambda x:round(x,2), dataG[w2][w3][d]+dataG[w3][w2][d]))))}")
                        for v1, v2 in zip(dataG[w1][w3][d]+dataG[w3][w1][d], dataG[w2][w3][d]+dataG[w3][w2][d]):
                            if v1==0.5 and v2==0.5: continue
                            elif v1==0.5 or v2==0.5:
                                distance +=2 # max possible distance
                                numdists +=1
                            else:
                                distance += abs(v1-v2)
                                numdists += 1

                similarity   = 0 if numdists==0 else 1-distance/numdists/2
                simG[w1][w2] = similarity
                simG[w2][w1] = similarity
                if self.output: print(f"\t{distance}\t{numdists}\t{similarity}")
        return simG

    def displaySimG(self, simG):
        # print("--------------------------------------------------------")
        # for w1 in simG:
        #     print(f"{w1}")
        #     for w2 in simG[w1]:
        #         print(f"\t{w2}\t{round(simG[w1][w2],2)}")

        G = nx.Graph()
        for u in simG:
            for v, w in simG[u].items():
                G.add_edge(u, v, weight=w)

        weights = [G[u][v]['weight'] for u, v in G.edges()]
        edge_widths = [w * 5 for w in weights]
        pos = nx.spring_layout(G)
        nx.draw(
            G,
            pos,
            with_labels=True,
            width=edge_widths,
            node_color='lightblue',
            edge_color='gray'
        )
        plt.show()

class Dir:
    L = 1
    R = 2
