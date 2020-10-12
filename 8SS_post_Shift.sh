#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=6
#SBATCH --time=06-23
#SBATCH --partition=shas      
#SBATCH --qos=long
#SBATCH --output=sample-%j.out
#SBATCH --mail-type=begin     
#SBATCH --mail-type=end
#SBATCH --mail-user=saup0513@colorado.edu

module load python
module load R
python main.py
