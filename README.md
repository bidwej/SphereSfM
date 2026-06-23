# SphereSfM on upstream COLMAP 4.x

This repository is being migrated from a hard fork of COLMAP 3.8 to a branch
based on upstream COLMAP 4.x (`main`).

## Why migrate?

The spherical (360° ERP) SfM functionality that SphereSfM originally added to
COLMAP 3.8 is now native upstream as the `EQUIRECTANGULAR` camera model
([PR #4441](https://github.com/colmap/colmap/pull/4441)). Maintaining a separate
hard fork is no longer necessary for the core feature, and upstream receives
ongoing bug fixes, performance improvements, and new algorithms.

## Status

- [x] Branch `sphere-sfm-v2` created from upstream COLMAP `main`.
- [x] `SPHERE` → `EQUIRECTANGULAR` converter script (`scripts/convert_sphere_to_equirectangular.py`).
- [ ] Port `sphere_cubic_reprojecer` / cubic perspective export.
- [ ] Port `ImageReader.pose_path` if still required.
- [ ] Build verification and regression tests.

See [`PORTING.md`](PORTING.md) for the full migration guide and remaining work.

## Quick start

Convert an existing sphere-sfm reconstruction:

```bash
python scripts/convert_sphere_to_equirectangular.py \
    --input_path  /path/to/sphere-sfm-reconstruction \
    --output_path /path/to/upstream-ready-reconstruction
```

Run spherical SfM with upstream COLMAP:

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

For a Python reference, see upstream's `python/examples/panorama_sfm.py`.

## Original SphereSfM

The original sphere-sfm code (COLMAP 3.8 fork) remains available on the
`origin/main` branch and at https://github.com/json87/spheresfm.git.
