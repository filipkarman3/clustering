# -*- coding: utf-8 -*-
"""
Created on Fri Sep  5 16:38:12 2025

@author: anjo1309
"""

# --- Minimal stubs for types and chunks ---
class Type:
    def __init__(self, name):
        self.name = name
    def __eq__(self, other):
        return isinstance(other, Type) and self.name == other.name
    def __repr__(self):
        return f"Type({self.name})"
    def is_expecting_after(self):
        # Example: Types ending with "/N" expect after
        return "/N" in self.name
    def is_expecting_before(self):
        # Example: Types starting with "S/" expect before
        return self.name.startswith("S/")
    def right_type(self):
        # For simplicity, assume after "/" is right_type
        return self.name.split("/")[-1] if "/" in self.name else self.name
    def left_type(self):
        return self.name.split("/")[0] if "/" in self.name else self.name

class TChunk:
    def __init__(self, structure):
        self.structure = structure  # can be a Type or list of Types
    def reduce(self):
        # Simplified: just take the last Type for reduction
        if isinstance(self.structure, list):
            return self.structure[-1]
        return self.structure
    def has_empty_elements(self):
        return False
    def is_consistent(self):
        return True
    def __repr__(self):
        return f"TChunk({self.structure})"

class SChunk:
    def __init__(self, chunk):
        self.chunk = chunk

class ChunkPair:
    def __init__(self, s1, s2):
        self.s1 = s1
        self.s2 = s2

# --- Minimal stub for LTM ---
class LTM:
    def __init__(self):
        self.chunk_type_associations = {}
    def get_value(self, chunk):
        # Always return 1.0 for testing
        return 1.0

# --- Working memory stub ---
class WM:
    def __init__(self):
        self.ts1 = None
        self.ts2 = None

# --- Learner stub ---
class Learner:
    def __init__(self):
        self.wm = WM()
        self.ltm = LTM()
        self.n_reinf = 0

    # Example softmax_choice
    def softmax_choice(self, candidates, tau=1.0):
        # deterministic pick of max for now
        return max(candidates, key=candidates.get)

    # Minimal stub for get_z_values_type
    def get_z_values_type(self, pair):
        return [0.3, 0.7]  # example values

    # Minimal stub for modify_expectation_at_level
    def modify_expectation_at_level(self, ts, index, new_type, side="right"):
        # Just return new_type for testing
        return new_type

    # Minimal stub for split_top_level
    def split_top_level(self, ts, new_type):
        return ts  # return unchanged for testing

    # Minimal stub for extract_bad_types
    def extract_bad_types(self, chunk):
        return []

    # Minimal stub for extract_good_types
    def extract_good_types(self, chunk):
        return []

    # The function under test
    def correct_typings(self, pair: ChunkPair):
        ts1 = self.wm.ts1
        ts2 = self.wm.ts2
        
        if not ts1.has_empty_elements() and not ts2.has_empty_elements():
            t1 = ts1.reduce() if isinstance(ts1.structure, list) else ts1.structure
            t2 = ts2.structure
            if t1.is_expecting_after() and not t2.is_expecting_before():
                t1_r = Type(t1.right_type())
                if t1_r != t2:
                    z_values = self.get_z_values_type(pair)
                    winner_index = self.softmax_choice({i:z for i,z in enumerate(z_values)})
                    winner_value = z_values[winner_index]
                    value_ts2 = self.ltm.get_value(ts2)
                    dominant_side = self.softmax_choice({'s1': winner_value, 's2': value_ts2})
                    if dominant_side == 's2':
                        new_ts1 = self.modify_expectation_at_level(ts1, winner_index, t2, side="right")
                        self.wm.ts1 = TChunk(new_ts1)
                        self.wm.ts2 = TChunk(t2)
                    else:
                        self.wm.ts2 = TChunk(t1_r)
        return self.wm.ts1, self.wm.ts2

# --- Example test ---
if __name__ == "__main__":
    # Compound s1, single s2
    s1 = TChunk([Type("N"), Type("S/N")])
    s2 = TChunk(Type("N"))
    pair = ChunkPair(s1, s2)

    learner = Learner()
    learner.wm.ts1 = s1
    learner.wm.ts2 = s2

    ts1_out, ts2_out = learner.correct_typings(pair)
    print("Output ts1:", ts1_out)
    print("Output ts2:", ts2_out)
    
    
if __name__ == "__main__":
    learner = Learner()

    # Case 1: Compound s1, single s2
    s1 = TChunk([Type("N"), Type("S/N")])   # s1 is compound
    s2 = TChunk(Type("N"))                  # s2 is single
    pair = ChunkPair(s1, s2)
    learner.wm.ts1, learner.wm.ts2 = s1, s2
    print("Case 1 (compound s1, single s2):", learner.correct_typings(pair))

    # Case 2: Single s1, single s2
    s1 = TChunk(Type("S/N"))
    s2 = TChunk(Type("N"))
    pair = ChunkPair(s1, s2)
    learner.wm.ts1, learner.wm.ts2 = s1, s2
    print("Case 2 (single s1, single s2):", learner.correct_typings(pair))

    # Case 3: Single s1, compound s2
    s1 = TChunk(Type("N"))
    s2 = TChunk([Type("S/N"), Type("N")])   # s2 is compound
    pair = ChunkPair(s1, s2)
    learner.wm.ts1, learner.wm.ts2 = s1, s2
    print("Case 3 (single s1, compound s2):", learner.correct_typings(pair))

    # Case 4: Both compound
    s1 = TChunk([Type("N"), Type("S/N")])
    s2 = TChunk([Type("S/N"), Type("N")])
    pair = ChunkPair(s1, s2)
    learner.wm.ts1, learner.wm.ts2 = s1, s2
    print("Case 4 (both compound):", learner.correct_typings(pair))