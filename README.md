# PyRockDiff - Automatic change-detection workflow for rockfall identification

### 🚀 Quick Overview
This Python-based pipeline automates the comparison of two point clouds obtained from LiDAR or SfM, specifically targeting rock surfaces. It allows for efficient analysis of geological changes with minimal user input.

Key features include:

- **Automation:** The pipeline operates automatically, requiring only a single configuration file for setup.
- **User-Friendly Configuration:** Simplifies the process, making advanced analysis accessible without programming knowledge.
- **Preprocessing:** Cleans point clouds by removing noise and vegetation and aligns them accurately using registration algorithms.
- **Change Detection:** Detects differences between the two analyzed epochs with the M3C2 algorithm.
- **Clustering & Volume Calculation:** Isolates changes using DBSCAN and estimates volumes via alpha-shape triangulation.

## Table of Contents
- [Overview](#overview)
- [Installation and Requirements](#installation-and-requirements)
  - [Installation](#installation)
- [How It Works](#how-it-works)
- [Usage Guide](#usage-guide)
- [Future Updates & Development Stages](#future-updates--development-stages)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Overview

<details>
<summary>Click to expand</summary>

<br>

This project is a Python-based pipeline designed to automate the comparison of two point clouds obtained from LiDAR or Structure from Motion (SfM), specifically focusing on rock surfaces. The pipeline begins with essential pre-processing steps, including data cleaning and vegetation removal, to prepare the data for analysis. It then employs algorithms for Fast Global Registration and Iterative Closest Point (ICP) alignment, enabling precise change detection results.

The software identifies differences between the two epochs using the M3C2 algorithm, isolates clusters using the DBSCAN algorithm, and calculates the volumes of detected changes through alpha-shape triangulation. It is designed for automation and user-friendliness, making it accessible to non-experts in coding while efficiently processing large datasets. The libraries and software used are open-source, enhancing accessibility and collaboration.
</details>

## Installation and requirements

<details>
<summary>Click to expand</summary>

The following external open-source software is used:

| Software/Library | License | Link |
|------------------|---------|------|
| CloudCompare      | GPL     | [CloudCompare Website](https://www.danielgm.net/cc/) |

Other dependencies are managed through Python, and can be installed via `requirements.txt`.

### Installation
To set up the environment and install the required dependencies:

```bash
git clone https://github.com/xabierblanch/PyRockDiff.git
cd PyRockDiff
pip install -r requirements.txt
```
Ensure CloudCompare is downloaded and accessible from the command line.

</details>

## How It Works

This section provides a basic overview of how the code operates, what inputs are expected, and how the execution flow is controlled.

<details>
<summary>Basic Functionality</summary>

### Basic Functionality
The code is designed to automate a sequence of point cloud processing tasks, including filtering, registration, clustering, and volume computation. Each step is modular and can be executed depending on the options selected.
</details>

<details>
<summary>Input Data</summary>

### Input Data
The code expects specific input data formats:
- Point clouds (e.g., `.ply`, `.las`)
- Pre-defined parameters and paths provided through a configuration `.JSON` file.
</details>

<details>
<summary>Configuration JSON File</summary>

### Configuration JSON File
All options, paths, and parameters for the execution are controlled through a configuration file located in the `json_files` folder. This file allows the user to toggle various processing steps and fine-tune parameters without modifying the code.
</details>

<details>
<summary>Code Structure</summary>

### Code Structure
The code follows a sequential execution pattern, but it is flexible. You can start from any step in the workflow, provided the necessary files from earlier steps are supplied as inputs. This modular approach allows skipping steps that have been completed previously or executing the entire workflow from start to finish.
</details>


## Usage Guide
<details>
<summary>1. Transform and Subsample</summary>

#### Transform and Subsample
<p>Transforms and subsamples the point clouds using CloudCompare, if the <code>transform_and_subsample</code> option is enabled.</p>
</details>

<details>
<summary>2. Vegetation Filter</summary>

#### Vegetation Filter (CANUPO)
<p>Applies the vegetation filter using CANUPO, if the <code>vegetation_filter</code> option is enabled.</p>
</details>

<details>
<summary>3. Cleaning Filter</summary>

#### Cleaning Filter
<p>Applies a statistical outlier removal filter, if the <code>cleaning_filtering</code> option is enabled.</p>
</details>

<details>
<summary>4. Fast Global Registration</summary>

#### Fast Registration
<p>Performs Fast Global Registration (FGR), if the <code>fast_registration</code> option is enabled.</p>
</details>

<details>
<summary>5. ICP Registration</summary>

#### ICP Registration
<p>Executes ICP (Iterative Closest Point) registration, if the <code>icp_registration</code> option is enabled.</p>
</details>

<details>
<summary>6. ROI Focus</summary>

#### ROI Focus
<p>Performs Region of Interest (ROI) clipping on the point clouds, if the <code>roi_focus</code> option is enabled.</p>
</details>

<details>
<summary>7. M3C2 Change Detection</summary>

#### M3C2 Computation
<p>Computes change detection using the M3C2 algorithm, if the <code>m3c2_dist</code> option is enabled.</p>
</details>

<details>
<summary>8. Autoparameters</summary>

#### Auto Parameters for DBSCAN
<p>Calculates point density for DBSCAN parameters, if the <code>auto_parameters</code> option is enabled.</p>
</details>

<details>
<summary>9. Rockfall clustering</summary>

#### Rockfall Clustering (DBSCAN)
<p>Applies the DBSCAN algorithm to identify clusters in the point clouds, if the <code>rf_clustering</code> option is enabled.</p>
</details>

<details>
<summary>10. Volume Estimation</summary>

#### Volume Estimation
<p>Estimates the volume of the detected clusters, if the <code>rf_volume</code> option is enabled.</p>
</details>

## Development stages & Future Updates

<details>
<summary>Current Version TODOs</summary>

### Current Version TODOs

The following functionalities are part of the current version but require further refinement:

- [ ] Verify all paths before CloudCompare
- [ ] Enhance plots/visualizations and saving options
- [ ] Add the option to activate/deactivate additional features
- [ ] Review verbosity and debugging options
- [ ] Add a robust way to select parameters
- [ ] Create a graphical abstract

</details>

<details>
<summary>Planned Features</summary>

### Planned Features

The following features and enhancements are planned for future versions of this software:

- [ ] Implement the software for pre-failure deformation identification
- [ ] Integrate tools from [**py4dgeo**](https://github.com/3dgeo-heidelberg/py4dgeo) (MIT License)
- [ ] Provide different approaches for volume calculation
- [ ] Add AI tools for vegetation filtering
- [ ] Add AI tools to filter the wrong clusters (Blanch et al, 2020)
- [ ] Include and process RGB data (for LiDAR or SfM Point Clouds)

</details>

## Contact

<details>
<summary>Click to expand</summary>

For questions, issues, or further information regarding this software, feel free to reach out to the authors:

- **Xabier Blanch**: xabier.blanch@upc.edu

Please include a clear subject line and detailed information if reporting a bug or requesting support.

</details>

## Acknowledgments

<details>
<summary>Click to expand</summary>

We would like to thank the following individuals and institutions for their invaluable contributions and support:

- The [**RISKNAT research group**](http://www.ub.edu/risknat/) at the University of Barcelona for their past support of the doctoral research that laid the basis for this software.
- The [**Technische Universität Dresden**](https://tu-dresden.de/) and [**Universitat Politècnica de Catalunya**](https://www.upc.edu/en) for their assistance with the project.
- The colleagues at the [**Juniorprofessur für Geosensorsysteme**](https://tu-dresden.de/bu/umwelt/geo/ipf/geosensorsysteme) (TU Dresden) for their cooperation and support.
- The [**ICGC**](http://www.icgc.cat/) (Institut Cartogràfic i Geològic de Catalunya) for funding this project.
- The [**CloudCompare**](https://www.danielgm.net/cc/) and [**Open3D**](http://www.open3d.org/) open-source communities for their incredible tools and libraries.
- The [**CANUPO**](https://nicolas.brodu.net/common/recherche/publications/canupo.pdf) (Brodu & Lague) and [**M3C2**](https://www.sciencedirect.com/science/article/abs/pii/S0924271613001184) (Lague et al.) authors for developing these great algorithms.

Additionally, the methodologies used in this software are based on the work developed in the following doctoral theses in the RISKNAT research group:

| Author           | Title                                                                                                                                                                                                                                                                                                                     | Year |
|------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------|
| Antonio Abellán  | [Improvements in our understanding of rockfall phenomenon by Terrestrial Laser Scanning](https://www.researchgate.net/publication/257870480_PhD_Thesis_-_Improvements_in_our_understanding_of_rockfall_phenomenon_by_Terrestrial_Laser_Scanning_-_Emphasis_on_change_detection_and_its_application_to_spatial_prediction) | 2010 | 
| Manuel Royán     | [Rockfall characterization and prediction by means of Terrestrial LiDAR](https://www.tdx.cat/handle/10803/334400#page=1)                                                                                                                                                                                                  | 2015 |
| Xabier Blanch    | [Developing Advanced Photogrammetric Methods for Automated Rockfall Monitoring](https://diposit.ub.edu/dspace/handle/2445/189157)                                                                                                                                                                                         | 2023 |


</details>

## License

<details>
<summary>Click to expand</summary>

This project is licensed under the **GNU General Public License (GPL)**. You are free to use, modify, and distribute this software under the terms of this license.

For more information, please refer to the [GPL License](https://www.gnu.org/licenses/gpl-3.0.en.html).

</details>