# First simulate WF+WO based on predicitions made by a WF attack, then compute
# metrics. Below are two examples for two types of WF attack output.

echo "WF type: probabilities for each possible WF label for each classification."
echo ""
python sim.py -lm example/df-nodef-test-labels-mon.pkl -lu example/df-nodef-test-labels-unmon.pkl -lp example/df-nodef-predictions.pkl -s example_prob.pkl
echo ""
python metrics.py -lm example/df-nodef-test-labels-mon.pkl -lu example/df-nodef-test-labels-unmon.pkl -wf example/df-nodef-predictions.pkl -p example_prob.pkl

echo "WF type: single prediction (label) for each classification."
echo ""
python sim.py -lm example/df-nodef-test-labels-mon.pkl -lu example/df-nodef-test-labels-unmon.pkl -lp example/df-nodef-predictions-single.pkl -s example_single.pkl
echo ""
python metrics.py -lm example/df-nodef-test-labels-mon.pkl -lu example/df-nodef-test-labels-unmon.pkl -wf example/df-nodef-predictions-single.pkl -p example_single.pkl
