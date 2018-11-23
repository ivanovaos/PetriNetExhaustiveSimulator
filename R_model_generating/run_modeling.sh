#!/bin/bash
#some checks
COUNTER_from=1
while [ $COUNTER_from -lt 62 ]; do
    COUNTER_to=$(((COUNTER_from+5)-1))
    if [ $COUNTER_to -gt 61 ]
    then
        COUNTER_to=61
    fi
    echo The counter is $COUNTER_from $COUNTER_to
    jname="row"$COUNTER_from"to"$COUNTER_to
    echo $jname
    echo "module load R; Rscript /hpc/dbg_gen/samini/repos/exhaustivepetrinetsim/R_model_generating/generate_models.R $COUNTER_from $COUNTER_to" | qsub -l h_rt=8:00:00,tmpspace=2G,h_vmem=30G -N $jname
    let COUNTER_from=COUNTER_from+5
done
