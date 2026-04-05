
from typing import Any, Union, List
from copy import deepcopy

def flatten(lst: List[Any]) -> List[Any]:
    flat_list = []
    for item in lst:
        if isinstance(item, list):
            flat_list.extend(flatten(item))
        else:
            flat_list.append(item)
    return flat_list


class ChunkPair:
    _cache = dict()  # Class-level cache

    def __new__(cls, couple):
        s1, s2 = couple
        key = (s1, s2)  # This assumes s1 and s2 are hashable and support equality

        if key in cls._cache:
            return cls._cache[key]
        else:
            instance = super().__new__(cls)
            cls._cache[key] = instance
            return instance

    def __init__(self, couple):
        # Prevent reinitialization if already initialized (due to caching in __new__)
        if hasattr(self, 's1') and hasattr(self, 's2'):
            return
        self.s1 = couple[0]
        self.s2 = couple[1]

    def get_sub_couples(self):
        sub_pairs = [self]
        try:
            subchunks = self.s1.get_right_subchunks2(0)
            for s in subchunks:
                sub_pairs.append(ChunkPair((s, self.s2)))
        except ValueError:
            pass  # s1 has no internal structure, return only the pair itself
        return sub_pairs

    def __hash__(self):
        return hash((self.s1, self.s2))

    def __eq__(self, other):
        return isinstance(other, ChunkPair) and self.s1 == other.s1 and self.s2 == other.s2

    def __repr__(self):
        return f"({self.s1},{self.s2})"



class SChunk:
    _cache = {}  # Cache to store unique chunks by their normalized structure

    def __new__(cls, structure: Union[List[Any], Any]) -> 'SChunk':
        # Normalize the structure to avoid duplication in cache
        normalized = cls._normalize(structure)

        # If the normalized structure already exists in the cache, return the cached object
        if normalized in cls._cache:
            return cls._cache[normalized]

        # Create a new instance if not found in the cache
        instance = super().__new__(cls)
        instance.structure = structure
        instance._normalized = normalized
        #instance.depth = instance._compute_depth()
        
        # Store the instance in cache to avoid future duplications
        cls._cache[normalized] = instance
        return instance

    @staticmethod
    def _normalize(structure: Union[List[Any], Any]) -> tuple:
        """Generate a normalized representation of the structure as a hashable tuple."""
        if isinstance(structure, list):
            return tuple(SChunk._normalize(s) for s in structure)  # recursively normalize the list
        return (structure,)  # wrap non-list elements in a tuple

    def __repr__(self) -> str:
        return f"{self.structure}"

    def __hash__(self):
        return hash(self._normalized)  # hash based on normalized structure

    def __init__(self, structure: Union[List[Any], Any]):
        """Ensure non-leaf chunks have exactly 2 subchunks."""
        if isinstance(structure, list):
            if len(structure) != 2:
                raise ValueError("Each non-leaf chunk must have exactly two subchunks.")
        self.structure = structure
        #self.depth = self._compute_depth()
    
    @property
    def depth(self) -> int:
        """Computes the depth of the rightmost path (rightmost branch)."""
        count = 0
        node = self.structure
        while isinstance(node, list):
            node = node[-1]  # always go right
            count += 1
        return count

    def get_left(self) -> 'SChunk':
        """Returns the left subchunk if it's a valid list structure."""
        if isinstance(self.structure, list):
            return SChunk(self.structure[0])
        else:
            raise ValueError("This chunk doesn't have a left part because its structure is not a list.")

    def get_right(self) -> 'SChunk':
        """Returns the right subchunk if it's a valid list structure."""
        if isinstance(self.structure, list):
            return SChunk(self.structure[1])
        else:
            raise ValueError("This chunk doesn't have a right part because its structure is not a list.")

    def get_right_subchunks(self, depth: int) -> List['SChunk']:
        """Returns a list of right subchunks at each depth."""
        subchunks = []
        current = self.structure
        for _ in range(depth):
            if not isinstance(current, list):
                raise ValueError("Reached a non-list structure while trying to access subchunks.")
            current = current[-1]  # Go right
            subchunks.append(SChunk(current))
        return subchunks
    
    def get_right_subchunks2(self, depth: int) -> List[Any]:
        """Returns a list of right subchunks at each depth starting from the specified depth."""
        subchunks = []
        current = self.structure
        current_depth = 0
    
        # First, navigate to the specified depth
        while current_depth < depth + 1:
            if not isinstance(current, list):
                raise ValueError(f"Cannot reach depth {depth} as the structure does not have enough depth.")
            current = current[-1]  # Go right
            current_depth += 1
    
        # Now, collect subchunks starting from the specified depth, going down the rightmost branch
        while isinstance(current, list):
            subchunks.append(SChunk(current))
            current = current[-1]  # Go rightmost (last element in the list)

        # Append the final element if it's not a list
        subchunks.append(SChunk(current))
    
        # If the specified depth is larger than the depth of the chunk structure, raise an exception
        if current_depth > self.depth:
            raise ValueError(f"The given depth {depth} exceeds the maximum depth of the structure.")
    
        return subchunks

    def chunk_at_depth(self, other, depth=0) -> 'SChunk':
        """Returns a new chunk with the other chunk at a specified depth."""
        nested_list = deepcopy(self.structure)
        if depth == 0:
            struct = [nested_list, other.structure]
            return SChunk(struct)
        else:
            self._modify_element_at_depth(nested_list, depth, other.structure)
            return SChunk(nested_list)

    def flatten_structure(self) -> List[Any]:
        """Flattens the structure recursively."""
        if isinstance(self.structure, list):
            return flatten(self.structure)
        else:
            return [self.structure]
        

    def __len__(self) -> int:
        """Returns the number of leaf elements in the structure."""
        if isinstance(self.structure, list):
            return len(self.flatten_structure())
        else:
            return 1

    @staticmethod
    def _modify_element_at_depth(nested_list: List[Any], depth: int, new_value: Any):
        current = nested_list
        for _ in range(depth - 1):
            current = current[-1]
        current[-1] = [current[-1], new_value]

