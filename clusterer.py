from pprint import pprint

class Clusterer:
    threshold     = 0.9
    consensus     = 0.7

    def __init__(self, cfg):
        self.cfg = cfg
        self.db  = dict()
        self.ws  = set()

    def cluster(self, num_sentences):
        self.num_sentences = num_sentences
        self.computeLinkStrengths()
        simG     = self.computeSimilarityGraph()
        clusters = [[w] for w in self.ws]
        toAdd    = []

        # pprint(simG)

        while True:
            changed   = False
            clusters += toAdd # !!!?
            toAdd     = []
            clusters  = list(filter(lambda x:len(x)>0, clusters))
            
            for i in range(len(clusters)):
                c1 = clusters[i]
                if len(c1)==0: continue
                # !!! can this be made into a >i cond?
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
        # return list(filter(lambda x:len(x)>0, clusters))

        # computing centremost elem of each cluster
        out = []
        for c in clusters:
            min_word = min(c, key=lambda x:self.getSumDistance(simG, c, x))
            out.append((c,min_word))
            
        # pprint(out)
        return out

    def getSumDistance(self, simG, c, w):
        out = 0
        for w1 in c:
            if w==w1: continue
            out += simG[w][w1]
        return out

    def computeSimilarityGraph(self):
        freqG = self.computeFrequencyGraph()
        adjMat = self.adjMatInit()
        for w1 in self.ws:
            for w2 in self.ws:
                if w1 > w2:
                    v = self.computeSimilarity(w1,w2,freqG)
                    adjMat[w1][w2]=v
                    adjMat[w2][w1]=v

        # pprint(freqG)
        # print("--------------------------------------")
        # pprint(adjMat)
        # print("--------------------------------------")
        return adjMat

    def computeSimilarity(self, w1, w2, freqG):
        sumDistances = 0
        # print("----------------------------------")
        # print(f"{w1} | {freqG[w1]}")
        # print(f"{w2} | {freqG[w2]}")
        for w3 in self.ws.difference([w1,w2]):
            v1 = freqG[w1][w3]
            v2 = freqG[w2][w3]
            if v1==0 and v2==0:
                distance = 0
            elif min(v1,v2)==0:
                distance = 1
            else:
                    distance = (max(v1,v2)-min(v1,v2))/min(v1,v2)
            # print(f"{w3} | {distance}")
            sumDistances+=distance
        # print(f"{w1}-{w2} | {1-(sumDistances/(len(self.ws)-2))}")
        return 1-(sumDistances/(len(self.ws)-2))

    def computeFrequencyGraph(self):
        adjMat = self.adjMatInit()
        for w1, w2 in self.db:
            adjMat[w1][w2] = self.db.get((w1,w2),0)
        return adjMat

    def adjMatInit(self):
        adjMat = dict()
        for w1 in self.ws:
            adjMat[w1] = dict()
            for w2 in self.ws:
                if w1!=w2:
                    adjMat[w1][w2] = 0
        return adjMat

    def computeLinkStrengths(self):
        for _ in range(self.num_sentences):
            sentence = self.cfg.generate_sentence('S')
            for i in range(len(sentence)-1):
                for j in range(i,len(sentence)):
                    self.increment(sentence[i],sentence[j])
    
    def increment(self, w1, w2):
        self.ws.add(w1)
        self.ws.add(w2)

        if w1!=w2:
            key = (w1,w2)
            if key not in self.db: self.db[key] = 0
            self.db[key] += 1