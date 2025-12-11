# UAVision
UAVision is a Python package for UAV instrument data processing (particle counters, BME sensors, POPS, mCDA, OPC).
It provides preprocessing utilities, concentration calculations.

## Features
- Preprocessing helpers and utilities for particle counters and sensor streams
- Concentration / lag helpers for aerosol instruments (OPC / Mavic-like devices)
- Bundled bin-edge and mid-bin resources for common instrument presets
- Lazy-loading top-level submodules for fast imports

## Package layout
Top-level submodules (imported lazily): `mavic`, `bme`, `cpc`, `mcda`, `pops`

## Installation
From PyPI (when published):
```sh
pip install UAVision
```

From local source (development install):
```sh
git clone https://github.com/vietle94/UAVision.git
cd UAVision
pip install -e .
```

## Quick usage
Show package version and available submodules:
```py
import UAVision
print(UAVision.__version__)
print(UAVision.__all__)  # declared submodules
```

Access a submodule (imports lazily on first access):
```py
#    mCDA processing, calculate derived parameters as well
from UAVision.mcda.preprocess import preprocess_mcda
df = preprocess_mcda("data_path/datafile.csv", # path to mcda csv file (string)
                    size) # size category string, one of the following
#                           ['PSL_0.6-40', 'PSL_0.15-17', 'water_0.6-40', 'water_0.15-17'] OR
#                           an array-like of mid-bin values (list/tuple/ndarray)
#                           If an array-like is provided, it must be length 256.
#    return: processed dataframe

#    POPS processing
from UAVision.pops.preprocess import preprocess_pops
df = preprocess_pops("data_path/datafile.csv", # path to pops csv file (string)
                    size=None, # optional. If None uses bundled pops_binedges (bin edges).
                            # If array-like is provided it must be the bin edges with length 17.
                    drop_aux=True) # bool, if True drop auxiliary columns (default True). 
                            # If False keep them.
#    return: processed dataframe


#    CPC processing
from UAVision.cpc.preprocess import preprocess_cpc
df = preprocess_cpc("data_path/datafile.csv") # path to cpc csv file (string)
#    return: processed dataframe


#    BME processing
from UAVision.bme.preprocess import preprocess_bme
df = preprocess_bme("data_path/datafile.csv") # path to bme csv file (string)
#    return: processed dataframe

####################################################################################
# Check default bins
####################################################################################
# Check the mcda bins
mcda_midbin_all = UAVision.mcda.preprocess.mcda_midbin_all
print(mcda_midbin_all["water_0.15-17"])


# Check the pops bins
pops_binedges = UAVision.pops.preprocess.pops_binedges
print(pops_binedges)


# Check the OPC bins
# OPC N2
n2_binedges = UAVision.mavic.preprocess.n2_binedges
print(n2_binedges)

# OPC N3
n3_binedges = UAVision.mavic.preprocess.n3_binedges
print(n3_binedges)

```

# Contributing / Contact
Github: https://github.com/vietle94/UAVision

Author: viet.le@fmi.fi — pull requests and bug reports welcome.