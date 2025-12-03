# UAVision
UAVision is a Python package for UAV instrument data processing (particle counters, BME sensors, POPS, mCDA, OPC).
It provides preprocessing utilities, concentration calculations.

## Features
- Preprocessing and derived metrics for MCDA, POPS and other instruments.
- OPC / Mavic helpers for concentration and lag calculations.
- Included bin-edge resources for common instruments (mcda, pops, opc).
- For mcda, there are 4 options for sizes: ['PSL_0.6-40', 'PSL_0.15-17', 'water_0.6-40', 'water_0.15-17']

## Key modules (examples)
- UAVision.preprocess — functions like preprocess_mcda, preprocess_pops, calculate_height_df.
- UAVision.mavic.preprocess — functions like calculate_concentration, calculate_lag.

## Example usage
```sh
from UAVision.preprocess import preprocess_mcda
df = preprocess_mcda("data_path/datafile.csv", size="water_0.15-17")
```
The bins and bins can be found as
```sh
import UAVision

mcda_midbin_all = UAVision.preprocess.mcda_midbin_all
print(mcda_midbin_all["water_0.15-17"])

pops_binedges = UAVision.preprocess.pops_binedges
print(pops_binedges)

import UAVision.mavic
n2_binedges = UAVision.mavic.preprocess.n2_binedges
print(n2_binedges)

n3_binedges = UAVision.mavic.preprocess.n3_binedges
print(n3_binedges)
```

# Contributing / Contact
Author: viet.le@fmi.fi — pull requests and bug reports welcome.