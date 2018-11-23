#!/bin/bash
#some checks
#hostname
#date
#df -lh |grep $TMPDIR

#your command here
path=$"/hpc/dbg_gen/samini/gi_kp_gstf/modeling/simulation_results_v2"
for folder in "$path"/*; do
    echo $folder
    echo "module load R; Rscript /hpc/dbg_gen/samini/repos/exhaustivepetrinetsim/epis_analysis.R $folder" | qsub -l h_rt=40:00:00,tmpspace=1G,h_vmem=2G
done

#dd if=/dev/zero of=$TMPDIR/output.dat  bs=1M  count=100000 &
#catch the process id
#pid=$!

#if this script is killed, kill the catched process
#trap "kill $pid 2> /dev/null" EXIT

# While process is running...
#pmap -x $pid |head -n2 >$HOME/memUse/${JOB_ID}_${JOB_NAME}
#ps -o pid,tid,pcpu,psr|head >$HOME/cpUse/${JOB_ID}_${JOB_NAME}

#while kill -0 $pid 2> /dev/null; do
#    df -lh |grep $TMPDIR >>$HOME/tmpUse/${JOB_ID}_${JOB_NAME}
#    pmap -x $pid |grep total >>$HOME/memUse/${JOB_ID}_${JOB_NAME}
#    ps --no-headers -o pid,tid,pcpu,psr -p $pid >>$HOME/cpUse/${JOB_ID}_${JOB_NAME}
#    sleep 5
#done

# Disable the trap on a normal exit.
#trap - EXIT

