import db as dbfile
from db import Dir
from enum import Enum

class Word:
    def __init__(self, name, source_db):
        self.name = name
        self.t = source_db.getType(name)
        self.db = dict()

    def get_improvement_value(self, dType, d, source_db):
        # assign numdeps and values if it doesn't exist in local db yet
        key = (dType, d)
        if key not in self.db:
            self.db[key] = (0, source_db.get(self.t, dType, d))
        
        # cannot have more than 2 deps in a dir of one type
        n, l = self.db[key]

        # print(f"considering adding dep {self.t}->{dType}. There are currently {n} of these from this word | l: {l} | ",end='')
        if n >= 2: return float('-inf')

        # find the optimum num deps and its utility
        optimumnumdeps = -1
        maxutility     = float('-inf')
        for i in range(3):
            if l[i]>maxutility:
                maxutility = l[i]
                optimumnumdeps = i

        # generate score based on that
        if optimumnumdeps < n+1:
            return l[n+1] - maxutility
        else:
            return maxutility-l[n]

    def __repr__(self):
        return self.t

    def __str__(self):
        return self.t

    def increment_dependency_count(self, dType, d, source_db):
        # print(f"Adding dep {self.t}->{dType} ({d}) ",end='')
        key = (dType, d)
        if key not in self.db:
            # print("| Nonexistent, initiating ", end='')
            self.db[key] = (0, source_db.get(self.t, dType, d))
        n, l = self.db[key]
        self.db[key] = (n+1, l)
        # print(f"| New val: {self.db[key]}")

    def get_num_dep_type(self, dType, d, source_db):
        # print(f"Getting num of {self.t}->{dType} ({d}) relations ", end='')
        key = (dType, d)
        if key not in self.db:
            self.db[key] = (0, source_db.get(self.t, dType, d))
            # print(f"(nonexistent for key {key}) ", end='')
        n, _ = self.db[key]
        # print(f"{n}")
        return n