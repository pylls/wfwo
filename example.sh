# First simulate WF+WO based on predicitions made by a WF attack, then compute
# metrics. Below are two examples for two types of WF attack output.

echo "WF type: probabilities for each possible WF label for each classification."
echo ""
./sim.py -lm example/df-nodef-test-labels-mon.pkl -lu example/df-nodef-test-labels-unmon.pkl -lp example/df-nodef-predictions.pkl -s example_prob_nodef.pkl
echo ""
./metrics.py -lm example/df-nodef-test-labels-mon.pkl -lu example/df-nodef-test-labels-unmon.pkl -wf example/df-nodef-predictions.pkl -p example_prob_nodef.pkl -o example_nodef

echo "WF type: single prediction (label) for each classification."
echo ""
./sim.py -lm example/df-nodef-test-labels-mon.pkl -lu example/df-nodef-test-labels-unmon.pkl -lp example/df-nodef-predictions-single.pkl -s example_prob_single.pkl
echo ""
./metrics.py -lm example/df-nodef-test-labels-mon.pkl -lu example/df-nodef-test-labels-unmon.pkl -wf example/df-nodef-predictions-single.pkl -p example_prob_single.pkl

# Below you find lines to run WF+WO sim and metrics against the WTF-PAD and
# Walkie-Talkie examples also included in examples.zip

echo "Probabilities, as above, but for WTF-PAD defense"
echo ""
./sim.py -lm example/df-wtfpad-test-labels-mon.pkl -lu example/df-wtfpad-test-labels-unmon.pkl -lp example/df-wtfpad-predictions.pkl -s example_prob_wtfpad.pkl
echo ""
./metrics.py -lm example/df-wtfpad-test-labels-mon.pkl -lu example/df-wtfpad-test-labels-unmon.pkl -wf example/df-wtfpad-predictions.pkl -p example_prob_wtfpad.pkl -o example_wtfpad

echo "Probabilities, as above, but for Walkie-Talkie defense"
echo ""
./sim.py -lm example/df-wt-test-labels-mon.pkl -lu example/df-wt-test-labels-unmon.pkl -lp example/df-wt-predictions.pkl -s example_prob_wt.pkl
echo ""
./metrics.py -lm example/df-wt-test-labels-mon.pkl -lu example/df-wt-test-labels-unmon.pkl -wf example/df-wt-predictions.pkl -p example_prob_wt.pkl -o example_wt
