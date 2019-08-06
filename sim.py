#!/usr/bin/env python
import argparse
import math
import numpy as np
import pickle
import copy

ap = argparse.ArgumentParser()
ap.add_argument("-lm", required=True, 
    help="File with monitored testing labels")
ap.add_argument("-lu", required=True, 
    help="File with unmonitored testing labels")
ap.add_argument("-lp", required=True, 
    help="File with pre-computed predictions from the WF attack")
ap.add_argument("-s", required=True, 
    help="Filename for resulting simulated predictions")

ap.add_argument("-t", required=False, type=int, default=100, 
    help="Timeframe in milliseconds")
ap.add_argument("-p", required=False, type=float, default=1.0, 
    help="Probability of website oracle observing a website visit")
ap.add_argument("-f", required=False, type=float, default=0.0, 
    help="False positive rate of the website oracle")
ap.add_argument("-a", required=False, type=int, default=4, 
    help="Max monitored starting Alexa rank 10^{0,a} (inclusive)")
ap.add_argument("-c", required=False, type=float, default=1.0, 
    help="Scale Tor network size")
ap.add_argument("-z", required=False, type=bool, default=True,
    help="Be lazy and only re-simulate Tor when it makes sense statistically")
args = vars(ap.parse_args())

def main():
    '''Perform a WF+WO attack with a simulated WO using results of a WF attack.

    There are two steps to using this script to simulate a WF+WO attack:
      1. Modify your WF attack code to store its labels and predictions, and
      2. modify the code below that loads labels and predictions.
    
    First train your WF attack and then modify the testing step to store, for
    each testing trace and its correct label/class, the correct label and the
    output of the WF attack. 
    
    We support two types of prediction outputs from the WF attack for WF+WO
    simulation per test case:
    - only the guessed label, or
    - a list of probabilities for each possible label.
    
    Next, modify the two functions below to load your correct labels from your
    testing data and the predictions. The load_labels() and
    load_predictions() functions document the expected formats.
    
    we assume that all unmonitored sites have the same integer label, and that
    monitored sites are labelled with smaller integers, including 0 FIXME:
    does 0 matter here?
    '''
    print("attempting to load labels")
    labels_mon, labels_unmon = load_labels()
    print("attempting to load predictions")
    predictions_mon, predictions_unmon = load_predictions()

    if not check_datatypes(labels_mon, labels_unmon, 
                predictions_mon, predictions_unmon):
        return -1
    print("all checks passed, labels and predictions should be OK")
    print("we got {} monitored and {} unmonitored labels".format(len(predictions_mon), len(predictions_unmon)))
    result = sim_wf_wo(labels_mon, labels_unmon, 
            predictions_mon, predictions_unmon, 
            args["t"], args["p"], args["f"], args["c"], args["a"], args["z"])

    print("All done! Saving simulated predictions to {}".format(args["s"]))
    pickle.dump(result, open(args["s"], "wb"))

def load_labels():
    '''Loads all testing labels. Change this function for your own data.

    The code below shows how to load the labels in the provided example/ folder,
    using the command line parameter to find the data to load. See (and use)
    check_datatypes() for all constraints on the output of this function.
    '''
    with open(args["lm"], 'rb') as handle: 
        labels_mon = list(np.array(pickle.load(handle)))
    with open(args["lu"], 'rb') as handle:
        labels_unmon = list(np.array(pickle.load(handle)))
    return labels_mon, labels_unmon

def load_predictions():
    '''Loads the WF predictions. Change this function for your own data.

    The code below shows how to load predictions from the example/ folder, using
    the command line parameter to find the data to load. See (and use)
    check_datatypes() for all constraints on the output of this function.
    '''
    return pickle.load(open(args["lp"], "rb"))

