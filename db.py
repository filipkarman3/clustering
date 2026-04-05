from TypeClusterer import TypeClusterer
from random import random
import math as maths

class DB:
    inittypevalgood = 5
    inittypevalbad  = 0
    typevalimprovement = 0.1
    typevalloss        = 0.95

    initnumdepval = 0.5
    numdepvalalpha = 0.1

    def __init__(self, clustering=False, clusters=None):
        self.words        = set()
        self.initWTT(clusters)
        self.typeInfo     = dict()
        self.reinforcementsSinceReshuffle = 0
        self.numReshuffles = 0
        self.clustering=clustering
        self.clusters=clusters

    def getReinforceThresh(self):
        return 2*maths.log(len(self.words))*(len(self.words)**2)

    def initWTT(self, clusters):
        self.wordsToTypes = dict()
        if clusters!=None:
            for c, w_centre in clusters:
                for w in c:
                    self.words.add(w)
                    if w not in self.wordsToTypes: self.wordsToTypes[w] = dict()
                    self.wordsToTypes[w][w_centre] = self.inittypevalgood
                    self.wordsToTypes[w][w]        = self.inittypevalbad

    def getType(self, w):
        if w not in self.wordsToTypes:
            self.words.add(w)
            self.wordsToTypes[w] = dict()
            self.wordsToTypes[w][w] = self.inittypevalbad

        d = self.wordsToTypes[w]
        # print(f"dict: {self.wordsToTypes[w]}, keys: {self.wordsToTypes[w].keys()}, values: {self.wordsToTypes[w].values()}")
        return self.choose(list(zip(d.keys(),d.values())))

    def choose(self, options):
        # print(f"Softmax from {options}")
        # scores = list(map(lambda x:maths.exp(x[1]), options))
        max_val = max(x[1] for x in options)
        scores = [maths.exp(x[1] - max_val) for x in options]
        tot = sum(scores)
        thresh = random()*tot
        s = 0
        for option, score in zip(map(lambda x:x[0], options), scores):
            s += score
            if s > thresh:
                # print(option)
                return option
        # print(f"options: {list(options)}, scores: {scores}, tot: {tot}, thresh: {thresh}, s: {s}")

    def get(self, hType, dType, d):
        key = (hType, dType, d)
        if key not in self.typeInfo:
            self.typeInfo[key] = [self.initnumdepval]*3
        return self.typeInfo[key]

    def reinforce(self, word, key, n, val):
        self.reinforcementsSinceReshuffle += 1
        l = self.get(key[0], key[1], key[2])
        # print(f"reinforcing {word} | key: {key} | n: {n} | val: {val} | l: {l}")
        l[n] = self.numdepvalalpha*val + (1-self.numdepvalalpha)*l[n]
        self.typeInfo[key] = l
        self.reinforceTypeAssignment(word, key[0], val>0)

        if self.reinforcementsSinceReshuffle>self.getReinforceThresh() and self.clustering:
            self.reshuffle()

    def reinforceTypeAssignment(self, word, t, correct):
        if word not in self.wordsToTypes: self.wordsToTypes[word] = dict()
        if t not in self.wordsToTypes[word]:
            self.wordsToTypes[word][t] = self.inittypevalgood
        if correct:
            self.wordsToTypes[word][t] += self.typevalimprovement
        else:
            self.wordsToTypes[word][t] *= self.typevalloss

    def output(self):
        old = None
        for key in sorted(self.typeInfo):
            if old != key[0]:
                print(key[0])
                old = key[0]
            vals = self.typeInfo[key]
            f = 'NA' if all(lambda x:x==self.initnumdepval, vals) else max([0,1,2], key=lambda x:float('-inf') if vals[x]==0.5 else vals[x])
            if key[2] == Dir.R:
                print(f"\t{key[1]}\t->\t{f}\t{list(map(lambda x:round(x,2), vals))}")
            else:
                print(f"\t{key[1]}\t<-\t{f}\t{list(map(lambda x:round(x,2), vals))}")

        print("----------------------------------------------------")
        for w in self.wordsToTypes:
            newD = dict()
            for k in self.wordsToTypes[w]:
                newD[k] = round(self.wordsToTypes[w][k],2)
            print(f"{w}\t{newD}")

        print("----------------------------------------------------")
        # TypeClusterer(output=False).cluster(self.typeInfo, self.words)
        print(f"Num reshuffles: {self.numReshuffles}")

        if self.clusters!=None:
            print("##### initial clusters #####")
            for c in self.clusters:
                print(c)

    def reshuffle(self):
        self.reinforcementsSinceReshuffle = 0
        self.numReshuffles += 1

        # create dict for ez access
        clusterDict = dict()
        clustering = TypeClusterer(output=False).cluster(self.typeInfo, self.words)
        print()
        for c, cw in clustering:
            print(cw,c)
            for w in c:
                clusterDict[w] = cw

        # for every word
            # for every type
                # centre of cluster takes on old value
                # old value factored 0.75
        for w in self.words:
            ts = self.wordsToTypes[w]
            to_add = []
            for t in ts:
                if clusterDict[t]!=t:
                    to_add.append((clusterDict[t],ts[t]))
                    ts[t]*=0.75
            for k,v in to_add: ts[k]=v

            # keep top 3
            selfval = self.wordsToTypes[w][w]
            self.wordsToTypes[w] = dict(sorted(ts.items(), key=lambda x:x[1], reverse=True)[:3])
            self.wordsToTypes[w][w] = selfval # keep [w][w] if it gets removed

def all(f, l):
    return len(list(filter(f,l)))==len(l)

class Dir:
    L = 1
    R = 2