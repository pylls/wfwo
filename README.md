# Simulating Website Fingerprinting with Website Oracles (WF+WO) Attacks

Download [example data here](https://dart.cse.kau.se/example.zip) and unzip in
this directory.

First run `example.sh` to simulate WF+WO using the predictions (pre-computed
from the example data) from the [Deep Fingerprinting (DF) attack by Sirinam et
al.](https://github.com/deep-fingerprinting/df) with no WF defense in place.
This will produce two files, `example_prob.pkl` and `example_single.pkl`, that
are used for calculating metrics. Beyond output of typical ML metrics used for
WF attacks, there should `example.pdf` created that looks like this:

<div align="center">
<p align="center">
  <img src="example.png" width="500px" />
</p>
</div>

## Details on Simulation
The two example outputs from the simulation--`example_prob.pkl` and
`example_single.pkl`--are the results of simulating the WF+WO output of two
types of WF attacks based on the _WF_ output:

- Probabilities associated to each possible label (resulting in
  `example-prob.pkl`), and
- A single label for each test case (resulting in `example-single.pkl`). 

Probabilities are more useful and the defended traces in the example data use
this output. We include one example with single labels as a useful example for
those that might, e.g., want to simulate WF+WO on WF attacks that do not provide
probabilities as output. 

The example data also includes predictions by DF for the WF defenses WTF-PAD and
Walkie-Talkie. 

To run DF attacks (as input to our simulation), we also provide a smaller
[simple version of DF](https://github.com/pylls/df-simple).

### Parameters to the Simulation
The top of `sim.py` shows the arguments:

```
usage: sim.py [-h] -lm LM -lu LU -lp LP -s S [-t T] [-p P] [-a A] [-c C]
                    [-z Z]

optional arguments:
  -h, --help  show this help message and exit
  -lm LM      File with monitored testing labels
  -lu LU      File with unmonitored testing labels
  -lp LP      File with pre-computed predictions from the WF attack
  -s S        Filename for resulting simulated predictions
  -t T        Timeframe in milliseconds
  -p P        Probability of website oracle observing a website visit
  -a A        Max monitored starting Alexa rank 10^{0,a} (inclusive)
  -c C        Scale Tor network size
  -z Z        Be lazy and only re-simulate Tor when it makes sense
              statistically
```

The defaults are a timeframe of `100` ms, `1.0` probability, max Alexa rank `4`
(so Alexa rank 10,000), and being lazy when simulating. 

The script `example.sh` runs the following two simulations:

```
# WF with probabilities
python sim.py -lm example/df-nodef-test-labels-mon.pkl -lu example/df-nodef-test-labels-unmon.pkl -lp example/df-nodef-predictions.pkl -s example_prob.pkl

# WF with single label
python sim.py -lm example/df-nodef-test-labels-mon.pkl -lu example/df-nodef-test-labels-unmon.pkl -lp example/df-nodef-predictions-single.pkl -s example_single.pkl
```

### Using Predictions From Other WF Attacks
To use this script to simulate WF+WO attacks based on the output of another WF
attack, please see the instructions in the `main()` function of `sim.py`. In a
gist, you need to write a load function that structures the output of your WF
attack (that is provided as input to `sim.py`) in one of the expected formats.
Once that is done, the output of `sim.py` is largely what `metrics.py` expects.

## Details on Metrics
The `metrics.py` script has the following parameters:

```
usage: metrics.py [-h] -lm LM -lu LU -p P [-wf WF] [-d D] [-o O]

optional arguments:
  -h, --help  show this help message and exit
  -lm LM      File with monitored testing labels
  -lu LU      File with unmonitored testing labels
  -p P        File with simulated predictions from sim_wf+wo.py
  -wf WF      File with WF predictions provided as input to sim_wf+wo.py (for
              comparison)
  -d D        The figure title that describes the experiment
  -o O        Filename for the figure output
```
The script prints basic ML metrics used by the WF community. In addition, for
simulated WF+WO attacks that provide probabilities for each label, the script
also uses a threshold value and provides as output a precision-recall figure.
The figure is saved to `example.pdf` as default (`-o` flag), as shown at the top
of this README. 

Further, in both cases, if the `-wf` flag is provided with a path to the WF
predictions provided as input to `sim.py`, the script will also print metrics
and include the WF attack in the figure (if applicable). Note that you also need
to replace the `load_wf_predictions()` function here as in `sim.py`. 
