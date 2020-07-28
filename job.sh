#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=12
#SBATCH --time=06-23
#SBATCH --partition=shas
#SBATCH --qos=long
#SBATCH --output=sample-%j.out

module load python
module load R
python main.py
