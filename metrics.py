#!/usr/bin/env python
import argparse
import numpy as np
import pickle
import sys
import matplotlib.pyplot as plt

ap = argparse.ArgumentParser()
ap.add_argument("-lm", required=True, 
    help="File with monitored testing labels")
ap.add_argument("-lu", required=True, 
    help="File with unmonitored testing labels")
ap.add_argument("-p", required=True, 
    help="File with simulated predictions from sim_wf+wo.py")

ap.add_argument("-wf", required=False, 
    help="File with WF predictions provided as input to sim_wf+wo.py (for comparison)")
ap.add_argument("-d", required=False, default="WF+WO, timeframe 100ms",
    help="The figure title that describes the experiment")
ap.add_argument("-o", required=False, default="example",
    help="Filename for the figure output")
ap.add_argument("-wl", required=False, default="WF",
    help="WF label in produced graphs")    
args = vars(ap.parse_args())

# values for styling graphs
linestyles = [":", "--", "-.", "-", "-.", "-", ":", "--"]
markerstyles = ['o', 's', 'v', '^', '<', '>', '*', 's', 'p', '*', 'h', 'H', 'D', 'd']
legends = [args["wl"], '1', '10', '100', '1k', '10k', '100k']
colors = ['#d44f7e', '#ffd03d', '#2fb651', '#fb8134', '#7556a2', '#5bb2e5']

def main():
    print("loading labels")
    labels_mon, labels_unmon = load_labels()

    print("loading predictions")
    predictions, wf_predictions = [], []
    predictions = load_predictions()
    if args["wf"] is not None:
        wf_predictions = load_wf_predictions()

    # simulated Alexa popularity from sim_wf+wo.py
    popularity = [pow(10,i) for i in range(0,len(predictions))]

    # if the output has probabilities, then we can use a threshold and also
    # generate pretty precision-recall curves
    if pred_type_list_of_prob(predictions[0][0]):
        # create the shell for our results figure
        plotstyle() # intended, due to matplotlib shenanigans
        fig, ax = plt.subplots()
        fig.set_size_inches(5,3)
        plotstyle() # intended, due to matplotlib shenanigans

        threshold = np.append([0], 1.0 - 1 / np.logspace(0.05, 2, num=15, 
        endpoint=True))
        if args["wf"] is not None:
            print("")
            print("first computing WF without WO metrics with threshold")
            all_precision, all_recall = [], []
            for th in threshold:
                tp, fpp, fnp, tn, fn, accuracy, recall, precision = metrics(th, wf_predictions[0], labels_mon, wf_predictions[1], labels_unmon)
                all_precision.append(precision)
                all_recall.append(recall)
                print("\tthreshold {:4.2}, recall {:4.2}, precision {:4.2}, accuracy {:4.2}\t [tp {:>6}, fpp {:>6}, fnp {:>6}, tn {:>6}, fn {:>6}]".format(th, recall, precision, accuracy, tp, fpp, fnp, tn, fn))

            print(" ")
            ax.plot(all_recall, all_precision, label=legends[0], ls=linestyles[0], marker=markerstyles[0], color=colors[0])

        print("computing WF+WO metrics for different Alexa ranks and thresholds")
        print("")
        for i, pop in enumerate(popularity):
            print("WF+WO at simulated starting monitored Alexa rank {:,}, WO calls per label for monitored ({:.2}) and unmonitored ({:.2}) datasets".format(pop, float(predictions[i][2])/float(len(labels_mon)), float(predictions[i][3])/float(len(labels_unmon))))
            all_precision, all_recall = [], []
            for th in threshold:
                tp, fpp, fnp, tn, fn, accuracy, recall, precision = metrics(th, predictions[i][0], labels_mon, predictions[i][1], labels_unmon)
                all_precision.append(precision)
                all_recall.append(recall)
                print("\tthreshold {:4.2}, recall {:4.2}, precision {:4.2}, accuracy {:4.2}\t [tp {:>6}, fpp {:>6}, fnp {:>6}, tn {:>6}, fn {:>6}]".format(th, recall, precision, accuracy, tp, fpp, fnp, tn, fn))

            print(" ")
            ax.plot(all_recall, all_precision, label=legends[1+i], ls=linestyles[1+i], marker=markerstyles[1+i], color=colors[1+i])
        
        # plot setting that has to be here and then save results
        ax.legend(facecolor='#f7f7f7', ncol=2)
        plt.savefig("{}.pdf".format(args["o"]), bbox_inches='tight')

    # if we only have a single prediction per test then only simple metrics
    if pred_type_single_pred(predictions[0][0]):
        
        if args["wf"] is not None:
            print("metrics for WF only:")
            tp, fpp, fnp, tn, fn, accuracy, recall, precision = simple_metrics(wf_predictions[0], labels_mon, wf_predictions[1], labels_unmon)
            print("recall {:4.2}, precision {:4.2}, accuracy {:4.2}\t [tp {:>6}, fpp {:>6}, fnp {:>6}, tn {:>6}, fn {:>6}]".format(recall, precision, accuracy, tp, fpp, fnp, tn, fn))
            print("")
            print("metrics for simulated WF+WO:")

        # metrics for each simulated Alexa rank
        for i, pop in enumerate(popularity):
            tp, fpp, fnp, tn, fn, accuracy, recall, precision = simple_metrics(predictions[i][0], labels_mon, predictions[i][1], labels_unmon)
            print("Alexa rank {:,}, recall {:4.2}, precision {:4.2}, accuracy {:4.2}\t [tp {:>6}, fpp {:>6}, fnp {:>6}, tn {:>6}, fn {:>6}]".format(pop, recall, precision, accuracy, tp, fpp, fnp, tn, fn))


