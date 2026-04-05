# -*- coding: utf-8 -*-
"""
Created on Thu May  1 22:24:02 2025

@author: jmd01
"""

from RawInput import RawInput, RawInputLazy, ProbabilisticGrammar
from Learner import LearnerConfig, Learner
from Population import Population
import matplotlib.pyplot as plt

from datetime import datetime



def flatten(lst):
    flat_list = []
    for item in lst:
        if isinstance(item, list):
            flat_list.extend(flatten(item))
        else:
            flat_list.append(item)
    return flat_list

def create_stimuli():
    number_of_verbs = 5
    number_of_nouns = 5
    number_of_adj = 0
    number_of_relpron = 2
    number_of_det = 0
    
    verbs = ['v' + str(i) for i in range(1, number_of_verbs+1)]
    nouns = ['n' + str(i) for i in range(1, number_of_nouns+1)]
    adjs = ['a' + str(i) for i in range(1, number_of_adj+1)]
    relpron = ['r' + str(i) for i in range(1, number_of_relpron+1)]
    det = ['d' + str(i) for i in range(1, number_of_det+1)]
    
    terminals2 = flatten([verbs,nouns,adjs,relpron,det])
    non_terminals2 = ['S', 'N','NP','VP','V','RelCl']
    
    ###############################################################
    #
    #       NVN language
    #
    ###############################################################
    
    # Grammatical rules
    production_rulesNVN = {
        'S': [['N', 'VP','N']],
        'VP': [['V']],
        'N': [['n' + str(i)] for i in range(1, number_of_nouns+1)],
        'V': [['v' + str(i)] for i in range(1, number_of_verbs+1)]
    }
    
    weightsNVN = {
        'S': [1],
        'VP': [1],
        'N': [1/number_of_nouns for i in range(1, number_of_nouns+1)],
        'V': [1/number_of_verbs for i in range(1, number_of_verbs+1)]    
        }
    
    cfgNVN = ProbabilisticGrammar(terminals2, non_terminals2, production_rulesNVN,weightsNVN)
    return RawInputLazy(n_sentences=2000, grammar=cfgNVN)

if __name__ == '__main__':

    print('Defining the grammar')
    
    # definition of the grammar
    # Vocabulary
    number_of_verbs = 5
    number_of_nouns = 5
    number_of_adj = 0
    number_of_relpron = 2
    number_of_det = 0
    
    verbs = ['v' + str(i) for i in range(1, number_of_verbs+1)]
    nouns = ['n' + str(i) for i in range(1, number_of_nouns+1)]
    adjs = ['a' + str(i) for i in range(1, number_of_adj+1)]
    relpron = ['r' + str(i) for i in range(1, number_of_relpron+1)]
    det = ['d' + str(i) for i in range(1, number_of_det+1)]
    
    terminals2 = flatten([verbs,nouns,adjs,relpron,det])
    non_terminals2 = ['S', 'N','NP','VP','V','RelCl']
    
    ###############################################################
    #
    #       NVN language
    #
    ###############################################################
    
    # Grammatical rules
    production_rulesNVN = {
        'S': [['N', 'VP','N']],
        'VP': [['V']],
        'N': [['n' + str(i)] for i in range(1, number_of_nouns+1)],
        'V': [['v' + str(i)] for i in range(1, number_of_verbs+1)]
    }
    
    weightsNVN = {
        'S': [1],
        'VP': [1],
        'N': [1/number_of_nouns for i in range(1, number_of_nouns+1)],
        'V': [1/number_of_verbs for i in range(1, number_of_verbs+1)]    
        }
    
    cfgNVN = ProbabilisticGrammar(terminals2, non_terminals2, production_rulesNVN,weightsNVN)
    # Context free grammar
    
    print('Creating the stimuli stream')
    stimuli_stream = RawInputLazy(n_sentences=2000, grammar=cfgNVN)
    
    print('Learner initialization')
    # Configure and initialize learner
    n_trial = 1000
    alpha = 0.1
    alpha_v = 1
    beta = 1.9
    chaining = True
    RW = True
    configRWN = LearnerConfig(n_trials=n_trial,
                           border = 'cont',
                           initial_value_chunking=-1.,
                           initial_value_border=1.,
                           alpha= alpha,
                           alpha_v=alpha_v,
                           beta= beta,
                           positive_reinforcement = 25,
                           negative_reinforcement = -10,
                           RW=RW,
                           chaining = chaining)
    
    configRWC = LearnerConfig(n_trials=n_trial,
                           border = 'cont',
                           initial_value_chunking=-1.,
                           initial_value_border=1.,
                           alpha= alpha,
                           alpha_v=alpha_v,
                           beta= beta,
                           positive_reinforcement = 25,
                           negative_reinforcement = -10,
                           RW=RW,
                           chaining = False)
    
    configN = LearnerConfig(n_trials=n_trial,
                           border = 'next',
                           initial_value_chunking=-1.,
                           initial_value_border=1.,
                           alpha= alpha,
                           alpha_v=alpha_v,
                           beta= beta,
                           positive_reinforcement = 25,
                           negative_reinforcement = -10,
                           RW=RW,
                           chaining = chaining)
    
    configC = LearnerConfig(n_trials=n_trial,
                           border = 'next',
                           initial_value_chunking=-1.,
                           initial_value_border=1.,
                           alpha= alpha,
                           alpha_v=alpha_v,
                           beta= beta,
                           positive_reinforcement = 25,
                           negative_reinforcement = -10,
                           RW=RW,
                           chaining = False)
    
    
    
    # Initialize a learner
    learner = Learner(configN)
    
    print('Learning...')
    # Run learning
    learner.learn(stimuli_stream)
    
    print('Postprocessing')
    # Plot learning performance (moving average of successes)
    learner.history.plot_moving_average(15)
    
    print('Testing on population')
    labels = ['Next','NextChaining','Cont','ContChaining']
    config = [configC,configN,configRWC,configRWN]
    # Shared input
    start = datetime.now()
    #pop = Population(n_learners=100, config=config, grammar=cfgNVN, stimuli_stream=stimuli_stream)
    
    curves = []
    # Or: per-learner input
    #factory = lambda: RawInputLazy(n_sentences=2000, grammar=cfgNVN)
    
    
    
    for conf in config:
        pop = Population(n_learners=10, config=conf, stimuli_factory=create_stimuli)
        
        pop.train_all(use_multiprocessing=False)
        curves.append(pop.plot_average_learning_curve(window=10,show=False))
         
    end  = datetime.now()
    
    for curve, label in zip(curves,labels):
        plt.plot(curve, label = label)
    
    plt.title("Learning Curves Comparison")
    plt.xlabel("Trial")
    plt.ylabel("Moving Average Success")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    print('Duration: {}'.format(end - start))
    
    