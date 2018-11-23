#!/bin/bash
path=$"/hpc/dbg_gen/samini/gi_kp_gstf/modeling/generated_models"

# number of tokens for each regulator: 100
# change the simulation folder in config file to: /hpc/dbg_gen/samini/gi_kp_gstf/modeling/simulation_results/

for folder in "$path"/*/; do
    #echo "$(basename $folder)/"
    echo "module load python/3.4.3; module load numpy/1.10.2; python /hpc/dbg_gen/samini/repos/exhaustivepetrinetsim/pipeline.py -c /hpc/dbg_gen/samini/repos/exhaustivepetrinetsim/config/pipeline_config.conf -d $folder -o "$(basename $folder)/""| qsub -pe threaded 1 -l h_rt=16:00:00,tmpspace=1G,h_vmem=5G 
done
