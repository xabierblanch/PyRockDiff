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
  - [Input Data](#input-data)
  - [Workflow](#workflow)
  - [Function Reference](#function-reference)
  - [JSON File (Configuration file)](#json-file-configuration-file)
    - [Configuration Values](#configuration-values)
    - [Configuration Booleans](#configuration-booleans)
    - [Configuration Paths](#configuration-paths)
  - [Output Folder Structure](#output-folder-structure)
- [Development Stages & Future Updates](#development-stages--future-updates)
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

<details>
<summary><strong style="font-size:1.2em;">Input Data</strong></summary>

The code requires specific input formats and parameters to execute successfully:

- **Supported Point Cloud Formats**:
  - `.ply` (Polygon File Format)
  - `.las` (LASer format)
  - `.xyz` (ASCII Point Cloud)
  - `.txt` (Custom ASCII format)
  

- A pre-defined parameters and paths file: `xxx.JSON` file.
 
**Critical Note:** All point clouds must share the same coordinate reference system (CRS) and units (meters recommended).
</details>
<br>
<details>
<summary><strong style="font-size:1.2em;">Workflow</strong></summary>

The code follows a sequential execution pattern, but it is flexible. You can start from any step in the workflow, provided the necessary files from earlier steps are supplied as inputs. This modular approach allows skipping steps that have been completed previously or executing the entire workflow from start to finish.

1. **Preprocessing**  
   - Transformation and subsampling (`transform_and_subsample`)  
   - Vegetation filtering (`vegetation_filter`)  
   - Statistical cleaning (`cleaning_filtering`)  


2. **Registration**  
   - FGR (`fast_registration`)  
   - ICP (`icp_registration`)  


3. **Change Detection**  
   - M3C2 (`m3c2_dist`)  
   - DBSCAN clustering (`autoparameters` & `rf_clustering`)


4. **Volum Computation**
   - Volume Estimation (`rf_volume`)
</details>
<br>
<details>
<summary><strong style="font-size:1.2em;">Function Reference</strong></summary>
<br>
<details>
<summary>Transform and Subsample</summary>

Transform and subsample the point clouds using CloudCompare. This step of the pipeline handles two main objectives: to convert the original point cloud from any format accepted by CloudCompare to an .xyz format and to perform spatial subsampling to reduce and equalise the number of points in the two clouds to be compared.
#### How it works:
1. **Transformation to `.xyz` format**: Converts the input point cloud to the `.xyz` format for streamlined processing in subsequent steps. During this transformation, additional attributes such as color (RGB), normals, and scalar fields are removed to reduce file size and complexity.

   
2. **Subsampling**: The point cloud is spatially subsampled to reduce point density while maintaining overall structure. The `spatial_distance` parameter (in meters), defined in the configuration `.JSON` file, controls the minimum spacing between points in the output cloud.
#### JSON file parameters:
| Parameter Name              | Type        | Example Value                                         | JSON Section     |
|-----------------------------|-------------|-------------------------------------------------------|-------------------|
| `transform_and_subsample`    | Boolean    | `true`                                                | options           |
| `spatial_distance`           | Float (cm) | `0.05`                                                | parameters        |

- **`transform_and_subsample`**: Enables or disables the transformation and subsampling step.
- **`spatial_distance`**: Specifies the minimum distance (in meters) between points for subsampling.
</details>

<details>
<summary>Vegetation Filter</summary>

Applies a vegetation filter using [CANUPO workflow](https://nicolas.brodu.net/common/recherche/publications/canupo.pdf) (N. Brodu and D. Lague). This consist in a simple yet efficient way to automatically classify a point cloud

#### How it works:
1. **Vegetation Filtering**: The CANUPO algorithm identifies and filters vegetation points from the input point cloud. The algorithm is integrated in the CloudCompare software and requires a `.prm` file corresponding to the classifier. A classifier for vegetation is included with the software but the user can create his own ‘.prm’ files using CloudCompare's CANUPO suite. The resulting filtered point cloud is saved in `.xyz` format for further analysis.

#### JSON file parameters:
| Parameter Name          | Type    | Example Value                                         | JSON Section |
|-------------------------|---------|-------------------------------------------------------|--------------|
| `vegetation_filter`     | Boolean | `true`                                                | options      |
| `canupo_file`           | String  | `".\\bin\\canupo.prm"`                                | paths        |

- **`vegetation_filter`**: Enables or disables the vegetation filtering step.
- **`canupo_file`**: Path to the `.prm` file with the classifier

</details>

<details>
<summary>Cleaning Filter</summary>


Applies a statistical outlier filter to remove noise from the point cloud. This step helps enhance the quality of the data by eliminating points that are statistically different from their neighbors, ensuring more accurate analysis in subsequent steps.

#### How it works:
1. **Statistical Outlier Removal**: The outlier filter evaluates each point in the point cloud based on the distance to its neighbors. Points that have a significantly different distance compared to their local neighborhood are removed. The `nb_neighbors` parameter defines the number of neighboring points to consider, while the `std_ratio` parameter specifies the threshold for determining outliers.

#### JSON file parameters:
| Parameter Name              | Type      | Example Value                                         | JSON Section     |
|-----------------------------|-----------|-------------------------------------------------------|-------------------|
| `cleaning_filtering`           | Boolean   | `true`                                                | options           |
| `nb_neighbors_f`            | Integer   | `10`                                                 | parameters        |
| `std_ratio_f`               | Float (m) | `1.5`                                                | parameters        |

- **`cleaning_filtering`**: Enables or disables the application of the statistical outlier filter.
- **`nb_neighbors_f`**: Specifies the number of neighbors to consider for the statistical analysis.
- **`std_ratio_f`**: Defines the standard deviation multiplier used to identify outliers.
</details>

<details>
<summary>Fast Global Registration</summary>

Performs Fast Global Registration (FGR), if the <code>fast_registration</code> option is enabled. This method quickly aligns two point clouds based on their features, with the `voxel_size` parameter used to downsample the point clouds, and the registration refined through multiple iterations defined by the `ite_FGR` parameter.

#### JSON file parameters:
| Parameter Name              | Type        | Example Value                                         | JSON Section     |
|-----------------------------|-------------|-------------------------------------------------------|-------------------|
| `fast_registration`         | Boolean     | `true`                                                | options           |
| `voxel_size`               | Float       | `0.25`                                               | parameters        |
| `ite_FGR`                   | Integer     | `3`                                                  | parameters        |

- **`fast_registration`**: Enables or disables the application of the Fast Global Registration algorithm.
- **`voxel_size`**: Specifies the size of the voxel for downsampling the point clouds before registration.
- **`ite_FGR`**: Defines the number of iterations for the Fast Global Registration algorithm.

</details>

<details>
<summary>ICP Registration</summary>

Executes ICP (Iterative Closest Point) registration, if the <code>icp_registration</code> option is enabled. After initial alignment with FGR, ICP enhances the precision of the registration by iteratively minimizing the distance between corresponding points, using the `ite_ICP` parameter to specify the number of refinement iterations.

#### JSON file parameters:
| Parameter Name              | Type        | Example Value                                         | JSON Section     |
|-----------------------------|-------------|-------------------------------------------------------|-------------------|
| `icp_registration`          | Boolean     | `true`                                                | options           |
| `ite_ICP`                   | Integer     | `3`                                                  | parameters        |

- **`icp_registration`**: Enables or disables the application of the Iterative Closest Point algorithm.
- **`ite_ICP`**: Defines the number of iterations for the Iterative Closest Point algorithm.
</details>

<details>
<summary>ROI Focus</summary>

#### ROI Focus
<p>Performs Region of Interest (ROI) clipping on the point clouds, if the <code>roi_focus</code> option is enabled.</p>
</details>

<details>
<summary>M3C2 Change Detection</summary>

Calculates the differences between two point clouds using the **[M3C2 algorithm](https://www.sciencedirect.com/science/article/abs/pii/S0924271613001184)** (Lague et al., 2013) if the <code>m3c2_computation</code> option is enabled. This algorithm quantifies changes by analyzing the point clouds from different epochs, leveraging the specified parameters for optimal results.

Calculates differences using the 
#### JSON file parameters:
| Parameter Name              | Type        | Example Value                                         | JSON Section     |
|-----------------------------|-------------|-------------------------------------------------------|-------------------|
| `m3c2_dist`                 | Boolean     | `true`                                                | options           |
| `m3c2_param`                | Path        | `.\\bin\\m3c2_params.txt`                            | paths             |

- **`m3c2_dist`**: Enables or disables the application of the M3C2 algorithm to compute differences.
- **`m3c2_param`**: Path to the file containing parameters for the M3C2 calculation.</details>

<details>
<summary>Autoparameters</summary>

#### Auto MinPts estimation (for DBSCAN)
Calculates point density to estimate the `min_samples_rockfalls` parameter for DBSCAN algorithm **when the <code>auto_parameters</code> option is enabled**. Automatically estimates this parameter based on local point density and user-defined `eps_rockfalls`.  

**Important:** When enabled, the auto-calculated value **overrides** any manual entry of `min_samples_rockfalls` in the JSON file.
#### How it works:
1. **Density Calculation**  
   Computes local point density using CloudCompare's `-DENSITY` command with a spherical kernel (radius = 0.25 m):  
   `density = (points in sphere) / (π × r²)`  
   where r = 0.25 m


2. **Spatial Distance Estimation**  
   Derives average point spacing from density:  
   `spacing = √(1 / density)`


3. **MinPts Calculation**  
   Estimates minimum cluster size using safety factor (0.9):  
   `min_samples = ⎡density × π × eps² × 0.9⎤`  


#### JSON file parameters:
| Parameter Name          | Type    | Example Value | JSON Section | Description                              |
|-------------------------|---------|---------------|--------------|------------------------------------------|
| `auto_parameters`       | Boolean | `true`        | options      | Enables automatic parameter estimation    |
| `eps_rockfalls`         | Float   | `0.3`         | parameters   | Neighborhood radius (meters)             |

⚠️ **Key Limitations:** ⚠️

**This method is sensitive to:**  
- Significant density variations within the point cloud  
- Complex geometries (e.g., fractures, overhangs)  
- Discrepancies between `eps_rockfalls` and target sizes  

**Disable auto-estimation** and use manual values if: 
   - Clusters include obvious noise (increase `min_samples_rockfalls`)  
   - Valid rockfalls are missed (decrease `min_samples_rockfalls`)  

</details>

<details>
<summary>Rockfall clustering (DBSCAN)</summary>

Clusters detected changes using **[DBSCAN](https://scikit-learn.org/stable/modules/clustering.html#dbscan)** density-based spatial clustering. This step isolates significant rockfall events while filtering sparse noise points.

#### JSON file parameters:
| Parameter Name          | Type    | Example Value | JSON Section | Description                              |
|-------------------------|---------|---------------|--------------|------------------------------------------|
| `rf_clustering`         | Boolean | `true`        | options      | Enables/disables DBSCAN clustering       |
| `eps_rockfalls`         | Float   | `0.3`         | parameters   | Neighborhood radius (meters)            |
| `min_samples_rockfalls` | Integer | `15`          | parameters   | Minimum points per cluster               |
| `diff_threshold`        | Float   | `-0.05`       | parameters   | Pre-filtering threshold (meters)         |

**Technical Notes:**  
- Uses `scikit-learn` implementation of DBSCAN (Ester et al., 1996)  

</details>

<details>
<summary>Volume Estimation</summary>


Estimates rockfall volumes using **[alpha-shape triangulation](https://en.wikipedia.org/wiki/Alpha_shape)**  if the <code>rf_volume</code> option is enabled. This computational geometry method that generalizes convex hulls to capture concave geometries.
#### How it works:
1. **Alpha-shape Calculation**:  
   - Automatically estimates optimal `alpha` parameter using point density.  
   - Constructs alpha-shape to model rockfall geometry.


2. **Volume Computation**:  
   - Calculates volume via Delaunay triangulation of alpha-shape.  
   - Accounts for 3D surface differences from M3C2 results

#### JSON file parameters:
| Parameter Name       | Type    | Example Value | JSON Section | Description                          |
|----------------------|---------|---------------|--------------|--------------------------------------|
| `rf_volume`          | Boolean | `true`        | options      | Enables volume estimation     

**Technical Notes:**  
- **Alpha Sensitivity**: Volume accuracy depends on α value. Small α → underfitting (holes), large α → over-convex shapes.  
- **Validation Critical**: Always inspect generated alpha-shapes visually (plots in `5_volume/` folder).  

**Alpha-shapes may produce inaccurate volumes if:**  
- Point density varies significantly within a cluster.  
- Rockfalls have complex concavities not captured by automatic α estimation.  
- Erosion scars exhibit irregular geometries (e.g., elongated fractures).  

</details>
</details>

<br>
<details>
<summary><strong style="font-size:1.2em;">JSON File (Configuration file)</strong></summary>

The code follows a sequential execution pattern, but it is flexible. You can start from any step in the workflow, provided the necessary files from earlier steps are supplied as inputs. This modular approach allows skipping steps that have been completed previously or executing the entire workflow from start to finish.

<details>
<summary>Configuration Values</summary>

All processing parameters are defined in the configuration file (`_config.json`)

| Parameter Name              | Type    | Example Value | Processing Stage                                              |
|-----------------------------|---------|---------------|---------------------------------------------------------------|
| `spatial_distance`          | Float   | `0.05`        | Spatial distance for Point cloud subsampling                  |
| `voxel_size`                | Float   | `0.25`        | Voxel-size automatic subsampling for Fast Global Registration |
| `ite_FGR`                   | Integer | `2`           | Fast Global Registration (FGR) Iterations                     |
| `ite_ICP`                   | Integer | `3`           | Iterative Closest Point (ICP) Iterations                      |
| `diff_threshold`            | Float   | `-0.05`       | Change-detection threshold                                    |
| `eps_rockfalls`             | Float   | `0.3`         | DBSCAN clustering (ε)                                         |
| `min_samples_rockfalls`     | Integer | `15`          | Minimum cluster size                                          |
| `nb_neighbors_f`            | Integer | `10`          | Outlier removal (neighbors)                                   |
| `std_ratio_f`               | Float   | `1.5`         | Statistical outlier filtering                                 |
1. **Units**: All spatial parameters (`spatial_distance`, `voxel_size`, etc.) are in **meters**
2. **Change Detection**: Negative `diff_threshold` detects surface lowering (erosion/rockfalls)
</details>

<details>
<summary>Configuration Booleans</summary>

All main processing steps can be enabled or disabled via boolean flags in the configuration file. This allows the user to flexibly control the workflow without modifying the code.

| Parameter Name             | Type    | Default Example | Description                                                       |
|----------------------------|---------|-----------------|-------------------------------------------------------------------|
| `transform_and_subsample`  | Boolean | `true`          | Enable transformation to XYZ and spatial subsampling              |
| `vegetation_filter`        | Boolean | `true`          | Enable vegetation filtering using CANUPO                          |
| `cleaning_filtering`          | Boolean | `true`          | Enable statistical outlier removal                                |
| `fast_registration`        | Boolean | `true`          | Enable Fast Global Registration (FGR)                             |
| `icp_registration`         | Boolean | `true`          | Enable Iterative Closest Point (ICP) registration                 |
| `roi_focus`                | Boolean | `false`         | Enable Region of Interest (ROI) cropping                          |
| `m3c2_dist`                | Boolean | `true`          | Enable M3C2 change detection                                      |
| `auto_parameters`          | Boolean | `false`         | Automatically estimate DBSCAN parameters                          |
| `rf_clustering`            | Boolean | `true`          | Enable rockfall clustering (DBSCAN)                               |
| `rf_volume`                | Boolean | `true`          | Enable volume estimation for detected clusters                    |

**Note:** In JSON, boolean values must be written in lowercase and without quotes: `true` or `false`.  
Each flag corresponds to a major processing step and can be toggled independently.

**Warning:** The input files must be properly prepared for each enabled processing stage. Enabling a step without the required input data or pre-processing may result in errors or incomplete results.
</details>

<details>
<summary>Configuration Paths</summary>

All file and folder paths are defined in the configuration file (`_config.json`).

**Note:** On Windows systems, always use double backslashes (`\\`) in JSON strings to avoid path errors.

**Input Data Paths**

| Path Name | Description                                | Example Value                                              |
|-----------|--------------------------------------------|------------------------------------------------------------|
| `e1`      | Path to first input point cloud (epoch 1)  | `C:\...\PointClouds\epoch_1.xyz`                           |
| `e2`      | Path to second input point cloud (epoch 2) | `C:\...\PointClouds\epoch_2.xyz`                           |
| `e1_e2`   | Path to M3C2 change detection results      | `C:\...\PointClouds\epoch1_vs_epoch2_m3c2.xyz` |
| `m3c2_param`   | Path to M3C2 parameter file           | `.\\bin\\m3c2_params.txt`                     |
| `canupo_file`  | Path to CANUPO parameter file         | `.\\bin\\canupo.prm`                          |

**Output Path**

| Path Name   | Description                            | Example Value                                   |
|-------------|----------------------------------------|------------------------------------------------|
| `output`    | Output directory for processed results | `C:\Users\Xabier\Desktop\PyRockDiff_ICGCData`   |

**CloudCompare Path**

| Path Name      | Description                           | Example Value                                 |
|----------------|---------------------------------------|-----------------------------------------------|
| `CloudCompare` | Path to CloudCompare executable       | `C:\Program Files\CloudCompare\cloudcompare.exe` |

</details>
</details>
<br>
<details>
<summary><strong style="font-size:1.2em;">Output Folder Structure</strong></summary>

The pipeline generates the following folder and file structure in the output directory:

```
📂 output_directory/

├── 1_XYZ_sub/
│ ├── epoch1_sub.xyz
│ └── epoch2_sub.xyz
│
├── 1.2_canupo/
│ ├── epoch1_canupo.xyz
│ └── epoch2_canupo.xyz
│
├── 1.3_clean/
│ ├── epoch1_clean.xyz
│ └── epoch2_clean.xyz
│
├── 2_registration/
│ ├── epoch1_reg.xyz
│ └── epoch2_reg.xyz
│
├── 3_change_detection/
│ └── epoch1_vs_epoch2_m3c2.xyz
│
├── 4_dbscan/
│ └── epoch1_vs_epoch2_dbscan.xyz
│
├── 5_volume/
│ └── volumes.csv
│
├── log.txt
└── config_used.json
```````

- Each folder corresponds to a processing stage.
- Intermediate and final results are saved in clearly named subfolders.
- The log file and a copy of the configuration used are stored at the root of the output directory.
</details>

## Development stages & Future Updates

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

For questions, issues, or further information regarding this software, feel free to reach out to the authors:

- **Xabier Blanch**: xabier.blanch@upc.edu

## Acknowledgments

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

## License

This project is licensed under the **GNU General Public License (GPL)**. You are free to use, modify, and distribute this software under the terms of this license.

For more information, please refer to the [GPL License](https://www.gnu.org/licenses/gpl-3.0.en.html).
