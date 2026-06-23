# SphereSfM on upstream COLMAP 4.x

This repository is a migration of SphereSfM from a hard fork of COLMAP 3.8 to a
lightweight branch based on upstream COLMAP `main`.

## Why migrate?

The spherical (360° ERP) SfM functionality that SphereSfM originally added to
COLMAP 3.8 is now native upstream as the `EQUIRECTANGULAR` camera model
([PR #4441](https://github.com/colmap/colmap/pull/4441)). Maintaining a separate
hard fork is no longer necessary for the core feature.

This branch uses **only upstream types and workflows** — no custom camera models,
no custom enums, no C++ patches.

## Quick start

### Convert an existing sphere-sfm reconstruction

```bash
python scripts/convert_sphere_to_equirectangular.py \
    --input_path  /path/to/sphere-sfm-reconstruction \
    --output_path /path/to/upstream-ready-reconstruction
```

### Direct spherical SfM

```bash
colmap feature_extractor \
    --database_path ./colmap/database.db \
    --image_path ./images \
    --ImageReader.camera_model EQUIRECTANGULAR \
    --ImageReader.single_camera 1

colmap spatial_matcher --database_path ./colmap/database.db

colmap mapper \
    --database_path ./colmap/database.db \
    --image_path ./images \
    --output_path ./colmap/sparse
```

### Perspective-from-panorama SfM

```bash
python python/examples/panorama_sfm.py \
    --image_path ./images \
    --workspace_path ./workspace \
    --pano_render_type perspective_overlapping
```

## Migration details

See [`PORTING.md`](PORTING.md).

## Original SphereSfM

The original sphere-sfm code (COLMAP 3.8 fork) remains available on
`origin/main` and at https://github.com/json87/spheresfm.git.