def check_datatypes(labels_mon, labels_unmon, pred_mon, pred_unmon):
    def is_expected_type(t, name, ):
        if not type(t) in [list, np.array, np.ndarray]:
            print("{} is type {}, expect {}".format(name, type(t), [list, np.array, np.ndarray]))
            return False
        return True
    
    if not is_expected_type(labels_mon, "labels_mon"):
        return False
    if not is_expected_type(labels_unmon, "labels_unmon"):
        return False
    if not is_expected_type(pred_mon, "pred_mon"):
        return False
    if not is_expected_type(pred_unmon, "pred_unmon"):
        return False

    if len(labels_mon) != len(pred_mon):
        print("expected the same number of monitored labels as predictions")
        return False
    if len(labels_unmon) != len(pred_unmon):
        print("expected the same number of unmonitored labels as predictions")
        return False

    if not (pred_type_single_pred(pred_mon) or pred_type_list_of_prob(pred_mon)):
        print("non-supported format for monitored predictions")
        return False
    if not (pred_type_single_pred(pred_unmon) or pred_type_list_of_prob(pred_unmon)):
        print("non-supported format for unmonitored predictions")
        return False

    return True

def pred_type_single_pred(pred):
    '''Checks if each prediction is just a single integer.'''
    return type(pred[0]) in [int, np.int, np.int32, np.int64]

def pred_type_list_of_prob(pred):
    '''Checks if each prediction is a list of floats for common types.'''
    return type(pred[0]) in [list, np.array, np.ndarray] and type(pred[0][0]) in [float, np.float, np.float32, np.float64]

def sim_wf_wo(labels_mon, labels_unmon, # correct labels
                pred_mon, pred_unmon,   # predictions from WF attack
                timeframe=100,          # in ms, timeframe for WO
                probability=1.0,        # probability of WO observing
                fpr=0.0,                # false positive rate of WO
                scale_tor=1.0,          # scale the size of Tor network
                max_alexa=4,            # Alexa 10^{0,max_alexa} (inclusive)
                lazy=True):             # sim WO lazy or every classification

    sim_fp = sim_wf_wo
    if pred_type_single_pred(pred_mon):
        print("each prediction is a single label, using wf_wo_single()")
        sim_fp = wf_wo_single
    if pred_type_list_of_prob(pred_mon):
        print("each prediction is a list of probabilities, using wf_wo_list_prob()")
        sim_fp = wf_wo_list_prob
    if sim_fp == sim_wf_wo:
        print("failed to find an appropriate function for wf+wo sim, this shouldn't have gotten past the check function")
        return -1

    popularity = [pow(10,i) for i in range(0,max_alexa+1)]
    results = []
    print("simulating WF+WO with timeframe {} ms, probability {}, fpr = {}, lazy = {}, scale Tor = {}".format(timeframe, probability, fpr, lazy, scale_tor))
    for i, p in enumerate(popularity):
        print("\tAlexa monitored websites starting rank {}".format(p))
        o, counter = create_oracle(100, p, probability, fpr, lazy, scale_tor)
        
        print("\t\t simulating predictions for monitored")
        wo_pred_mon = sim_fp(o, pred_mon, labels_mon, labels_unmon[0])
        wo_pred_mon_counter = counter[0]

        print("\t\t simulating predictions for unmonitored")
        wo_pred_unmon = sim_fp(o, pred_unmon, labels_unmon, labels_unmon[0])
        wo_pred_unmon_counter = counter[0] - wo_pred_mon_counter
        results.append([wo_pred_mon, wo_pred_unmon, wo_pred_mon_counter, wo_pred_unmon_counter])
    return results

def create_oracle(timeframe, popularity, 
                    probability=1.0, fpr=0.0, lazy=True, scale=1):
    # helper function that sims visits over Tor
    def sim_visits():
        v = []
        for _ in range(0, tor_network_sim_num_sites(timeframe, scale)):
            v.append(pop_mani_wilsonbrown_et_al())
        return v

    # list of simulated visited websites over Tor by all other Tor users
    visited = sim_visits()
    
    # hack to pass a mutable value that allows us to track the number of calls
    # to the oracle
    counter = [0]

    def oracle(website, correct):
        '''Precondition: correct is the correct label for a _monitored_ website.

        We have three cases:
        - the target user visited the correct monitored website, and then, per
          definition, the the oracle detects it with the defined probability, 
        - the website oracle produced a false positive, or
        - the website was visited by another (simulated) Tor user.

        Below we only make a fresh simulation of the Tor network if told to (not
        lazy), the simulated starting Alexa rank is below 1k, or the timeframe is long enough to warrant it (statistically). 
        '''
        counter[0] = counter[0] + 1

        if website == correct and np.random.random() < probability: # observed
            return True
        elif np.random.random() < fpr: # false positive
            return True
        elif not lazy or popularity < 1000 or timeframe > 1000: # be not lazy
            return website + popularity in sim_visits()
        else:
            return website + popularity in visited # be lazy
    return oracle, counter