testing = False
if testing:
    # Simple leaf chunks
    a = SChunk("A")
    b = SChunk("B")
    print(a.flatten_structure())
    
    print("a:", a)
    print("b:", b)
    
    # Create a binary chunk (a, b)
    ab = SChunk([a.structure, b.structure])
    print("ab:", ab)
    
    # Create same structure again
    ab_duplicate = SChunk([a.structure, b.structure])
    print("ab_duplicate:", ab_duplicate)
    
    # ✅ Identity check due to caching
    print("ab is ab_duplicate:", ab is ab_duplicate)  # True
    
    # Create deeper nested chunk: ((A, B), A)
    aba = ab.chunk_at_depth(a, depth=0)
    print("aba:", aba)
    
    # Add a chunk at depth 1 (modifies deepest element)
    abb = ab.chunk_at_depth(b, depth=1)
    print("abb (chunked at depth 1):", abb)
    
    # Flattening a structure
    print("Flattened aba:", aba.flatten_structure())
    
    # Length (number of leaf elements)
    print("Length of aba:", len(aba))  # Should be 3: A, B, A
    
    # Access subchunks
    print("Left of ab:", ab.get_left())     # Should be A
    print("Right of ab:", ab.get_right())   # Should be B
    
    # Get right-side nested subchunks from a deeper chunk
    print("Right subchunks in aba (depth 1):")
    for i, ch in enumerate(abb.get_right_subchunks2(0)):
        print(f"  Depth {i+1}:", ch)
    
    
    a = SChunk("A")
    print(len(a))
    b = SChunk("B")
    ab = SChunk([a.structure, b.structure])
    abc = ab.chunk_at_depth(b, depth=1)
    
    print("Depth of a:", a.depth)        # 0
    print("Depth of ab:", ab.depth)      # 1
    print("Depth of abc:", abc.depth)    # 2
    
    pair = ChunkPair((abc,b))
    print(pair.s1)
    print(pair.s2)
    print(pair.get_sub_couples())
