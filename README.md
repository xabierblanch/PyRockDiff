# PyRockDiff - Automatic Change Detection for Rockfall Identification

## 🚀 Quick Overview

**PyRockDiff** is a Python-based pipeline that automates the comparison of two point clouds obtained from LiDAR or Structure-from-Motion (SfM), specifically targeting rock surfaces. It enables efficient geological change analysis with minimal user input.

### 🔑 Key Features

- **Automation**: Fully automated workflow requiring only a single configuration file.
- **User-Friendly Configuration**: Designed for ease of use, even without programming experience.
- **Preprocessing**: Cleans point clouds by removing noise and vegetation, and aligns them using robust registration algorithms.
- **Change Detection**: Identifies differences between two epochs using the M3C2 algorithm.
- **Clustering & Volume Calculation**: Detects and isolates changes with DBSCAN, and estimates volumes using alpha-shape triangulation

## 📖 Overview
<details>
<summary>Click to expand</summary>

**PyRockDiff** is a Python-based pipeline for automatically detecting changes in rock surfaces by comparing two point clouds obtained from LiDAR or Structure-from-Motion (SfM) data.

The process begins with essential pre-processing steps such as noise removal and vegetation filtering. It then aligns the point clouds using Fast Global Registration (FGR) and Iterative Closest Point (ICP) algorithms.

Change detection is performed using the M3C2 algorithm, followed by clustering of significant changes with DBSCAN. Finally, the volume of detected rockfalls is estimated using alpha-shape triangulation.

The pipeline is fully automated and user-friendly, requiring minimal input through a configuration file. It is designed to be accessible to users without programming experience and leverages open-source tools to promote transparency and collaboration.
</details>

## 🛠️ Installation & Requirements

<details>
<summary>Click to expand</summary>

### External Software

⚠️ **Note**: CloudCompare must be installed and accessible from the command line 

