# Extracting Data from Publications to inform Clinical Trials

This repo pprovides an overview of tools and workflows for extracting quantitative data from published clinical trial figures and tables. The goal is to reconstruct individual patient-level data (IPD) from publicly available sources when raw data is not accessible, supporting more data-driven clinical and statistical analyses.

---

## Key Topics Covered

- **Types of Data Extracted**:
  - Tabular data (e.g. baseline characteristics)
  - Plots and scatterplots
  - Kaplan–Meier (KM) survival curves

- **Extraction Tools and Workflows**:
  - [`tabulizer`](https://github.com/ropensci/tabulizer): R package for extracting structured tables from PDF publications
  - [`WebPlotDigitizer`](https://apps.automeris.io/wpd/): Web tool for extracting plot coordinates via manual or semi-automated digitization
  - Custom OpenCV image processing pipelines for fully automated extraction

---

## Kaplan–Meier Survival Curve Reconstruction

- **Digitization of KM curves**: Manual or semi-automatic marking of curve points using WebPlotDigitizer
- **Transformation to IPD**:
  - `ipdrecon`: R wrapper implementing two key reconstruction algorithms:
    - **Guyot et al. (2012)**: Uses digitized curve and risk table to estimate event and censoring distributions
    - **Rogula et al. (2022)**: Extends Guyot by incorporating known censoring times

- **Comparison**: Overlay of reconstructed survival curves and risk tables versus published plots to assess fidelity

---

## Tools and Packages Mentioned

- [`tabulizer`](https://github.com/ropensci/tabulizer): Extracts tables from PDFs using location-based hints
- [`WebPlotDigitizer`](https://apps.automeris.io/wpd/): Converts figure pixels to data space coordinates
- [`ipdrecon`](https://github.roche.com/wolowskv/ipdrecon) (R): Implements KM curve digitization to IPD reconstruction
- Other useful R packages:
  - `KMtoIPD`
  - `KMSubtraction`
  - `reconstructKM`



