# Setup
```bash
# create conda env from environment.yml
# make sure you have conda installed already
make env
conda activate dpsite
conda-develop . # from base of this project
```

# Remember to export env after installing new packages
```bash
conda activate dpsite

# try to use conda install only; `make export` relies on this since it uses "--from-history" (see Makefile).
conda install [package]

# make sure you have the conda-forge and main-x channels; some packages are only there
# to check: conda config --show channels
# to add:
#   conda config --append channels conda-forge
make export 
```

# Format
```bash
conda activate dpsite

make format
```
