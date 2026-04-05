#!/bin/bash
#
#SBATCH --job-name=pablo # Job name for tracking
#SBATCH --partition=tiger  # Partition you wish to use (see above for list)
#SBATCH --cpus-per-task=20      # Number of CPU threads used by your job, set this upto 128 as required.
#SBATCH --mem=32000             # 384GB RAM
#SBATCH --time=2-00:00:00        # Job time limit set to 2 days (48 hours)
#
#SBATCH --output=aaapablo.out # Standard out from your job
#SBATCH --error=aaapablo.err  # Standard error from your job

## Initialisation ##
source /etc/profile.d/modules.sh
source /etc/profile.d/conda.sh

## Execute your program(s) ##
./run.sh
# python3 testLearnerWithType.py 3 200000
