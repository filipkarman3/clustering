import pretty_errors

from collections import Counter

import scipy
from pprint import pprint

import numpy as np
from RawInput import RawInputLazy, ProbabilisticGrammar
from Learner import Learner,LearnerConfig
from Population import Population
from grammars import *
import matplotlib.pyplot as plt
import sys
from datetime import datetime
import concurrent.futures as cf

start_time = datetime.now()
n_sim = 20
n_trials = 100_000
alpha = 0.1
alpha_v = 1
beta = 1.
RW = True

config_t = LearnerConfig(n_trials=n_trials,
                       border = 'cont',
                       initial_value_chunking=-1.,
                       initial_value_border=1.,
                       alpha= alpha,
                       alpha_v=alpha_v,
                       beta= beta,
                       positive_reinforcement = 25,
                       negative_reinforcement = -10,
                       RW=RW,
                       chaining = False,
                       bad_type_threshold = -0.,
                       good_type_threshold = 0., 
                       tau = 0.1,
                       type_on = True)

config = LearnerConfig(n_trials=n_trials,
                       border = 'cont',
                       initial_value_chunking=-1.,
                       initial_value_border=1.,
                       alpha= alpha,
                       alpha_v=alpha_v,
                       beta= beta,
                       positive_reinforcement = 25,
                       negative_reinforcement = -10,
                       RW=RW,
                       chaining = False,
                       bad_type_threshold = -0.,
                       good_type_threshold = 0., 
                       tau = 0.1,
                       type_on = False)

#############################################################
#
#       G1 - valence
#
#############################################################

def generateGrammar(preterminals_, numterminals, rules_, weights_):
    # format the input preterminals
    preterminals = preterminals_.upper().split(" ")

    # format the input rules
    rules = {}
    non_terminals = []
    for rule_ in rules_:
        rule = rule_.upper()
        non_terminals.append(rule)
        rules[rule] = list(map(lambda x:x.split(" "), rules_[rule_].upper().split(";")))

    # format the input weights
    weights = {}
    for rule_ in weights_:
        rule = rule_.upper()
        weights[rule] = weights_[rule_]
    
    # generate terminals
    terminals = []
    for preterminal, num in zip(preterminals, numterminals):
        rules[preterminal] = [[f"{preterminal}{i}".lower()] for i in range(num)]
        terminals += list(map(lambda x:x[0], rules[preterminal]))
        non_terminals.append(preterminal)
        weights[preterminal] = [1/num for _ in range(num)]

    # print("--------------------")
    # for rule in rules:
    #     print(rule, rules[rule])
    #     print(weights[rule])
    #     print()
    return ProbabilisticGrammar(terminals, non_terminals, rules, weights)

preterminals = "n mtv dtv itv"
numterminals = [20,10,10, 10]
rules = {
    "s": "n itv;n mtv n;n dtv n n"
}
weights = {
    "s": [0.4, 0.3, 0.3]
}
cfg1 = generateGrammar(preterminals, numterminals, rules, weights)

#############################################################
#
#       G2 - conjunction
#
#############################################################

preterminals = "conj aj itv n"
numterminals = [1,   30,30, 30] # had to bump these up to let type get ahead
rules = {
    "s": "np itv",
    "np": "n;ajp n",
    "ajp": "aj;ajp' conj aj",
    "ajp'": "aj;aj ajp'"
}
weights = {
    "s": [1],
    "np": [0.5,0.5],
    "ajp": [0.7,0.3],
    "ajp'": [0.5,0.5]
}
cfg2 = generateGrammar(preterminals, numterminals, rules, weights)

#############################################################
#
#       G3 - agreement
#
#############################################################

preterminals = "npa npb aja ajb v mtv"
numterminals = [10,10,10, 10, 1,10]
rules = {
    "s": "NP MTV NP;NpA V AJA;NpB V AJB".lower(),
    "np": "npa;npb",
    "npa": "na;aja na",
    "npb": "nb;ajb nb"
}
weights = {
    "s": [0.6,0.2,0.2],
    "np": [0.5,0.5],
    "npa": [1],
    "npb": [1]
}
cfg3 = generateGrammar(preterminals, numterminals, rules, weights)

#############################################################
#
#       G4 - freer word order
#
#############################################################