def load_labels():
    '''Loads all testing labels. Same format expected as in sim_wf+wo.py.'''
    with open(args["lm"], 'rb') as handle: 
        labels_mon = list(np.array(pickle.load(handle)))
    with open(args["lu"], 'rb') as handle:
        labels_unmon = list(np.array(pickle.load(handle)))
    return labels_mon, labels_unmon

def load_predictions():
    return pickle.load(open(args["p"], "rb"))

def load_wf_predictions():
    return pickle.load(open(args["wf"], "rb"))

def metrics(threshold, predictions_mon, labels_mon, predictions_unmon, labels_unmon):
    ''' Computes a range of metrics.

    For details on the metrics, see, e.g., https://www.cs.kau.se/pulls/hot/baserate/
    '''
    tp, fpp, fnp, tn, fn, accuracy, recall, precision = 0, 0, 0, 0, 0, 0.0, 0.0, 0.0

    for i in range(len(predictions_mon)): # monitored
        label_pred = np.argmax(predictions_mon[i])
        prob_pred = max(predictions_mon[i])

        # either confident and correct,
        if prob_pred >= threshold and label_pred == labels_mon[i]:
            tp = tp + 1
        # confident and wrong monitored label, or
        elif prob_pred >= threshold and label_pred in labels_mon:
            fpp = fpp + 1
        # simply wrong because not confident or predicted unmonitored for monitored
        else:
            fn = fn + 1

    for i in range(len(predictions_unmon)): # unmonitored
        label_pred = np.argmax(predictions_unmon[i])
        prob_pred = max(predictions_unmon[i])

        if prob_pred < threshold or label_pred in labels_unmon: # correct prediction?
            tn = tn + 1
        elif label_pred < labels_unmon[0]: # predicted monitored for unmonitored
            fnp = fnp + 1
        else: # this should never happen
            print("this should never, wrongly labelled data? got label %d" % (label_pred))
            sys.exit(-1)

    if tp + fn + fpp > 0:
        recall = float(tp) / float(tp + fn + fpp)
    if tp + fpp + fnp > 0:
        precision = float(tp) / float(tp + fpp + fnp)

    accuracy = float(tp + tn) / float(tp + fpp + fnp + fn + tn)

    return tp, fpp, fnp, tn, fn, accuracy, recall, precision

def simple_metrics(predictions_mon, labels_mon, predictions_unmon, labels_unmon):
    ''' Computes a range of metrics, but without support for a threshold. 

    For details on the metrics, see, e.g.,
    https://www.cs.kau.se/pulls/hot/baserate/ . This function is as close as
    possible to metrics() for sake of ease of comparison.
    '''
    tp, fpp, fnp, tn, fn, accuracy, recall, precision = 0, 0, 0, 0, 0, 0.0, 0.0, 0.0

    for i in range(len(predictions_mon)): # monitored
        label_pred = predictions_mon[i]

        # correct,
        if label_pred == labels_mon[i]:
            tp = tp + 1
        # wrong monitored label, or
        elif label_pred in labels_mon:
            fpp = fpp + 1
        # wrong because predicted unmonitored for monitored
        else:
            fn = fn + 1

    for i in range(len(predictions_unmon)): # unmonitored
        label_pred = predictions_unmon[i]

        if label_pred in labels_unmon: # correct prediction?
            tn = tn + 1
        elif label_pred < labels_unmon[0]: # predicted monitored for unmonitored
            fnp = fnp + 1
        else: # this should never happen
            print("this should never, wrongly labelled data? got label %d" % (label_pred))
            sys.exit(-1)

    if tp + fn + fpp > 0:
        recall = float(tp) / float(tp + fn + fpp)
    if tp + fpp + fnp > 0:
        precision = float(tp) / float(tp + fpp + fnp)

    accuracy = float(tp + tn) / float(tp + fpp + fnp + fn + tn)

    return tp, fpp, fnp, tn, fn, accuracy, recall, precision

def pred_type_single_pred(pred):
    '''Checks if each prediction is just a single integer.'''
    return type(pred[0]) in [int, np.int, np.int32, np.int64]

def pred_type_list_of_prob(pred):
    '''Checks if each prediction is a list of floats for common types.'''
    return type(pred[0]) in [list, np.array, np.ndarray] and type(pred[0][0]) in [float, np.float, np.float32, np.float64]

def plotstyle():
    '''Sets a number of parameters for our graphs away from main()'''
    plt.style.use('ggplot')
    plt.rc('font',family='Ubuntu')
    plt.rcParams['lines.linewidth'] = 2
    plt.rcParams['font.size'] = 12
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.facecolor'] = '#fbfbfb'
    plt.xlabel('Recall', color=[0, 0, 0, 1])
    plt.ylabel('Precision', color=[0, 0, 0, 1])
    if args["d"] is not None:
        plt.title(args["d"])
    plt.tight_layout()

if __name__ == "__main__":
    main()
