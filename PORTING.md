# Migration to Upstream COLMAP 4.x — Minimal Strategy

This branch (`sphere-sfm-v2`) is based on upstream COLMAP `main`. We are **not**
maintaining a hard fork. Instead, we use upstream's native spherical support and
standard workflows.

## Camera model change

| sphere-sfm fork | upstream COLMAP 4.x |
|---|---|
| Model name `SPHERE`, ID `11`, params `f, cx, cy` | Model name `EQUIRECTANGULAR`, ID `17`, params `w, h` |
| `Mapper.sphere_camera 1` flag | Not needed; detected automatically via `Camera::IsSpherical()` |

## Converting existing reconstructions

For text-format reconstructions:

```bash
python python/examples/convert_sphere_to_equirectangular.py \
    --input_path  /path/to/sphere-sfm-reconstruction \
    --output_path /path/to/upstream-ready-reconstruction
```

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

## Recommended spherical SfM workflows

### 1. Direct equirectangular reconstruction (fastest)

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

### 2. Perspective rig reconstruction from panoramas (most accurate)

Use upstream's official example:

```bash
python python/examples/panorama_sfm.py \
    --image_path ./images \
    --workspace_path ./workspace \
    --pano_render_type perspective_overlapping
```

This renders perspective virtual cameras from the panoramas and runs standard
pinhole SfM+MVS. It replaces the fork's `sphere_cubic_reprojecer` without any
custom C++ code.

## What we are NOT porting

We intentionally keep this branch free of custom C++ patches:

- **`sphere_cubic_reprojecer`**: Replaced by `panorama_sfm.py`.
- **`ImageReader.pose_path`**: Use upstream pose priors / `pose_prior_mapper`.
- **Custom `SPHERE` camera model**: Replaced by upstream `EQUIRECTANGULAR`.
- **`Mapper.sphere_camera` flag**: Replaced by automatic spherical detection.

No new enums, no new types, no new camera models. Standardize on upstream.

## Build notes

Build upstream COLMAP 4.x as usual:

```bash
mkdir build && cd build
cmake .. -GNinja -DCMAKE_BUILD_TYPE=Release -DGUI_ENABLED=OFF -DCUDA_ENABLED=OFF
ninja
```

See upstream documentation for full dependency instructions.
