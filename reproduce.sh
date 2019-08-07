# reproduces wf+wo figures from "Website Fingerprinting with Website Oracles"

## figure 8, DF original dataset with nodef, WT, WTF-PAD
./sim.py -lm data/df/nodef-test-labels-mon.pkl -lu data/df/nodef-test-labels-unmon.pkl -lp data/df/nodef-predictions.pkl -s df_nodef.pkl
./metrics.py -lm data/df/nodef-test-labels-mon.pkl -lu data/df/nodef-test-labels-unmon.pkl -wf data/df/nodef-predictions.pkl -p df_nodef.pkl -o df_nodef -d "" -wl "DF"
./sim.py -lm data/df/wt-test-labels-mon.pkl -lu data/df/wt-test-labels-unmon.pkl -lp data/df/wt-predictions.pkl -s df_wt.pkl
./metrics.py -lm data/df/wt-test-labels-mon.pkl -lu data/df/wt-test-labels-unmon.pkl -wf data/df/wt-predictions.pkl -p df_wt.pkl -o df_wt -d "" -wl "DF"
./sim.py -lm data/df/wtfpad-test-labels-mon.pkl -lu data/df/wtfpad-test-labels-unmon.pkl -lp data/df/wtfpad-predictions.pkl -s df_wtfpad.pkl
./metrics.py -lm data/df/wtfpad-test-labels-mon.pkl -lu data/df/wtfpad-test-labels-unmon.pkl -wf data/df/wtfpad-predictions.pkl -p df_wtfpad.pkl -o df_wtfpad -d "" -wl "DF"

## figure 9, Wang et al.'s dataset with nodef, CS-BuFLO, and Tamaraw
./sim.py -lm data/wang/nodef-test-labels-mon.pkl -lu data/wang/nodef-test-labels-unmon.pkl -lp data/wang/nodef-predictions.pkl -s wang_nodef.pkl
./metrics.py -lm data/wang/nodef-test-labels-mon.pkl -lu data/wang/nodef-test-labels-unmon.pkl -wf data/wang/nodef-predictions.pkl -p wang_nodef.pkl -o wang_nodef -d "" -wl "DF"
./sim.py -lm data/wang/csbuflo-test-labels-mon.pkl -lu data/wang/csbuflo-test-labels-unmon.pkl -lp data/wang/csbuflo-predictions.pkl -s wang_csbuflo.pkl
./metrics.py -lm data/wang/csbuflo-test-labels-mon.pkl -lu data/wang/csbuflo-test-labels-unmon.pkl -wf data/wang/csbuflo-predictions.pkl -p wang_csbuflo.pkl -o wang_csbuflo -d "" -wl "DF"
./sim.py -lm data/wang/tamaraw-test-labels-mon.pkl -lu data/wang/tamaraw-test-labels-unmon.pkl -lp data/wang/tamaraw-predictions.pkl -s wang_tamaraw.pkl
./metrics.py -lm data/wang/tamaraw-test-labels-mon.pkl -lu data/wang/tamaraw-test-labels-unmon.pkl -wf data/wang/tamaraw-predictions.pkl -p wang_tamaraw.pkl -o wang_tamaraw -d "" -wl "DF"

## figure 10, Lu et al.'s DynaFlow dataset with nodef, config 1, and config 2
./sim.py -lm data/dynaflow/nodef-test-labels-mon.pkl -lu data/dynaflow/nodef-test-labels-unmon.pkl -lp data/dynaflow/nodef-predictions.pkl -s dynaflow_nodef.pkl
./metrics.py -lm data/dynaflow/nodef-test-labels-mon.pkl -lu data/dynaflow/nodef-test-labels-unmon.pkl -wf data/dynaflow/nodef-predictions.pkl -p dynaflow_nodef.pkl -o dynaflow_nodef -d "" -wl "DF"
./sim.py -lm data/dynaflow/config1-test-labels-mon.pkl -lu data/dynaflow/config1-test-labels-unmon.pkl -lp data/dynaflow/config1-predictions.pkl -s dynaflow_config1.pkl
./metrics.py -lm data/dynaflow/config1-test-labels-mon.pkl -lu data/dynaflow/config1-test-labels-unmon.pkl -wf data/dynaflow/config1-predictions.pkl -p dynaflow_config1.pkl -o dynaflow_config1 -d "" -wl "DF"
./sim.py -lm data/dynaflow/config2-test-labels-mon.pkl -lu data/dynaflow/config2-test-labels-unmon.pkl -lp data/dynaflow/config2-predictions.pkl -s dynaflow_config2.pkl
./metrics.py -lm data/dynaflow/config2-test-labels-mon.pkl -lu data/dynaflow/config2-test-labels-unmon.pkl -wf data/dynaflow/config2-predictions.pkl -p dynaflow_config2.pkl -o dynaflow_config2 -d "" -wl "DF"
