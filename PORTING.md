# Migration to Upstream COLMAP 4.x

This branch (`sphere-sfm-v2`) is based on upstream COLMAP `main` and replaces the
old COLMAP 3.8 hard fork. The core spherical-SfM functionality that motivated the
fork is now native upstream as the `EQUIRECTANGULAR` camera model (merged in PR
[#4441](https://github.com/colmap/colmap/pull/4441)).

## What changed in the camera model

| | sphere-sfm fork | upstream COLMAP 4.x |
|---|---|---|
| Model name | `SPHERE` | `EQUIRECTANGULAR` |
| Model ID | `11` | `17` |
| Parameters | `f, cx, cy` | `w, h` (image dimensions only) |
| Pipeline flag | `Mapper.sphere_camera 1` | automatic via `Camera::IsSpherical()` |

## Converting existing reconstructions

Use the provided Python script for **text-format** reconstructions:

```bash
python scripts/convert_sphere_to_equirectangular.py \
    --input_path  /path/to/sphere-sfm-reconstruction \
    --output_path /path/to/upstream-ready-reconstruction
```

The script rewrites `cameras.txt` (`SPHERE` → `EQUIRECTANGULAR`) and copies
`images.txt` / `points3D.txt` unchanged.

If your reconstruction is binary, first convert it to text with the old
sphere-sfm binary:

```bash
colmap model_converter \
    --input_path  /path/to/sphere-sfm-reconstruction \
    --output_path /path/to/text-reconstruction \
    --input_type  bin \
    --output_type txt
```

Then run the Python converter above.

## Running spherical SfM with upstream COLMAP

The `python/examples/panorama_sfm.py` script in upstream COLMAP demonstrates the
new workflow. The equivalent CLI workflow is:

```bash
colmap feature_extractor \
    --database_path ./colmap/database.db \
    --image_path ./images \
    --ImageReader.camera_model EQUIRECTANGULAR \
    --ImageReader.single_camera 1

colmap spatial_matcher \
    --database_path ./colmap/database.db \
    --SiftMatching.max_error 4 \
    --SiftMatching.min_num_inliers 50

colmap mapper \
    --database_path ./colmap/database.db \
    --image_path ./images \
    --output_path ./colmap/sparse
```

No `--Mapper.sphere_camera` option is required; upstream detects spherical
cameras automatically and uses bearing-vector geometry.

## Fork features still to port

The following sphere-sfm features are **not yet in upstream COLMAP** and must be
ported if they are still needed:

### 1. `sphere_cubic_reprojecer` / `ExportPerspectiveCubic`

The fork provides a command that exports a spherical reconstruction as six
perspective cube-face images per panorama:

```bash
colmap sphere_cubic_reprojecer \
    --image_path ./images \
    --input_path ./colmap/sparse/0 \
    --output_path ./colmap/sparse-cubic
```

Upstream has no equivalent command. A 4.x implementation would:

- Read the spherical reconstruction (`src/colmap/scene/reconstruction_io_text.h`).
- For each registered spherical image, generate six pinhole views using the cubic
  face rotations from the old `src/base/sphere_camera.cc`.
- Use `WarpImageBetweenCameras` (`src/colmap/image/warp.h`) or a custom tangent
  projection to resample the ERP image onto each pinhole camera.
- Write the resulting perspective images and a new reconstruction with trivial
  rigs/frames (`AddCameraWithTrivialRig`, `AddImageWithTrivialFrame`).
- Register the new command in `src/colmap/exe/colmap.cc` (or add it to
  `src/colmap/exe/model.cc`) and wire it into `src/colmap/exe/CMakeLists.txt`.

### 2. `ImageReader.pose_path`

The fork added `--ImageReader.pose_path` to inject external POS data during
feature extraction. Upstream does not have this option. Possible alternatives:

- Import pose priors via `pose_prior_mapper` or the new sensor/pose-prior APIs.
- Re-implement the option in `src/colmap/controllers/option_manager.cc` and
  `src/colmap/feature/extraction.cc` if the exact workflow must be preserved.

### 3. Spherical error-threshold helpers

Functions such as `ImagePlaneToSpherePlaneError` in the old
`src/base/sphere_camera.cc` are no longer needed; upstream normalizes errors via
`Camera::CamFromImgThreshold` and the bearing-vector cost functions.

## Build notes

This branch requires the standard upstream COLMAP 4.x build dependencies
(vcpkg/conda, Ceres, Eigen, OpenImageIO, etc.). On Windows without an existing
vcpkg installation, run:

```bash
mkdir build && cd build
cmake .. -GNinja -DCMAKE_BUILD_TYPE=Release -DGUI_ENABLED=OFF -DCUDA_ENABLED=OFF
ninja
```

If CMake cannot find dependencies, install them through vcpkg first (see
upstream COLMAP build documentation).
