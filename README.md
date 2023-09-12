# Temperature and Language Sonority

## Usage

The following 5 steps can be run separately as the output of each step is already provided in this repository (see [Data](#data) below). Steps 1 and 2 require a local storage of the [ASJP dataset](https://github.com/lexibank/asjp) and the [FLDAS dataset](https://hydro1.gesdisc.eosdis.nasa.gov/data/FLDAS/FLDAS_NOAH01_C_GL_M.001/), but you can skip these two steps so you do not need to download full datasets.

### 1. Extract geometry and sonority data from ASJP

Run `python get_sonority.py [raw_path]`, where `[raw_path]` is the path to `raw` folder in the local ASJP dataset (e.g. `python get_sonority.py C:/ASJP/raw/`). Results will be saved as `sonorities.csv`, `phones.csv`, `word_structures.csv`, and `word_lengths.csv` in the `data` folder.

### 2. Extract temperature data from FLDAS

Run `python get_temperature.py [FLDAS_path]` to extract monthly temperature data of all doculects in `sonorities.csv`, where `[FLDAS_path]` is the path to `FLDAS_NOAH01_C_GL_M.001` folder of the local FLDAS dataset (e.g. `python get_temperature.py C:/FLDAS/FLDAS_NOAH01_C_GL_M.001/`). Results will be saved as `data/temperatures.csv`.

Run `python get_temperature_global.py [FLDAS_path]` to extract global monthly mean temperature data. Result will be saved as `temperature_global.csv`.

### 3. Plot global distribution of temperature and sonority

Run `python plot_global.py`. Plot will be saved as `figure/global.png`.

### 4. Combine and process temperature and linguistic data

Run `python process.py`. Results will be saved as `data.csv`, `data_genus.csv`, `data_family.csv`, and `data_macroarea.csv` in the `data` folder.

### 5. Generate distribution and correlation plots, and more

Run corresponding code blocks in `process.r` in R.

## Data

All extracted data files are in the [`data`](data/) folder.

### Temperature Data

- [`temperatures.csv`](data/temperatures.csv): Monthly temperature (1982–2022) for each filtered doculect
- [`temperature_global.csv`](data/temperatures_global.csv): Global mean annual temperature over 41 years (180° W–180° E, 60° S–90° N)

### Linguistic Data

- [`sonorities.csv`](data/sonorities.csv): Mean sonority index (MSI) of each filtered doculect. We adapted 5 methods to calculate MSI from ASJP codes:
  - `index0`: Parker’s scale, from [Sonority](https://doi.org/10.1002/9781444335262.wbctp0049) in *The Blackwell Companion to Phonology*
  - `index1`: Fought’s scale, from [Sonority and climate in a world sample of languages: Findings and prospects](https://doi.org/10.1177/1069397103259439)
  - `index2`: List’s scale, from [*Sequence Comparison in Historical Linguistics*](https://doi.org/10.1515/9783110720082)
  - `index3`: Clements’s scale, from [The role of the sonority cycle in core syllabification](https://doi.org/10.1017/cbo9780511627736.017) in *Papers in Laboratory Phonology*
  - `index4`: Sonorant index (here obstruent = 1; sonorant = 2)
  - `index5`: Vowel index (here consonant = 1; semivowel = 2; vowel = 3)
  - `index6`: List’s scale, calculated using [LingPy `tokens2class()`](https://lingpy.org/reference/lingpy.sequence.html#lingpy.sequence.sound_classes.tokens2class)
- [`phones.csv`](data/phones.csv): Extracted phones from all doculects
- [`word_structures.csv`](data/word_structures.csv): Word structures statistics of all doculects, characterized by `C` (= consonant) and `V` (= vowel) symbols
- [`word_structures_grouped.csv`](data/word_structures_grouped.csv): Word lengths statistics of all doculects

### Combined Data

- [`data.csv`](data/data.csv): Data for each filtered doculect, with temperature data and linguistic data combined
  - `WL`: Mean word length
  - `Index0` to `Index6`: MSIs in 7 methods
  - `T`: Mean annual temperature
  - `T_max`: Max of 41-year mean monthly temperatures
  - `T_min`: Min of 41-year mean monthly temperatures
  - `T_sd`: Standard deviation of monthly temperatures over 41 years
  - `T_diff`: Mean annual range of temperature
  - `Index0_trans`, etc.: Transformated above data
- [`data_genus.csv`](data/data_genus.csv): Data for each [language “genus” classified by WALS](https://wals.info/languoid/genealogy)
- [`data_family.csv`](data/data_family.csv): Data for each [language family classified by WALS](https://wals.info/languoid/genealogy)
- [`data_macroarea.csv`](data/data_macroarea.csv): Data for each macroarea (North America, South America, Eurasia, Africa, Greater New Guinea, and Australia)

## Figures

All saved figure files are in the [`figures`](figures/) folder.

- [`global.png`](figures/global.png) (also converted into [`global.pdf`](figures/global.pdf)): Global distribution of MATs and MSIs
- [`distribution.pdf`](figures/distribution.pdf): Distribution of MATs and MSIs grouped by macroarea
- [`correlation.pdf`](figures/correlation.pdf): Relationship between MSI and MAT
- [`correlation_by_family.pdf`](figures/correlation_by_family.pdf): Relationship between MSI and MAT of the top 25 largest families
- [`word_length.pdf`](figures/word_length.pdf): Relationship between mean word length and MSI or MAT
- [`word_length_by_family.pdf`](figures/word_length_by_family.pdf): Relationship between MSI and mean word length of the top 25 largest families
- [`range.pdf`](figures/range.pdf): Relationship between mean annual range and MAT
