# PyRockDiff: Automatic change-detection workflow for rockfall identification

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

This project is a Python-based pipeline for processing point cloud data. It uses various open-source libraries and implements techniques such as data cleaning, filtering, registration, and clustering. Additionally, the software provides automatic parameter calculation and volume estimation of clusters in the point clouds. This Python code automates point cloud change detection between two epochs, using techniques like ICP registration, DBSCAN clustering, and the M3C2 algorithm. It leverages libraries like CloudCompare, py4dgeo, and Open3D.

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

<details>
<summary>Click to expand</summary>

This section provides a basic overview of how the code operates, what inputs are expected, and how the execution flow is controlled.

### Basic Functionality
The code is designed to automate a sequence of point cloud processing tasks, including filtering, registration, clustering, and volume computation. Each step is modular and can be executed depending on the options selected.

### Input Data
The code expects specific input data formats:
- Point clouds (e.g., `.ply`, `.las`)
- Pre-defined parameters and paths provided through a configuration `.JSON` file.

### Configuration via JSON File
All options, paths, and parameters for the execution are controlled through a configuration file located in the `json_files` folder. This file allows the user to toggle various processing steps and fine-tune parameters without modifying the code.

### Sequential Code Structure
The code follows a sequential execution pattern, but it is flexible. You can start from any step in the workflow, provided the necessary files from earlier steps are supplied as inputs. This modular approach allows skipping steps that have been completed previously or executing the entire workflow from start to finish.

</details>

## Usage Guide

<details>
<summary>Click to expand</summary>

This workflow follows the execution order of the main functions, depending on the selected options. Each function is numbered and organized in expandable sections for more details.

### Main Functions

Depending on the options selected in the JSON file, some functions will be called. Below is the list of all conditional functions:

#### Transform and Subsample
<details>
<summary>5. <code>utils.transform_subsample()</code></summary>
<p>Transforms and subsamples the point clouds using CloudCompare, if the <code>transform_and_subsample</code> option is enabled.</p>
</details>

#### Vegetation Filter (CANUPO)
<details>
<summary>6. <code>cp.canupo_core()</code></summary>
<p>Applies the vegetation filter using CANUPO, if the <code>vegetation_filter</code> option is enabled.</p>
</details>

#### Cleaning Filter
<details>
<summary>7. <code>cl.outlier_filter()</code></summary>
<p>Applies a statistical outlier removal filter, if the <code>cleaning_filtering</code> option is enabled.</p>
</details>

#### Fast Registration
<details>
<summary>8. <code>reg.FGR_reg()</code></summary>
<p>Performs Fast Global Registration (FGR), if the <code>fast_registration</code> option is enabled.</p>
</details>

#### ICP Registration
<details>
<summary>9. <code>reg.ICP_reg()</code></summary>
<p>Executes ICP (Iterative Closest Point) registration, if the <code>icp_registration</code> option is enabled.</p>
</details>

#### ROI Focus
<details>
<summary>10. <code>main_2Dcut()</code></summary>
<p>Performs Region of Interest (ROI) clipping on the point clouds, if the <code>roi_focus</code> option is enabled.</p>
</details>

#### M3C2 Computation
<details>
<summary>11. <code>m3c2.m3c2_core()</code></summary>
<p>Computes change detection using the M3C2 algorithm, if the <code>m3c2_dist</code> option is enabled.</p>
</details>

#### Auto Parameters for DBSCAN
<details>
<summary>12. <code>utils.density()</code></summary>
<p>Calculates point density for DBSCAN parameters, if the <code>auto_parameters</code> option is enabled.</p>
</details>

#### Rockfall Clustering (DBSCAN)
<details>
<summary>13. <code>rf.dbscan()</code></summary>
<p>Applies the DBSCAN algorithm to identify clusters in the point clouds, if the <code>rf_clustering</code> option is enabled.</p>
</details>

#### Volume Estimation
<details>
<summary>14. <code>vl.volume()</code></summary>
<p>Estimates the volume of the detected clusters, if the <code>rf_volume</code> option is enabled.</p>
</details>

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

- The [**RISKNAT research group**](http://www.ub.edu/risknat/) at the University of Barcelona for their past support of the doctoral research that laid the foundation for this software.
- The [**Technische Universität Dresden**](https://tu-dresden.de/) and [**Universitat Politècnica de Catalunya**](https://www.upc.edu/en) for their assistance with the project.
- The colleagues at the [**Juniorprofessur für Geosensorsysteme**](https://tu-dresden.de/bu/umwelt/geo/ipf/geosensorsysteme) (TU Dresden) for their cooperation and support.
- The [**ICGC**](http://www.icgc.cat/) (Institut Cartogràfic i Geològic de Catalunya) for funding this project.
- The [**CloudCompare**](https://www.danielgm.net/cc/) and [**Open3D**](http://www.open3d.org/) open-source communities for their incredible tools and libraries.

Additionally, the methodologies used in this software are based on the work developed in the following doctoral theses:

- Antonio Abellán (2010), Manuel Royán (2015), and Xabier Blanch (2023).

</details>

## License

<details>
<summary>Click to expand</summary>

This project is licensed under the **GNU General Public License (GPL)**. You are free to use, modify, and distribute this software under the terms of this license.

For more information, please refer to the [GPL License](https://www.gnu.org/licenses/gpl-3.0.en.html).

</details>