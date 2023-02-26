# Temperature and Language Sonority

## Usage

The following 5 steps can be run separately as the output of each step is already provided in this repository. `temperature_global.csv` is provided in zip file because its size is too large. The first 2 steps require a local storage of the [ASJP dataset](https://github.com/lexibank/asjp) and the [FLDAS dataset](https://hydro1.gesdisc.eosdis.nasa.gov/data/FLDAS/FLDAS_NOAH01_C_GL_M.001/), but you can skip these steps so you do not need to download full datasets.

### 1. Extract geometry and sonority data from ASJP

Run `py get_sonority.py [raw_path]`, where `[raw_path]` is the path to `raw` folder in the local ASJP dataset (e.g. `C:\ASJP\raw\`). Data will be saved as `sonorities.csv`. A list of phones from extracted doculects will also be saved as `phones.csv`

### 2. Extract temperature data from FLDAS

Run `py get_temperature.py [FLDAS_path]` to extract monthy temperature data of all doculects in `sonorities.csv`, where `[FLDAS_path]` is the path to `FLDAS_NOAH01_C_GL_M.001` folder of the local FLDAS dataset (e.g. `C:\FLDAS\FLDAS_NOAH01_C_GL_M.001\`). Data will be saved as `temperatures.csv`.

Run `py get_temperature_global.py [FLDAS_path]` to extract global monthy mean temperature data. Data will be saved as `temperature_global.csv`.

### 3. Plot global distribution of temperature and sonority

(Unzip `temperature_global.zip`.) Run `py plot_global.py`. Plot will be saved as `global.png`.

### 4. Combine and process temperature and sonority data

Run `py process.py`. Data will be saved as `data.csv`, `data_family.csv`, and `data_macroarea.csv`.

### 5. Generate distribution and correlation plot

Run corresponding code blocks in `process.r` in R to:

- Read 3 csv files above and analysis the correlation
- Plot distribution of temperature and sonority
- Plot correlation of temperature and sonority

Plots are saved as `distribution.pdf` and `correlation.pdf` in this repository.
