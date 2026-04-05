# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 11:21:27 2023

@author: jmd01
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 20:22:29 2023

@author: jmd01
"""

import re
#import json
#from json import JSONEncoder
import copy
from itertools import accumulate
from random import random




def modify_element_at_depth(nested_list, depth, new_value):
    for i in range(depth-1):
        nested_list = nested_list[-1]
    nested_list[-1] = [nested_list[-1],new_value]
    
def change_element_at_depth(nested_list, depth, new_value):
    for i in range(depth-1):
        nested_list = nested_list[-1]
    nested_list[-1] = [new_value]
    
def flatten(lst):
    flat_list = []
    for item in lst:
        if isinstance(item, list):
            flat_list.extend(flatten(item))
        else:
            flat_list.append(item)
    return flat_list

def add_weights(b_values1,b_values2):
    a = copy.deepcopy(b_values1)
    b = copy.deepcopy(b_values2)
    l = sorted((a, b), key=len)
    c = l[1].copy()
    c[:len(l[0])] += l[0]
    return c

class Type:
    # create a cache to store instances of the Type class
    cache = {}
    prim_ID = 1
    
    EMPTY = None
    SENTENCE = None
    
    # override the __new__ method to check the cache for an existing instance
    def __new__(cls, formula):
        
        # check if the key is in the cache
        if formula in cls.cache:
            # if the key is in the cache, return the corresponding instance
            return cls.cache[formula]
        else:
            # if the key is not in the cache, create a new instance
            instance = super().__new__(cls)
            # store the new instance in the cache
            cls.cache[formula] = instance
            # return the new instance
            return instance
    
    # initialize the instance with its formula
    def __init__(self, formula):
        self.formula = formula

    @staticmethod
    def create_primitive_type():
        tt = Type( str(Type.prim_ID))
        Type.prim_ID += 1
        return tt
        
    def __hash__(self):
        return hash((self.formula))
        
    # define the string representation of the instance
    def __repr__(self):
        string = self.formula.replace('o','/')
        string = string.replace('u','\\')
        return 'tc_'+string    
    
    def __eq__(self, other):
        return self is other
    
    def split(self, pu=0.5, prim='New', bad_s1=None, bad_s2=None):
        """Splits the Type into two subtypes based on a probability.
    
        Args:
            pu (float): Probability to split by 'u' vs 'o'.
            preferred_prim (Type or str): Primitive type to use, or 'New'.
            bad_s1 (list of Type): Types not allowed on left split.
            bad_s2 (list of Type): Types not allowed on right split.

        Returns:
            list of Type: Two resulting Types after split.
        """
        def get_new_primitive(bad_list):
            index = 0
            while Type(str(index)) in bad_list:
                index += 1
            return Type(str(index))

        # Determine which side to prioritize
        use_u_split = random() < pu

        # Handle preferred primitive
        if isinstance(prim, Type) and prim.is_primitive():
            prim_type = prim
        else:
            prim_type = None  # will generate new if needed

        # Adjust primitive choice if it's invalid
        if use_u_split:
            if prim_type and bad_s1 and prim_type in bad_s1:
                prim_type = None
            if prim_type is None:
                prim_type = get_new_primitive(bad_s1 if bad_s1 else [])
            return [prim_type, Type(prim_type.formula + "u" + self.formula)]
        else:
            if prim_type and bad_s2 and prim_type in bad_s2:
                prim_type = None
            if prim_type is None:
                prim_type = get_new_primitive(bad_s2 if bad_s2 else [])
            return [Type(self.formula + "o" + prim_type.formula), prim_type]
    
    def is_start(self): # Checks whether the type is expecting something on the left. 
        return len(self.left_compatible_chunks()) == 0
    

    def get_primitives(self):
        return re.split(r"u|o",self.formula)
    
    def __len__(self):
        return len(self.get_primitives())
    
    def is_expecting_before(self):
        if self.left_compatible_chunks():
            return True
        else:
            return False

    def is_expecting_after(self):
        if self.right_compatible_chunks():
            return True
        else:
            return False
    
    
    def left_compatible_chunks(self):
        #substrings = re.findall(r".*?u", self.formula)
        substrings = re.findall(r"^"+self.left_type()+"u",self.formula)
        substrings = list(accumulate(substrings))
        #print(substrings)
        substrings = [re.sub(r"u$", "$", x) for x in substrings]
        #print(substrings)
        substrings1 = [re.sub(r"^", r"^", x) for x in substrings]
        #print(substrings1)
        substrings2 = [re.sub(r"^", r"u", x) for x in substrings]
        #print(substrings2)
        return substrings1 + substrings2
    
    def right_compatible_chunks(self):
        #substrings = re.findall(r".*?o", self.formula[::-1])
        substrings = re.findall(r"o"+self.right_type()+"$",self.formula)
        substrings = list(accumulate(substrings))
        substrings = [re.sub(r"^o", "", x) for x in substrings]
        substrings1 = [re.sub(r"^", r"^", x) for x in substrings]
        substrings2 = [re.sub(r"$", r"o", x) for x in substrings1]
        substrings1 = [re.sub(r"$", r"$", x) for x in substrings1]
        return substrings1 + substrings2
    
    def is_empty(self):
        return self is Type.EMPTY
        #return len(self.get_primitives()) == 1 and len(self.get_primitives()[0])==0
    
    
    def is_primitive(self):
        if len(self.get_primitives()) == 1 and not self.is_empty():
            return True
        else:
            return False
        #return (len(self.right_compatible_chunks()) + len(self.left_compatible_chunks())) == 0
    
    def left_type(self):
        primitives = self.get_primitives()
        return primitives[0]
    
    def right_type(self):
        primitives = self.get_primitives()
        return primitives[-1]
    
    def is_right_compatible(self, other):
        for i, pattern in enumerate(self.right_compatible_chunks()):
            #print(pattern)
            match = re.search(pattern, other.formula)
            if match:
                return True, pattern
        return False, None
    
    def is_left_compatible(self, other):
        for i, pattern in enumerate(other.left_compatible_chunks()):
            #print(pattern)
            match = re.search(pattern, self.formula)
            if match:
                return True, pattern
        return False, None
    
    def is_compatible(self, other):
        return self.is_left_compatible(other)[0] or self.is_right_compatible(other)[0]

    
    def __add__(self, other):
        if self.is_left_compatible(other)[0]:
            #print('left_compatible')
            pattern = self.is_left_compatible(other)[1][:-1]
            if pattern.startswith("^"):
                l = len(pattern)
                return Type(other.formula[l:])
            elif pattern.startswith("u"):
                l = len(pattern)
                return Type(self.formula[:-l+1]+other.formula[l:])
            else:
                print('Problem here.')
        elif self.is_right_compatible(other)[0]:
            #print('right_compatible')
            pattern = self.is_right_compatible(other)[1][1:]
            if pattern.endswith("$"):
                l = len(pattern)
                return Type(self.formula[:-l])
            elif pattern.endswith("o"):
                l = len(pattern)
                return Type(self.formula[:-l+1]+other.formula[l:])
            else:
                print('Problem here.')
        else:
            raise TypeError("Incompatible types")
            
    @staticmethod
    def reduce(types):
        remaining_types = types[:]
        
        # keep trying to reduce the list of types until it contains only one type
        while len(remaining_types) > 1:
            # set the reduced flag to False
            reduced = False
            
            # iterate over the remaining types
            for i, type1 in enumerate(remaining_types[:-1]):
                type2 = remaining_types[i+1]
                # if the two types are compatible, reduce them and update the reduced flag
                if type1.is_compatible(type2):
                    remaining_types[i] = type1 + type2
                    del remaining_types[i+1]
                    reduced = True
                    break
        
            # return the remaining type
            if not reduced:
                return remaining_types
        
        return remaining_types
    
    @staticmethod
    def is_sentence(types):
        remaining_types = Type.reduce(types)
        if len(remaining_types) == 1 and remaining_types[0] == Type.SENTENCE:
            return True
        else:
            return False

Type.EMPTY = Type('')
Type.SENTENCE = Type('0')


class TChunk():
    
    def __init__(self, structure):
        self.structure = structure
        #self.type_dic = {}
        self.depth = self.get_depth()
        
    def __repr__(self):
        return str(self.structure)
    
    def __hash__(self):
        return hash(str(self.structure))
    
    def get_left(self):
        [s1,s2] = self.structure
        s1 = TChunk(s1)
        s2 = TChunk(s2)
        return s1
    
    def get_right(self):
        [s1,s2] = self.structure
        s1 = TChunk(s1)
        s2 = TChunk(s2)
        return s2
    
    def get_right_subchunks(self, depth):
        right_subchunks = [self]
        nested_list = self.structure[:]
        for d in range(depth):
            nested_list = nested_list[-1]
            right_subchunks.append(TChunk(nested_list))
        return right_subchunks
    
    @staticmethod
    def from_list_and_responses(list_of_types, responses):
        if len(list_of_types) != len(responses)+1:
            print('mismatch of length')
        else:
            tc1 = TChunk(list_of_types[0])
            for i in range(len(responses)):
                tc2 = TChunk(list_of_types[i+1])
                tc1 = tc1.chunk_at_depth(tc2,depth=tc1.depth+1-responses[i])
             # Here I need to construct a TChunk based on the corresponding responses
        return tc1
    
    def chunk_at_depth(self, other, depth=0):
        if type(self.structure)== Type:
            nested_list = self.structure
        else:
            nested_list = self.structure[:]
        
        if depth == 0:
            return TChunk([nested_list,other.structure])
        else:
            modify_element_at_depth(nested_list, depth, other.structure)
            return TChunk(nested_list)
    
    def get_depth_old(self):
        st = str(self.structure)
        match = re.search("]*$",st)
        return len(match.group(0))
    
    def get_depth(self):
        structure = self.structure
        depth = 0
        while isinstance(structure, list) and len(structure) == 2:
            structure = structure[1]  # Always move to the right
            depth += 1
        return depth
    



    
    def remove_structure(self):
        if type(self.structure) is Type:
            return str(self.structure)
        else:
            return flatten(self.structure)
        
    def remove_structure2(self):
        if type(self.structure) is Type:
            return [self.structure]
        else:
            return flatten(self.structure)
        

    def is_consistent_gpt(self):
        if isinstance(self.structure, Type):
            return True
    
        left_chunk = TChunk(self.structure[0])
        right_chunk = TChunk(self.structure[1])
    
        if not left_chunk.is_consistent_gpt() or not right_chunk.is_consistent_gpt():
            return False
    
        left_type = left_chunk.reduce_gpt()
        right_type = right_chunk.reduce_gpt()
    
        return left_type.is_compatible(right_type)

        
    def reduce(self):
        if type(self.structure) != list:
            return self.structure
        else:
            [s1,s2] = self.structure[:]
            s1 = TChunk(s1)
            s2 = TChunk(s2)
            if type(s1.structure) == Type and type(s2.structure)== Type:
                result = s1.structure + s2.structure
                return result
            elif type(s1.structure) != Type and type(s2.structure)== Type:
                result = s1.reduce() + s2.structure
                # Weird bug fixed by the following line: if more than one element reduce to 0, creates bug...
                self = TChunk([s1.structure,s2.structure])
                return result
            elif type(s1.structure) == Type and type(s2.structure)!= Type:
                result = s1.structure + s2.reduce()
                # Weird bug fixed by the following line: if more than one element reduce to 0, creates bug...
                self = TChunk([s1.structure,s2.structure])
                return result
            else:
                t1 = s1.reduce()
                t2 = s2.reduce()
                result = t1 + t2
                # Weird bug fixed by the following line: if more than one element reduce to 0, creates bug...
                self = TChunk([s1.structure,s2.structure])

                return result
     
    def is_sentence(self):
        return self.reduce() == Type.SENTENCE               
        
    def is_consistent(self):
        if type(self.structure) != list:
            return True
        else:
            [s1,s2] = self.structure[:]
            s1 = TChunk(s1)
            s2 = TChunk(s2)

            if type(s1.structure) == Type and type(s2.structure)== Type:
                return s1.structure.is_compatible(s2.structure)
            elif type(s1.structure) != Type and type(s2.structure)== Type:
                if s1.is_consistent():
                    return s1.reduce().is_compatible(s2.structure)
                else:
                    return False
            elif type(s1.structure) == Type and type(s2.structure)!= Type:
                if s2.is_consistent():
                    return s1.structure.is_compatible(s2.reduce())
                else:
                    return False
            else:
                if s1.is_consistent() and s2.is_consistent():
                    return s1.reduce().is_compatible(s2.reduce())
                else:
                    return False
    
    def find_type_to_modify(self):
        if self.is_consistent() and self.reduce().is_expecting_after():
            expected_type = Type(self.reduce().right_type())
            for i, t in enumerate(self.right_types()):
                
                if t.is_expecting_after() and Type(t.right_type())==expected_type:
                    return i, self.remove_structure2()[-(i+1)]
                
    def modified_element(self,new_expectation):
        if self.is_consistent() and self.reduce().is_expecting_after():
            expected_type = Type(self.reduce().right_type())
            right_types = self.right_types()
            right_types.reverse()
            #print(f'In modified element, right_types is {right_types}')
            for i,t in enumerate(right_types):
                if t.is_expecting_after() and Type(t.right_type()) == expected_type:
                    new_type = t + expected_type
                    [new_type,_] = new_type.split(pu=0, prim=new_expectation)
                    right_types[i] = new_type
            
            #print(f'In modified element, modified right_types is {right_types}')
            
            # for i in range(len(right_types)-1):
            #     if len(right_types[i+1])>len(right_types[i]):
            #         [_,new_type]=right_types[i].split(pu=1,prim=right_types[i+1])
            #     else:
            #         [new_type,_]=right_types[i].split(pu=0,prim=right_types[i+1])
            return new_type
            
    
    def right_types(self):
        # Only works if TChunk is consistent!!!
        list_of_reduced_types = []
        if not isinstance(self.structure, list):
            return [self.structure]
        
        for chunk in self.get_right_subchunks(self.depth):
            list_of_reduced_types.append(chunk.reduce())
        list_of_reduced_types.reverse()
        return list_of_reduced_types
    
    
    
    def has_empty_elements(self):
        flat = self.remove_structure2()
        if Type.EMPTY in flat:
            return True
        else:
            return False
        
    def retype_expectation(self,typ,responses):
        if self.is_consistent() and self.reduce().is_expecting_after():
            list_of_types = self.remove_structure2()
            #print(f'list of types: {list_of_types}')
            chunktree = ChunkTree.from_tchunk(self)
            #print(f'list of types after chunktree creation: {list_of_types}')
            (index, old_type) = self.find_type_to_modify()
            #print(f'the old type is {old_type}')
            new_type = self.modified_element(typ)
            #print(f'Should be replaced by {new_type}')
            list_of_types[-(index+1)] = new_type
            new_ts1 = TChunk.from_list_and_responses(list_of_types, responses)
            #print(f'new list of types: {list_of_types}')
            #new_ts1 = chunktree.apply_types(list_of_types) # The apply_types function only works for ts1 of length 2, more complex structure fail to construct a TChunk with the correct internal structure
            return new_ts1
        
class VChunk():
    
    def __init__(self, structure: float):
        self.structure = structure
        #self.type_dic = {}
        self.depth = self.get_depth()
        
    def __repr__(self):
        return str(self.structure)
    
    def __hash__(self):
        return hash(str(self.structure))
    
    def get_left(self):
        [s1,s2] = self.structure
        s1 = VChunk(s1)
        s2 = VChunk(s2)
        return s1
    
    def get_right(self):
        [s1,s2] = self.structure
        s1 = VChunk(s1)
        s2 = VChunk(s2)
        return s2
    
    @staticmethod
    def from_list_and_responses(list_of_values, responses):
        if len(list_of_values) != len(responses)+1:
            print('mismatch of length')
        else:
            tc1 = VChunk(list_of_values[0])
            for i in range(len(responses)):
                tc2 = VChunk(list_of_values[i+1])
                tc1 = tc1.chunk_at_depth(tc2,depth=tc1.depth+1-responses[i])
             # Here I need to construct a TChunk based on the corresponding responses
        return tc1
    
    def get_right_subchunks(self, depth):
        right_subchunks = [self]
        nested_list = self.structure[:]
        for d in range(depth):
            nested_list = nested_list[-1]
            right_subchunks.append(VChunk(nested_list))
        return right_subchunks
    
    def chunk_at_depth(self, other, depth=0):
        if not isinstance(self.structure,list):
            nested_list = self.structure
        else:
            nested_list = self.structure[:]
        
        if depth == 0:
            return VChunk([nested_list,other.structure])
        else:
            modify_element_at_depth(nested_list, depth, other.structure)
            return VChunk(nested_list)
    
    def get_depth_old(self):
        st = str(self.structure)
        match = re.search("]*$",st)
        return len(match.group(0))
    
    def get_depth(self):
        structure = self.structure
        depth = 0
        while isinstance(structure, list) and len(structure) == 2:
            structure = structure[1]  # Always move to the right
            depth += 1
        return depth

    
    def remove_structure(self):
        if type(self.structure) is Type:
            return (self.structure)
        else:
            return flatten(self.structure)
        
    def remove_structure2(self):
        if type(self.structure) is Type:
            return [self.structure]
        else:
            return flatten(self.structure)
        


        
    def reduce(self):
        if type(self.structure) != list:
            return self.structure
        else:
            [s1,s2] = self.structure[:]
            s1 = VChunk(s1)
            s2 = VChunk(s2)
            if type(s1.structure) == float and type(s2.structure)== float:
                result = (s1.structure + s2.structure)/2
                return result
            elif type(s1.structure) != float and type(s2.structure)== float:
                result = (s1.reduce() + s2.structure)/2
                # Weird bug fixed by the following line: if more than one element reduce to 0, creates bug...
                self = VChunk([s1.structure,s2.structure])
                return result
            elif type(s1.structure) == float and type(s2.structure)!= float:
                result = (s1.structure + s2.reduce())/2
                # Weird bug fixed by the following line: if more than one element reduce to 0, creates bug...
                self = VChunk([s1.structure,s2.structure])
                return result
            else:
                t1 = s1.reduce()
                t2 = s2.reduce()
                result = (t1 + t2)/2
                # Weird bug fixed by the following line: if more than one element reduce to 0, creates bug...
                self = VChunk([s1.structure,s2.structure])

                return result
     
    
    
    def right_values(self):
        # Only works if TChunk is consistent!!!
        list_of_reduced_types = []
        if not isinstance(self.structure, list):
            list_of_reduced_types.append(self.structure)
            return list_of_reduced_types
        
        for chunk in self.get_right_subchunks(self.depth):
            list_of_reduced_types.append(chunk.reduce())
        list_of_reduced_types.reverse()
        return list_of_reduced_types
    
class ChunkTree:
    def __init__(self, left, right):
        self.left = left  # ChunkTree or placeholder
        self.right = right

    @staticmethod
    def from_tchunk(tchunk):
        if isinstance(tchunk.structure, Type):
            return None  # Atomic
        left, right = tchunk.structure
        return ChunkTree(
            ChunkTree.from_tchunk(TChunk(left)) or 0,  # placeholder for type
            ChunkTree.from_tchunk(TChunk(right)) or 0
        )

    def apply_types(self, types):
        if self.left == 0:
            left_type = types.pop(0)
        else:
            left_type = self.left.apply_types(types)

        if self.right == 0:
            right_type = types.pop(0)
        else:
            right_type = self.right.apply_types(types)

        return TChunk([left_type, right_type])
          
###############################################################################
#
#           Tests
#
###############################################################################
tests = False

v1 = VChunk(2.)
v2 = VChunk(3.)
v3 = VChunk(0.2)

if tests:    
    a = Type(r"aufubocodd")
    print(a)
    print(a.formula)
    print(re.findall(r"o"+a.right_type()+"$",a.formula))
    print(re.findall(r"^"+a.left_type()+"u",a.formula))
    #print(a.right_compatible_chunks2())
    #print(a.left_compatible_chunks2())
    
    b = Type(r"aufubocodd")
    print(b.left_type())
    print(b.right_type())
    print(b.get_primitives())
    
    
    print('-------------------------------')
    d = Type(r"ddoe")
    e = Type(r"dd")
    f = Type(r"a")
    g = Type(r"auf")
    h = Type(r"buauf")
    #print(f.right_compatible_chunks2())
    #print(f.left_compatible_chunks2())
    print(f.right_compatible_chunks())
    print(f.left_compatible_chunks())
    print(b.is_primitive())
    print(d.is_primitive())
    print(e.is_primitive())
    print(f.is_primitive())
    print(h.is_primitive())
    print(h.is_compatible(g))
    print('Compatibility check for ghost types')
    
    print(str(a)+'+'+str(d)+'='+str(a+d))
    print(str(a)+'+'+str(e)+'='+str(a+e))
    print(str(f)+'+'+str(a)+'='+str(f+a))
    #print(str(g)+'+'+str(a)+'='+str(g+a))
    #print(str(h)+'+'+str(a)+'='+str(h+a))
    
    
    
    
        
    def reduce_types(types):
        # make a copy of the list of types
        remaining_types = types[:]
        
        # keep trying to reduce the list of types until it contains only one type
        while len(remaining_types) > 1:
            #print(remaining_types)
            # set the reduced flag to False
            reduced = False
            
            # iterate over the remaining types
            for i, type1 in enumerate(remaining_types[:-1]):
                type2 = remaining_types[i+1]
                # if the two types are compatible, reduce them and update the reduced flag
                if type1.is_compatible(type2):
                    #print('add')
                    #print(type1)
                    #print(type2)
                    #print('result')
                    #print(type1+type2)
                    remaining_types[i] = type1 + type2
                    del remaining_types[i+1]
                    reduced = True
                    break
            
            # if the list of types was not reduced, raise a TypeError
            if not reduced:
                return remaining_types
        
        # return the remaining type
        return remaining_types
    
    t1 = Type("1o3")
    t3 = Type("3")
    t2 = Type("1u0o2")
    t5 = Type("dd")
    t4 = Type("4u2o3")
    ttt = Type('')
    print(t1.is_primitive())
    print(t2.is_primitive())
    print(t3.is_primitive())
    print(t4.is_primitive())
    print(t5.is_primitive())
    print(ttt.is_primitive())
    print(ttt.is_empty())
    
    print('???????????????????????????????')
    
    tt = Type("0")
    types = tt.split(pu=0.5)
    print(types)
    ttypes= types[0].split(pu=0.5,prim='New') + types[1].split(pu=0.5)
    print(ttypes)
    tctypes = []
    for ttt in ttypes:
        tctypes.append(TChunk(ttt))
        
    tttc =tctypes[0].chunk_at_depth(tctypes[1])
    tttc2 = tctypes[2].chunk_at_depth(tctypes[3])
    tchunk = tttc.chunk_at_depth(tttc2)
    print(tchunk)
    reduce_types(ttypes)
    print('Reduced?')
    print(Type.reduce(ttypes))
    print(Type.is_sentence(ttypes))
    #print(types[0].split())
    #print(types[1].split())
    
    #result = reduce_types([t1,t3, t2,t5, t4,t3])
    #print(result)  # prints "a\\b\\c\\d"
    
    tc =TChunk(b)
    print(tc)
    tcc = TChunk(t5)
    print(tcc)
    new_tc =TChunk([tc.structure,tcc.structure])
    print(new_tc)
    if new_tc.is_consistent():
        print(new_tc.reduce())
    else:
        print('incompatible types')
    #print(new_tc.is_consistent())
    print('---------------------')
    
    print(tchunk)
    print('right types')
    print(tchunk)
    print(tchunk.right_types())
    print('Test remove structure')
    print(tchunk.remove_structure())
    print(tchunk.get_right_subchunks(tchunk.depth))
    #print(reduce_types(tchunk.remove_structure()))
    list_of_reduced_types = reduce_types(tchunk.remove_structure())
    for chunk in tchunk.get_right_subchunks(tchunk.depth):
        if type(chunk.structure) is not Type:
            #print(chunk.structure[0]+chunk.structure[1])
            list_of_reduced_types.append(chunk.structure[0]+chunk.structure[1])
        else:
            list_of_reduced_types.append(chunk.structure)
            #print(chunk.structure)
    list_of_reduced_types.reverse()
    print(list_of_reduced_types)
    
    
    print('===================================')
    tt = Type("0")
    types = tt.split(pu=0.5)
    print(types)
    bad_s1 = {Type('0'):-1,Type('1'):-2}
    bad_s2 = {Type('0'):-1,Type('1'):-2,Type('2'):-2}
    ttypes= types[0].split(pu=0.5,prim='New',bad_s1=bad_s1,bad_s2=bad_s2) + types[1].split(pu=0.5)
    print(ttypes)
    tctypes = []
    for ttt in ttypes:
        tctypes.append(TChunk(ttt))
        
    tttc =tctypes[0].chunk_at_depth(tctypes[1])
    tttc2 = tctypes[2].chunk_at_depth(tctypes[3])
    tchunk = tttc.chunk_at_depth(tttc2)
    print(ttypes)
    reduce_types(ttypes)
    print('Reduced?')
    print(Type.reduce(ttypes))
    print(Type.is_sentence(ttypes))
    
    print('===================================')
    print(tchunk)
    print(tchunk.get_right_subchunks(tchunk.depth))
    #print(tchunk.is_consistent())
    #print(tchunk)
    #print(tchunk.reduce())
    #print(tchunk)
    print('right types version 1')
    print(tchunk.right_types())
    
    #TChunk(2)
