# Temperature and Language Sonority

## Results

- [`sonorities.csv`](sonorities.csv): Mean sonority index (MSI) of each filtered doculect. We adapted 5 methods to calculate MSI from ASJP codes:
  - `index0`: Parker’s scale, from [Sonority](https://doi.org/10.1002/9781444335262.wbctp0049) in *The Blackwell Companion to Phonology*
  - `index1`: Fought’s scale, from [Sonority and climate in a world sample of languages: Findings and prospects](https://doi.org/10.1177/1069397103259439)
  - `index2`: Clements’ scale, from [The role of the sonority cycle in core syllabification](https://doi.org/10.1017/cbo9780511627736.017) in *Papers in Laboratory Phonology*
  - `index3`: Sonorant index (here obstruent = 1; sonorant = 2)
  - `index4`: Vowel index (here consonant = 1; semivowel = 2; vowel = 3)
- [`phones.csv`](phones.csv): Extracted phones from all doculects (not used further in this research)
- [`temperatures.csv`](temperatures.csv): Monthly temperature (1982–2022) for each filtered doculect
- `temperature_global.csv` (contained in [`temperature_global.zip`](temperature_global.zip)): Global 40-year mean monthly temperature.
- [`data.csv`](data.csv): MSIs and temperature data for each filtered doculect:
  - `Index0` to `Index4`: MSIs in 5 methods
  - `T`: Mean annual temperature
  - `T_max`: Max of 40-year mean monthly temperatures
  - `T_min`: Min of 40-year mean monthly temperatures
  - `T_sd`: Standard deviation of monthly temperatures over 40 years
  - `T_diff`: Mean annual range of temperature
  - `Index0_trans`, etc.: Transformated above data
- [`data_family.csv`](data_family.csv): MSIs and temperature data for each language family classified by WALS
- [`data_macroarea.csv`](data_macroarea.csv): MSIs and temperature data for each macroarea (North America, South America, Eurasia, Africa, Greater New Guinea, and Australia)
- [`global.png`](global.png) (also converted into [`global.pdf`](global.pdf)): Global distribution of MATs and MSIs
- [`distribution.pdf`](distribution.pdf): Distribution of MATs and MSIs grouped by macroarea
- [`correlation.pdf`](correlation.pdf): Relationship between MAT and MSI

## Usage

The following 5 steps can be run separately as the output of each step is already provided in this repository. `temperature_global.csv` is provided in zip file because its size is too large. Steps 1 and 2 require a local storage of the [ASJP dataset](https://github.com/lexibank/asjp) and the [FLDAS dataset](https://hydro1.gesdisc.eosdis.nasa.gov/data/FLDAS/FLDAS_NOAH01_C_GL_M.001/), but you can skip these two steps so you do not need to download full datasets.

### 1. Extract geometry and sonority data from ASJP

Run `py get_sonority.py [raw_path]`, where `[raw_path]` is the path to `raw` folder in the local ASJP dataset (e.g. `C:\ASJP\raw\`). Result will be saved as `sonorities.csv` and `phones.csv`.

### 2. Extract temperature data from FLDAS

Run `py get_temperature.py [FLDAS_path]` to extract monthy temperature data of all doculects in `sonorities.csv`, where `[FLDAS_path]` is the path to `FLDAS_NOAH01_C_GL_M.001` folder of the local FLDAS dataset (e.g. `C:\FLDAS\FLDAS_NOAH01_C_GL_M.001\`). Result will be saved as `temperatures.csv`.

Run `py get_temperature_global.py [FLDAS_path]` to extract global monthy mean temperature data. Result will be saved as `temperature_global.csv`.

### 3. Plot global distribution of temperature and sonority

(Unzip `temperature_global.zip`.) Run `py plot_global.py`. Plot will be saved as `global.png`.

### 4. Combine and process temperature and sonority data

Run `py process.py`. Results will be saved as `data.csv`, `data_family.csv`, and `data_macroarea.csv`.

### 5. Generate distribution and correlation plot

Run corresponding code blocks in `process.r` in R to:

- Read 3 csv files above and analysis the correlation
- Plot distribution of temperature and sonority
- Plot correlation of temperature and sonority

Plots were saved as `distribution.pdf` and `correlation.pdf` in this repository.