| Software/Library | License | Link |
|------------------|---------|------|
| CloudCompare      | GPL     | [CloudCompare Website](https://www.danielgm.net/cc/) |
#### ✅ Compatibility Checklist
- [x] Tested with CloudCompare 2.14.alpha
- [x] Tested with CloudCompare 2.13.2 (Kharkiv)

### Python Dependencies

All other dependencies are managed via Python and can be installed using the provided `requirements.txt` file.

#### ✅ Compatibility Checklist

- [x] Tested with Python 3.13
- [x] Tested with Python 3.12

### Installation
To set up the environment and install the required dependencies:

```bash
git clone https://github.com/xabierblanch/PyRockDiff.git
cd PyRockDiff
pip install -r requirements.txt
```
</details>

## ⚙️ How It Works

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

**⚠️ Preprocessing Recommendation:** Although PyRockDiff is designed to automatically process point clouds obtained via TLS, **preliminar "cleaning" is highly recommended** to optimize results.

**This "cleaning" may include:**
- Removing non-overlapping or inconsistent areas between different epochs
- Excluding parts of the scan that are not relevant to the specific study area
- Cropping the point clouds to the zone of interest

***

</details>

<details>

<summary><strong style="font-size:1.2em;">Workflow</strong></summary>

The code follows a sequential execution pattern, but it is flexible. You can start from any step in the workflow, provided the necessary files from earlier steps are supplied as inputs. This modular approach allows skipping steps that have been completed previously or executing the entire workflow from start to finish.

1. **Preprocessing**  
   - Transformation and subsampling (`transform_and_subsample`)  
   - Vegetation_filter (`vegetation_filter`)  
   - Statistical cleaning (`outlier_filter`)  


2. **Registration**  
   - FGR (`fgr`)  
   - ICP (`icp`)  


3. **Change Detection**  
   - M3C2 (`m3c2_distance`)  
   - DBSCAN clustering (`dbscan_clustering`)


4. **Volume Computation**
   - Volume Estimation (`volume_calculation`)

**Note**  
PyRockDiff always starts from two point-cloud epochs (`epoch1`, `epoch2`).  
If you skip any preprocessing or registration step, you must supply the corresponding intermediate files yourself.

***

</details>

<details>

<summary><strong style="font-size:1.2em;">Rockfall Identification vs. Prefailure Deformation </strong></summary>

***

</details>

<details>
<summary><strong style="font-size:1.2em;">Output Folder Structure</strong></summary>

The pipeline generates the following folder and file structure in the output directory:

```
📂 output_directory/

├── 1_XYZ_sub/
│   ├── epoch1_sub.xyz                  # Transformed & subsampled epoch1
│   └── epoch2_sub.xyz                  # Transformed & subsampled epoch2
│
├── 1.2_canupo/
│   ├── epoch1_canupo.xyz               # Vegetation-filtered epoch1 (rock points only)
│   └── epoch2_canupo.xyz               # Vegetation-filtered epoch2 (rock points only)
│
├── 1.3_clean/
│   ├── epoch1_clean.xyz                # Statistical outlier-filtered epoch1
│   └── epoch2_clean.xyz                # Statistical outlier-filtered epoch2
│
├── 2_registration/
│   ├── epoch1_reg.xyz                  # Registered epoch1
│   ├── epoch2_reg.xyz                  # Registered epoch2
│   └── *_REGISTRATION_MATRIX_*.txt     # Transformation matrices (timestamped)
│
├── 3_change_detection/
│   ├── epoch1_vs_epoch2_m3c2.xyz       # Full M3C2 results
│   ├── epoch1_vs_epoch2_threshold.xyz  # Filtered significant changes only
│   └── m3c2_auto_params.txt            # Auto-generated M3C2 parameters (if enabled)
│
├── 4_dbscan/
│   ├── epoch1_vs_epoch2_dbscan.xyz     # DBSCAN clustered rockfall points
│   ├── epoch1_vs_epoch2.jpg            # Cluster visualization (no vegetation)
│   └── epoch1_vs_epoch2_veg.jpg        # Cluster visualization (with vegetation context)
│
├── 5_volume/
│   ├── epoch1_vs_epoch2__db.csv        # Volume database with cluster statistics
│   ├── vol_plots/                      # 2D alpha-shape visualizations
│   │   ├── epoch1_vs_epoch2_0_Vol.png      # Cluster 0 alpha-shape plot
│   │   └── epoch1_vs_epoch2_N_Vol.png      # Additional clusters...
│   └── 3D_plots/                       # 3D surface comparison plots
│       ├── epoch1_vs_epoch2_0_3D.png       # Cluster 0 3D surface comparison
│       └── epoch1_vs_epoch2_N_3D.png       # Additional clusters...
│
├── log.txt                             # Complete processing log
└── config_used.json                    # Copy of configuration file used

```````

- Each folder corresponds to a processing stage.
- Intermediate and final results are saved in clearly named subfolders.
- The log file and a copy of the configuration used are stored at the root of the output directory.
</details>



## 🔧 Function Reference

The following **functions** can be enabled or configured in the JSON file. Each section provides a detailed description of the function's purpose, parameters, and usage instructions.

<details>
<summary>Transform and Subsample</summary>

**Transforms** and **Spatially Subsamples** the point clouds using CloudCompare. This step accomplishes two primary goals: converting input files to `.xyz` ASCII format and reducing point density through spatial subsampling.

#### How it works:

1. **Transformation to `.xyz` format**: Converts any input point cloud format supported by CloudCompare into `.xyz` ASCII files. During transformation, additional attributes such as RGB color, normals, and scalar fields are automatically removed to reduce file size and simplify downstream processing.


2. **Spatial Subsampling**: The point cloud is downsampled based on minimum spatial distance to reduce noise and balance point density between epochs. The `spatial_resolution` parameter (in meters) from the JSON configuration controls this minimum spacing between points in the output.

#### JSON file parameters:

| Parameter Name           | Type    | Example Value | JSON Section |
|--------------------------|---------|---------------|--------------|
| `transform_and_subsample` | Boolean | `true`        | options      |
| `spatial_resolution`      | Float   | `0.05`        | parameters   |

- **`transform_and_subsample`**: Toggle to enable or disable the transformation and subsampling step.
- **`spatial_resolution`**: Defines minimum spacing (in meters) between points for spatial subsampling.

***

</details>

<details>

<summary>Vegetation Filter</summary>

Applies **Vegetation Filtering** using the [CANUPO algorithm](https://nicolas.brodu.net/common/recherche/publications/canupo.pdf) (N. Brodu and D. Lague). CANUPO classifies point clouds by analyzing 3D geometric features at multiple scales to automatically separate vegetation from rock surfaces.

#### How it works:

1. **Classification**: The CANUPO algorithm integrates with CloudCompare to classify each point in the cloud based on its local 3D geometry at multiple scales. The classification uses a pre-trained `.prm` classifier file that defines the geometric signatures of different surface types.


2. **Filtering**: After classification, the algorithm extracts only points classified as **rock (class 1)** and saves them as a filtered point cloud. Vegetation and other classes are automatically removed from the dataset.

#### JSON file parameters:

| Parameter Name      | Type    | Example Value             | JSON Section |
|---------------------|---------|---------------------------|--------------|
| `vegetation_filter` | Boolean | `true`                    | options      |
| `canupo_file`       | Path    | `C:\\...\\classifier.prm` | paths        |

- **`vegetation_filter`**: Enables or disables the CANUPO vegetation filtering step.
- **`canupo_file`**: Path to the `.prm` classifier file containing the trained CANUPO model.

**⚠️ Critical Classification Requirements:**

When training your CANUPO classifier, ensure that:
- **Class 1 MUST be assigned to ROCK/BEDROCK surfaces**
- **Class 2 MUST be assigned to VEGETATION**

The pipeline automatically extracts Class 1 points as rock surfaces for geomorphological analysis. Incorrect class assignment will result in analysis of vegetation instead of rock surfaces.

**⚠️ The `.prm` file must be trained specifically for your study area to ensure optimal vegetation filtering and classification performance.**

***

</details>

<details>

<summary>Statistical Outlier Filter</summary>

Applies a **Statistical Outlier Filter** to remove noise and spurious points from the point cloud using Open3D's statistical outlier removal algorithm, enhancing data quality for downstream analysis.

#### How it works:

1. **Neighborhood Analysis**: For each point, the algorithm calculates distances to its `neighbors` nearest neighbors and computes the mean distance and standard deviation for the local neighborhood.


2. **Outlier Detection**: Points whose mean distance to neighbors exceeds `mean + (std_ratio × standard_deviation)` are classified as statistical outliers and removed from the dataset.


3. **Filtering**: The cleaned point cloud retains only the statistically consistent points, removing noise, measurement errors, and isolated spurious points.

#### JSON file parameters:

| Parameter Name     | Type    | Example Value | JSON Section |
|--------------------|---------|---------------|--------------|
| `outlier_filter`   | Boolean | `true`        | options      |
| `neighbors`        | Integer | `25`          | parameters   |
| `std_ratio`        | Float   | `1.5`         | parameters   |

- **`outlier_filter`**: Enables or disables the statistical outlier removal step.
- **`neighbors`**: Number of nearest neighbors used for statistical analysis (higher values = more robust but slower).
- **`std_ratio`**: Standard deviation multiplier threshold; lower values = more aggressive filtering.

**Technical Notes:**
- Uses Open3D's `remove_statistical_outlier()` implementation
- Typical `std_ratio` values: 1.0 (aggressive) to 2.0 (conservative)

***

</details>

<details>

<summary>Fast Global Registration (FGR)</summary>

Performs **Fast Global Registration (FGR)** to quickly align two point clouds based on geometric feature descriptors. This method provides robust initial alignment that serves as a starting point for more precise registration methods.

#### How it works:

1. **Multi-Scale Preprocessing**: Point clouds are voxel-downsampled at progressively finer scales and Fast Point Feature Histograms (FPFH) are computed for feature-based correspondence matching.


2. **Iterative Refinement**: The registration runs for the specified `fgr_iterations`, with automatically calculated voxel sizes:
   - **Iteration 1**: `8× spatial_resolution` (coarse alignment)
   - **Iteration 2**: `4× spatial_resolution` (medium refinement) 
   - **Iteration 3+**: `2× spatial_resolution` (fine alignment — only necessary if ICP registration fails to converge or requires additional refinement)


3. **Feature-Based Matching**: Uses FPFH descriptors and RANSAC-based correspondence estimation for robust registration even with partial overlap.


4. **Optional Visualization**: Real-time visualization of registration progress can be enabled for monitoring and validation.

   **⚠️ Caution:** Activating visualization will pause the automated workflow until each visualization window is manually closed, preventing fully automated batch processing.

#### JSON file parameters:

| Parameter Name       | Type    | Example Value | JSON Section |
|----------------------|---------|---------------|--------------|
| `fgr`                | Boolean | `false`       | options      |
| `fgr_visualization`  | Boolean | `false`       | options      |
| `fgr_iterations`     | Integer | `2`           | parameters   |

- **`fgr`**: Enables or disables the Fast Global Registration step.
- **`fgr_visualization`**: Shows intermediate registration results (disable for batch processing).
- **`fgr_iterations`**: Number of iterative refinements with progressively finer voxel scales.

**Technical Notes:**
- Uses Open3D's Fast Global Registration implementation
- Automatically saves transformation matrices with timestamp
- Voxel sizes are calculated from `spatial_resolution` - no manual voxel parameter needed
- Set `fgr_visualization: false` for headless/batch processing environments

***

</details>

<details>

<summary>Iterative Closest Point (ICP) Registration</summary>

Executes the **Iterative Closest Point (ICP)** algorithm to refine the alignment precision of two point clouds after initial registration (typically FGR). ICP provides high-precision refinement by iteratively minimizing point-to-point distances.

#### How it works:

1. **Precision Refinement**: ICP iteratively adjusts the transformation between two point clouds to minimize the distance between corresponding nearest points, achieving sub-millimeter accuracy.


2. **Iterative Process**: The algorithm runs for the specified number of iterations (`icp_iterations`), with each iteration progressively improving the alignment quality.


3. **CloudCompare Integration**: ICP is executed via CloudCompare's command-line interface with optimized parameters:
   - **Full overlap assumption** (100%)
   - **Large random sampling limit** for robust correspondence
   - **Farthest point removal** to eliminate outliers


#### JSON file parameters:

| Parameter Name    | Type    | Example Value | JSON Section |
|-------------------|---------|---------------|--------------|
| `icp`             | Boolean | `false`       | options      |
| `icp_iterations`  | Integer | `2`           | parameters   |

- **`icp`**: Enables or disables the ICP registration refinement step.
- **`icp_iterations`**: Number of iterative refinements to perform (typically 2-3 iterations provide optimal results).

**Performance Considerations:**
- ICP is computationally intensive; limit iterations to 2-3 for efficiency
- Works best after good initial alignment from FGR

***

</details>

<details>
<summary>M3C2 Change Detection</summary>

Computes precise **distances** between two point clouds using the [M3C2 algorithm](https://www.sciencedirect.com/science/article/abs/pii/S0924271613001184) (Lague et al., 2013). M3C2 measures distance changes along surface normals, providing robust change detection for geomorphological analysis.

#### How it works:

1. **Surface Normal Computation**: M3C2 estimates surface normals using a multi-scale approach. For each core point, normals are computed at multiple scales, and the scale that produces the flattest surface (most planar neighborhood) is selected for optimal orientation estimation.


2. **Automatic Parameter Configuration (Optional)**: 
   - When `auto_parameters_m3c2` is enabled, M3C2 parameters are automatically scaled based on `spatial_resolution`:
     - **SearchScale**: `4× spatial_resolution` (neighborhood for distance computation)  
     - **NormalMinScale**: `2× spatial_resolution` (minimum scale for multi-scale normals)
     - **NormalMaxScale**: `5× spatial_resolution` (maximum scale for multi-scale normals)
     - **NormalStep**: `1× spatial_resolution` (step between scales)
     
   - When `auto_parameters_m3c2` is disabled, uses parameters from the `m3c2_file` specified in the JSON file.


3. **Threshold Filtering (Mandatory)**: After M3C2 computation, all points are filtered using the `change_threshold` parameter. This step removes noise and stable areas and focuses analysis on significant changes. Points below the threshold are discarded, retaining only meaningful surface changes (negative values typically indicate erosion/rockfall).

#### JSON file parameters:

| Parameter Name        | Type    | Example Value              | JSON Section     |
|-----------------------|---------|----------------------------|------------------|
| `m3c2_distance`       | Boolean | `true`                     | options          |
| `m3c2_file`           | Path    | `C:\\...\\m3c2_params.txt` | paths            |
| `auto_parameters_m3c2`| Boolean | `true`                     | parameters/diff  |
| `change_threshold`    | Float   | `-0.05`                    | parameters/diff  |

- **`m3c2_distance`**: Enables or disables M3C2 change detection computation.
- **`m3c2_file`**: Path to the M3C2 parameter configuration file.
- **`auto_parameters_m3c2`**: Automatically optimizes M3C2 parameters based on data resolution. When enabled, overrides manual parameter settings.
- **`change_threshold`**: Distance threshold (meters) for filtering significant changes. Negative values detect surface lowering (erosion/rockfall).

**Technical Notes:**
- Updated M3C2 configuration is saved as `m3c2_auto_params.txt` when auto-parameters are enabled

***

</details>

<details>

<summary>DBSCAN Clustering</summary>

**Identifies Clusters** of significant surface changes (rockfalls) using the density-based spatial clustering algorithm [DBSCAN](https://scikit-learn.org/stable/modules/clustering.html#dbscan) (Ester et al., 1996). This step isolates meaningful change events while filtering out noise and isolated points.

#### How it works:

1. **Automatic Parameter Estimation (Optional)**: 
   When `auto_parameters_dbscan` is enabled, the algorithm automatically calculates optimal `eps` and `min_samples` parameters based on the point cloud's `spatial_resolution`. This overrides any manual parameter values specified in the JSON file.


2. **Density-Based Clustering**: 
   DBSCAN groups nearby points that exceed the density threshold (`min_samples` within `eps` radius) into clusters representing individual rockfall events. Points that don't meet the density criteria are classified as noise and removed.

#### JSON file parameters:

| Parameter Name          | Type    | Example Value | JSON Section | Description                                    |
|-------------------------|---------|---------------|--------------|------------------------------------------------|
| `dbscan_clustering`     | Boolean | `true`        | options      | Enables/disables DBSCAN clustering            |
| `auto_parameters_dbscan`| Boolean | `true`        | parameters   | Enables automatic parameter estimation         |
| `eps`                   | Float   | `0.3`         | parameters   | Neighborhood radius (meters)                   |
| `min_samples`           | Integer | `15`          | parameters   | Minimum points per cluster                     |

- **`dbscan_clustering`**: Enables or disables the DBSCAN clustering step.
- **`auto_parameters_dbscan`**: When enabled, automatically calculates `eps` and `min_samples` from spatial resolution, overriding manual values.
- **`eps`**: DBSCAN neighborhood radius in meters (used only when auto-parameters disabled).
- **`min_samples`**: Minimum points required to form a cluster (used only when auto-parameters disabled).

**Technical Notes:**
- Uses scikit-learn's DBSCAN implementation for robust clustering
- Automatic parameter estimation is based on point density analysis
- Two visualizations of the clusters are also saved in the output path
- Cluster labels are assigned sequentially starting from 0
- Noise points (label = -1) are automatically filtered from results

***

</details>

<details>

<summary>Volume Estimation</summary>

Estimates **Rockfall Volumes** for each detected cluster using [alpha-shape triangulation](https://en.wikipedia.org/wiki/Alpha_shape), a computational geometry method that generalizes convex hulls to capture concave geometries for volume calculations.

#### How it works:

1. **Automatic Alpha Parameter Estimation**: 
   For each cluster, the algorithm automatically calculates the optimal alpha parameter using k-nearest neighbor analysis: `α = 1/(typical_distance × 2)`, where typical distance is the 50th percentile of nearest neighbor distances.

2. **Alpha Shape Construction**: 
   Creates a 2D alpha shape from the cluster's X-Z projection to define the rockfall footprint.

3. **Constrained Delaunay Triangulation**: 
   Performs Delaunay triangulation of the cluster points, filtering triangles to keep only those whose centroids lie within the alpha shape boundary.

4. **Volume Calculation**: 
   Computes volume by integrating M3C2 surface differences over valid triangles: 
   `Volume = Σ(triangle_area × average_m3c2_difference)` for all valid triangles.

5. **Visualizations**:
   - **2D Alpha-Shape Plots**: Show triangulation with color-coded M3C2 differences
   - **3D Surface Comparison**: Display pre- and post-event topography

#### JSON file parameters:

| Parameter Name      | Type    | Example Value | JSON Section |
|---------------------|---------|---------------|--------------|
| `volume_calculation`| Boolean | `false`       | options      |

- **`volume_calculation`**: Enables volume estimation for detected rockfall clusters. Only executes if clusters are present from DBSCAN step.

**Technical Implementation:**
- Uses `alphashape` library for robust alpha-shape computation
- Applies `scipy.spatial.Delaunay` for triangulation

**Critical Validation Steps:**
- **Visual inspection mandatory**: Always review generated alpha-shape plots in `5_volume/vol_plots/`
- **Geometric validation**: Check 3D surface plots in `5_volume/3D_plots/` for reasonable surface reconstruction
- **Statistical review**: Examine CSV output for outlier volumes that may indicate calculation errors

**Potential Limitations:**
- **Alpha sensitivity**: Automatic parameter estimation may not be optimal for irregular cluster shapes
- **Complex concavities**: Deep indentations or fractures may not be captured accurately
- **Edge effects**: Boundary points may introduce artifacts in volume calculations

***

</details>


## 📋 JSON File (Configuration file)

The code follows a sequential execution pattern, but it is flexible. You can start from any step in the workflow, provided the necessary files from earlier steps are supplied as inputs. This modular approach allows skipping steps that have been completed previously or executing the entire workflow from start to finish.

<details>
<summary>Parameters Values</summary>
All processing parameters are defined in the configuration file (`config.json`), organized by processing stage:

| Parameter Name              | Type    | Example Value | Description                                                                                               |
|-----------------------------|---------|---------------|-----------------------------------------------------------------------------------------------------------|
| `spatial_resolution`        | Float   | `0.05`        | Spatial distance (meters) for point cloud subsampling; controls minimum spacing between points.         |
| `fgr_iterations`           | Integer | `2`           | **FGR:** Number of iterations to refine alignment progressively.                                         |
| `icp_iterations`           | Integer | `2`           | **ICP:** Number of iterations to refine registration precision.                                          |
| `neighbors`                | Integer | `25`          | **Outlier Filter:** Number of nearest neighbors used to calculate median distance.                      |
| `std_ratio`                | Float   | `1.5`         | **Outlier Filter:** Standard deviation multiplier; points beyond this threshold are removed.            |
| `auto_parameters_m3c2`     | Boolean | `true`        | **M3C2:** Auto-adjust parameters based on spatial resolution. If false, uses m3c2_params.txt in bin folder. |
| `change_threshold`         | Float   | `-0.05`       | Threshold (meters) to filter significant changes; negative values detect surface lowering (erosion/rockfalls). |
| `auto_parameters_dbscan`   | Boolean | `true`        | **DBSCAN:** Auto-calculate parameters, overriding eps and min_samples below.                            |
| `eps`                      | Float   | `0.3`         | **DBSCAN:** Neighborhood radius (meters); used only when auto_parameters_dbscan is false.              |
| `min_samples`              | Integer | `15`          | **DBSCAN:** Minimum points per cluster; used only when auto_parameters_dbscan is false.                |

**Important Notes:**
1. **Critical Parameter**: Many of the software's parameter values are derived using `spatial_resolution` as a starting point for calculations. If results are unsatisfactory or unexpected, we strongly recommend reviewing this parameter's value and ensuring its appropriateness for your specific dataset and analysis requirements.
2. **Units**: All spatial parameters are specified in **meters**.
3. **Change Detection**: Negative values of `change_threshold` indicate detection of surface lowering events such as erosion or rockfalls.
4. **Auto Parameters**: When enabled, auto-calculated parameters will override manual settings for M3C2 and DBSCAN.

</details>

<details>
<summary>Option Booleans</summary>

All main processing steps can be enabled or disabled via boolean flags. This allows flexible workflow control without code modification.

| Parameter Name            | Type    | Default Example | Description                                                       |
|---------------------------|---------|-----------------|-------------------------------------------------------------------|
| `transform_and_subsample` | Boolean | `false`         | Enable transformation to XYZ and spatial subsampling             |
| `vegetation_filter`       | Boolean | `false`         | Enable vegetation filtering using CANUPO                         |
| `outlier_filter`          | Boolean | `false`         | Enable statistical outlier removal                               |
| `fgr`                     | Boolean | `false`         | Enable Fast Global Registration (FGR)                            |
| `fgr_visualization`       | Boolean | `false`         | Enable visualization during FGR (disable for batch mode)        |
| `icp`                     | Boolean | `false`         | Enable Iterative Closest Point (ICP) registration               |
| `m3c2_distance`           | Boolean | `true`          | Enable M3C2 change detection                                     |
| `dbscan_clustering`       | Boolean | `true`          | Enable rockfall clustering (DBSCAN)                              |
| `volume_calculation`      | Boolean | `true`          | Enable volume estimation for detected clusters                   |

**Important Notes:**
- **JSON Format**: Boolean values must be written in lowercase and without quotes: `true` or `false`.  
- **Modular Design**: Each flag corresponds to a major processing step and can be toggled independently.
- **Batch Processing**: Set `fgr_visualization: false` for uninterrupted execution


**Warning:** The input files must be properly prepared for each enabled processing stage. Enabling a step without the required input data or pre-processing may result in errors or incomplete results.

***

</details>

<details>
<summary>Configuration Paths</summary>

All file and folder paths are defined in the configuration file (`_config.json`).

**Note:** On Windows systems, always use double backslashes (`\\`) in JSON strings to avoid path errors.

**Input Data Paths**

| Path Name | Description                                | Example Value                                              |
|-----------|--------------------------------------------|------------------------------------------------------------|
| `epoch1`      | Path to first input point cloud (epoch 1)  | `C:\...\PointClouds\epoch_1.xyz`                           |
| `epoch2`      | Path to second input point cloud (epoch 2) | `C:\...\PointClouds\epoch_2.xyz`                           |
| `m3c2_file`   | Path to M3C2 parameter file           | `.\\bin\\m3c2_params.txt`                     |
| `canupo_file`  | Path to CANUPO parameter file         | `.\\bin\\canupo.prm`                          |

**Output Path**

| Path Name   | Description                            | Example Value               |
|-------------|----------------------------------------|-----------------------------|
| `output_path`    | Output directory for processed results | `C:\...\PyRockDiff_Results` |

**CloudCompare Path**

| Path Name      | Description                           | Example Value                                 |
|----------------|---------------------------------------|-----------------------------------------------|
| `CloudCompare_path` | Path to CloudCompare executable       | `C:\Program Files\CloudCompare\cloudcompare.exe` |

***

</details>

## 🚧 Development stages & Future Updates

<details>
<summary>Planned Features</summary>

The following features and enhancements are planned for future versions of this software:

- [ ] Implement the software for pre-failure deformation identification
- [ ] Integrate tools from [**py4dgeo**](https://github.com/3dgeo-heidelberg/py4dgeo) (MIT License)
- [ ] Provide different approaches for volume calculation
- [ ] Add AI tools for vegetation filtering
- [ ] Add AI tools to filter the wrong clusters (Blanch et al, 2020)
- [ ] Include and process RGB data (for LiDAR or SfM Point Clouds)

</details>

## 📬 Contact

For questions, issues, or further information regarding this software, feel free to reach out to the authors:

- **Xabier Blanch**: xabier.blanch@upc.edu

## 🙏 Acknowledgments

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

## 📝 License

This project is licensed under the **GNU General Public License (GPL)**. You are free to use, modify, and distribute this software under the terms of this license.

For more information, please refer to the [GPL License](https://www.gnu.org/licenses/gpl-3.0.en.html).