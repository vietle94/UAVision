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
- Package data: /bin_edges/*.txt

## Example usage
```sh
from UAVision.preprocess import preprocess_mcda
df = preprocess_mcda("data_path/datafile.csv", size="water_0.15-17")
```
# Notes
Bin-edge files are included as package data and can be loaded with importlib.resources. See pyproject.toml for packaging metadata.

# Contributing / Contact
Author: viet.le@fmi.fi — pull requests and bug reports welcome.