def wf_wo_single(oracle, predictions, labels, unmon_label):
    predictions_updated = copy.deepcopy(predictions)

    for i in range(len(predictions)): 
        if predictions[i] >= unmon_label or oracle(predictions[i], labels[i]):
            continue
        predictions_updated[i] = unmon_label

    return predictions_updated

def wf_wo_list_prob(oracle, predictions, labels, unmon_label):
    predictions_updated = copy.deepcopy(predictions)

    for i in range(len(predictions)): 
        label_correct = labels[i]

        # loop until the highest probability label either is the unmonitored
        # label or a label for a website that has been visited according to 
        # the simulated website oracle
        for _ in range(len(predictions[i])):
            label_pred = np.argmax(predictions_updated[i])

            # done if already classified as unmonitored or visited
            if label_pred >= unmon_label or oracle(label_pred, label_correct):
                break
            
            # oracle says not visited, so probability of being correct is 0
            predictions_updated[i][label_pred] = 0.0

            # Update probabilities, using the method detailed in the WF+WO
            # paper. This method worked OK given how we defined thresholds for
            # DF, as is done in the metrics script.
            predictions_updated[i] = softmax(predictions_updated[i]*5 / max(predictions_updated[i]))

    return predictions_updated

# thank you https://stackoverflow.com/questions/34968722/how-to-implement-the-softmax-function-in-python
def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    return np.exp(x) / np.sum(np.exp(x), axis=0)

def pop_mani_wilsonbrown_et_al():
    """Returns a random website visit.

    This is an approximation of the observed distribution by Mani and
    Wilson-Brown et al. in "Understanding Tor Usage with Privacy-Preserving
    Measurement", Figure 2. The approximation is naive but punishes our attacker
    as long as we monitor websites in Alexa top 1m. This is because we slightly
    overestimate the visits to Alexa top 1m.
    """

    """
    Constant for torproject.org, because it was overrepresented in the paper due
    to what might have been a bug in Onionoo. We give it a constant label such
    that we can account for the case if the attacker is monitoring
    torproject.org or not.
    """
    torproject_label = 100000-1

    x = np.random.random() # uniform [0,1), slight bias towards Alexa sites
    if x < 0.401:
        return torproject_label
    elif x < 0.401+0.084: # websites (0,10]
        return np.random.randint(0, 10)+1
    elif x < 0.401+0.084+0.051: # websites (10,100]
        return np.random.randint(10,100)+1
    elif x < 0.401+0.084+0.051+0.062: # websites (100,1k]
        return np.random.randint(100,1000)+1
    elif x < 0.401+0.084+0.051+0.062+0.043: # websites (1k,10k]
        return np.random.randint(1000, 10*1000)+1
    elif x < 0.401+0.084+0.051+0.062+0.043+0.077: # websites (10k,100k]
        return np.random.randint(10*1000, 100*1000)+1
    elif x < 0.401+0.084+0.051+0.062+0.043+0.077+0.07: # websites (100k,1m]
        return np.random.randint(100*1000, 1000*1000)+1
    else:
        return np.random.randint(1000*1000, 2*1000*1000)+1

def tor_network_sim_num_sites(ms,scale_tor_network=1):
    """Answers: "how many new websites are visited over Tor in x ms?.

    This is based on 140M websites/24h by Mani et al.., the upper bound if a
    95% confidence interval for inferred website visits in early 2018 for the
    entire Tor network. 
    """
    return int(math.ceil((float(140*1000*1000)/float(24*60*60*1000))*ms*scale_tor_network))

if __name__ == "__main__":
    main()
