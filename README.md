# TDBRAIN Prediction Model

This repository contains code for EDA and model building on demographic and EEG data of the TDBRAIN dataset.  

## Environment Setup
After git cloning this repo, you can run the below commands from the main project directory to set up the conda environment:
```bash
# load anaconda module
module load anaconda3/2023.09-0-aqbc

# create the environment
conda env create -f environment.yml -n myenv

# activate the environment
conda activate myenv

# optional: make the environment available in Jupyter
conda install ipykernel
python -m ipykernel install --user --name=myenv --display-name "Python (myenv)"
