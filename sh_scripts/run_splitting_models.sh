#!/bin/bash
echo "module load R; Rscript /hpc/dbg_gen/samini/repos/exhaustivepetrinetsim/divide_models.R" | qsub -l h_rt=60:00:00,tmpspace=1G,h_vmem=20G
