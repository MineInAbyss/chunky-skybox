# Chunky Skybox

## Generate chunky scene files:

Command

```skybox_scene_generator.py --deeper_world_config=/path/to/config.yml --worlds_dir=/path/to/folder/containing/all/worlds --output_dir=/path/where/you/want/resulting/file/structure```

Result will be a directory structure like so:

```
scene-dir
    |--city
    |   |--0.json
    |   |--1.json
    |   |--2.json
    |   |--3.json
    |
    |--l1s1
    |   |--0.json
```

You can change the width/height in `base_scene.json`. Keep in mind final skybox is 6x bigger than this.

## Run chunky script

This requires a custom chunky binary that does batch rendering. Its still pretty bad sooo yea. But it *does* reuse the
loaded chunks rather than reloading for all 6 camera angles.

```
skybox_generator.py --scene_dir=/output/path/from/last/run/sectionname
```

Run `skybox_generator.py --help` to see additional options such as desired spp / look above.

## Stitch results together

This takes output from the chunky renders, and makes a skybox image.

```
stitching.py --snapshot_dir=/output/path/from/last/run/sectionname/snapshots
```

Resulting image will be dropped in the snapshots folder.

## Repeat steps 2/3 for every single section lol