preterminals = "aj n itv mtv t"
numterminals = [10,10,10,10, 3]
rules = {
    "s": "np vp;t np vp;np t vp;np vp t",
    "vp": "itv;mtv np",
    "np": "n;aj n"
}
weights = {
    "s": [.7,.1,.1,.1],
    "vp": [.6,.4],
    "np": [.5,.5]
}
cfg4 = generateGrammar(preterminals, numterminals, rules, weights)

#############################################################
#
#       Plotting functions
#
#############################################################

def plot_one(l):
    percentages = [np.mean(chunk) * 100 for chunk in np.array_split(l.wm.success, 100)]
    plt.plot([int(x*n_trials/100) for x in range(1,101)], percentages)
    plt.xlabel("Number of reinforcements")
    plt.ylabel("Percentage of correct parses")
    plt.ylim(-1, 101)
    plt.show()
    plt.savefig("graphs/plot-one.png")

def plot_many(ls):
    ps = []
    for l in ls:
        ps.append([np.mean(chunk) * 100 for chunk in np.array_split(l.wm.success, 100)])
        # for i,chunk in enumerate(np.array_split(l.success,100)):
        #     print(f"\n##### {i} #####")
        #     print(chunk)
        #     print(np.mean(chunk))
        # print(f"Success length: {len(l.success)}\n")
        # print(l.success)

    avg_percentages = np.mean(ps, axis=0)
    plt.xlabel("Number of reinforcements")
    plt.ylabel("Percentage of correct parses")

    # print("_-----------------------------------------------------------")
    plt.plot([int(x*n_trials/100) for x in range(1,101)], avg_percentages)
    plt.ylim(-1, 101)
    plt.show()
    plt.savefig("graphs/plot-many.png")

def plot_several(lss,savename=None,title=None):
    plt.clf()
    plt.xlabel("Number of reinforcements")
    plt.ylabel("Percentage of correct parses")
    plt.ylim(0,101)
    for ls, label in lss:
        ps = []
        for l in ls:
            ps.append([np.mean(chunk)*100 for chunk in np.array_split(l.wm.success,100)])
        avg_percentages = np.mean(ps, axis=0)
        plt.plot([int(x*n_trials/100) for x in range(1,101)], avg_percentages, label=label)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # plt.tight_layout()
    if savename is None:
        if title is not None: plt.title(title)
        plt.show()
    else:
        plt.savefig(f"graphs/{savename}.png", bbox_inches='tight')

#############################################################
#
#       Initialisation
#
#############################################################

"""
for cfg, cfgname in zip([cfg1,cfg2,cfg3,cfg4],["Transitivity grammar", "Conjunction grammar", "Agreement grammar", "Freer word order grammar"]):
# for cfg, cfgname in zip([cfg4],["Freer word order grammar"]):
    stimuli_stream = RawInputLazy(20*n_trials, cfg)
    lss = []
    max_num_samples = 20_000
    for conf, num_samples, clustering in zip([config,config,config,config,config_t],[0,20_000,0,20_000,0],[False,False,True,True,False]):
        ls = [Learner(conf, num_samples, cfg, clustering=clustering) for _ in range(0,3)]
        with cf.ThreadPoolExecutor() as executor:
            results = [executor.submit(lambda:l.learn(stimuli_stream)) for l in ls]
            for future in cf.as_completed(results):
                result = future.result()

        if conf.type_on:
            lss.append((ls,"CG model"))
        else:
            samplingtext = "No statistical clustering, " if num_samples==0 else f"{num_samples}-sample clustering, "
            clusteringtext = "no type clustering" if not clustering else "type clustering"
            lss.append((ls,samplingtext+clusteringtext))
    plot_several(lss,savename=cfgname)
exit()
"""

print('Initializing learners')
cfg=cfg1
stimuli_stream = RawInputLazy(20*n_trials,cfg)
typ = 'flexible'
border = 'nxt'

if n_sim == 1:
    l = Learner(config, 20_000, cfg, output=True, clustering=True)
    l.learn(stimuli_stream)
    print('Duration: {}'.format(datetime.now() - start_time))
    plot_one(l)

else:
    ls = [Learner(config, 0, cfg,clustering=False, original=False) for i in range(0,n_sim)]
    with cf.ThreadPoolExecutor() as executor:
        print("Number of worker threads:", executor._max_workers)
        results = [executor.submit(lambda:l.learn(stimuli_stream)) for l in ls]
        for future in cf.as_completed(results):
            result = future.result()
    print('Duration: {}'.format((datetime.now() - start_time)/n_sim))
    plot_many(ls)