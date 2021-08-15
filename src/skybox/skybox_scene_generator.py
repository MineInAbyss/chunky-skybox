import argparse
import json
import math
import pathlib

import yaml
import os
import operator
import copy


# Generate the chunks that should be in the render
def generate_chunks(x1, z1, x2, z2):
    # return [[1,1]]
    x1c = math.floor(x1 / 16)
    z1c = math.floor(z1 / 16)
    x2c = math.ceil(x2 / 16)
    z2c = math.ceil(z2 / 16)

    lst = []

    # Could use zip
    for x in range(x1c, x2c + 1):
        for z in range(z1c, z2c + 1):
            lst.append([x, z])

    return lst


def convert_to_central(prev_center, prev_ref, own_ref):
    delta = map(operator.sub, own_ref, prev_ref)

    return [*map(operator.add, prev_center, delta)]


base_scene_path = 'base_scene.json'

with open(base_scene_path) as fp:
    base_scene = json.load(fp)

skybox_orientations = {
    "skybox_east": {
        "roll": 0.0,
        "pitch": -1.5707963267948966,
        "yaw": 3.141592653589793
    },

    "skybox_west": {
        "roll": 0.0,
        "pitch": -1.5707963267948966,
        "yaw": 0.0
    },
    "skybox_north": {
        "roll": 0.0,
        "pitch": -1.5707963267948966,
        "yaw": -1.5707963267948966
    },
    "skybox_south": {
        "roll": 0.0,
        "pitch": -1.5707963267948966,
        "yaw": 1.5707963267948966
    }
}

vertical_orientations = {
    "skybox_down": {
        "roll": 0.0,
        "pitch": 0.0,
        "yaw": -1.5707963267948966
    },
    "skybox_up": {
        "roll": 0.0,
        "pitch": math.pi,
        "yaw": -1.5707963267948966
    }
}


class Section:
    def __init__(self, data):
        self._data = data
        self.world = data["world"]
        self.region = data["region"]
        self.name = data["name"]
        self.above = None
        self.below = None
        self.refTop = data["refTop"]
        self.refBottom = data["refBottom"]

    def __repr__(self):
        a = self.above.name if self.above else None
        b = self.below.name if self.below else None

        return "{}->[{}]->{}".format(a, self.name, b)


# Fun fact. None of the chunks loaded for one sections skybox
# are guaranteed to be needed for the next :)
# TODO top and bottom of boxes are a pain
def get_needed_scenes(section, worlds_dir: pathlib.Path, scenes_dir: pathlib.Path, y1: int):
    # First get the standard scenes:

    # TODO I would like to make an option to render by offsetting to get center coordinates
    # Generate skybox by finding its position relative to the top-most skybox
    # center_x = section.refTop[0]  # get the x and z coordinates of this section's refTop
    # center_y = section.refTop[2]

    # next_section = section.get_above()  # this doesn't work right now because section.above returns above->current->below and not the actual section
    # while next_section is not None:
    #     center_x -= next_section.refBottom[0]
    #     center_y -= next_section.refBottom[2]
    #     next_section = section.get_above()

    # generate skybox by finding center of region
    center_x = (section.region[0] + section.region[2]) / 2
    center_y = (section.region[1] + section.region[3]) / 2
    camera_pos = {
        "x": center_x,
        "y": y1,
        "z": center_y
    }

    root = scenes_dir / section.name

    try:
        os.mkdir(root)
    except Exception:
        pass

    generate_multi_camera(section, 0, camera_pos, root, ["skybox_up", "skybox_down"], worlds_dir)

    current = section
    below = section.below
    center_to_translate = (center_x, y1, center_y)

    index = 1

    while below:
        center_to_translate = convert_to_central(center_to_translate, current.refBottom, below.refTop)
        x, y, z = center_to_translate

        camera_pos = {
            "x": x,
            "y": y,
            "z": z
        }

        if index > 3:  # Only 3 scenes below
            break

        generate_multi_camera(below, index, camera_pos, root, ["skybox_down"], worlds_dir)

        index += 1
        current = below
        below = current.below

    current = section
    above = section.above
    center_to_translate = (center_x, y1, center_y)
    print(current)

    index = -1

    while above:
        center_to_translate = convert_to_central(center_to_translate, current.refTop, above.refBottom)
        x, y, z = center_to_translate

        camera_pos = {
            "x": x,
            "y": y,
            "z": z
        }

        if index < -3:  # Only 3 scenes above
            break
        generate_multi_camera(above, index, camera_pos, root, ["skybox_up"], worlds_dir)

        index -= 1
        current = above
        above = current.above


base_camera = {
    "name": "camera 1",
    "position": {
        "x": 5440.0,
        "y": 0.0,
        "z": 24.0
    },
    "orientation": {
        "roll": 0.0,
        "pitch": -1.5707963267948966,
        "yaw": 3.141592653589793
    },
    "projectionMode": "PINHOLE",
    "fov": 90.0,
    "dof": "Infinity",
    "focalOffset": 2.0
}


def generate_multi_camera(section, index, camera_position, root, verticals, worlds_dir: pathlib.Path):
    scene = copy.deepcopy(base_scene)
    scene['world']['path'] = str((worlds_dir / section.world).absolute().resolve())
    scene['chunkList'] = generate_chunks(*section.region)

    scene['name'] = section.name + "_" + str(index)

    for name, orientation in skybox_orientations.items():
        scene['cameraPresets'][name] = copy.deepcopy(base_camera)
        scene['cameraPresets'][name]['name'] = name
        scene['cameraPresets'][name]['position'] = camera_position
        scene['cameraPresets'][name]['orientation'] = orientation

    for vertical in verticals:
        scene['cameraPresets'][vertical] = copy.deepcopy(base_camera)
        scene['cameraPresets'][vertical]['name'] = vertical
        scene['cameraPresets'][vertical]['position'] = camera_position
        scene['cameraPresets'][vertical]['orientation'] = vertical_orientations[vertical]

    with open(root / (str(index) + ".json"), 'w+') as fp:
        json.dump(scene, fp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Skybox Configs.')
    parser.add_argument('--deeper_world_config', type=pathlib.Path,
                        default="../../configs/config.yml",
                        help="Path to the deeper world config file.")
    parser.add_argument('--worlds_dir', type=pathlib.Path, default="../../worlds",
                        help="Directory containing all required minecraft worlds as specified in config.")
    parser.add_argument('--output_dir', type=pathlib.Path, default="../../scenes",
                        help="Directory to write scenes to.")
    parser.add_argument('--y', type=int, default=0,
                        help="y level to gen for")

    args = parser.parse_args()

    with open(args.deeper_world_config) as fp:
        deeper_config = yaml.load(fp)

    sections_data = deeper_config['sections']

    sections = []

    base_camera["position"]["y"] = args.y

    prev = None
    for section_data in sections_data:
        cur = Section(section_data)
        cur.above = prev

        if prev:
            prev.below = cur

        sections.append(cur)

        prev = cur

    print(sections)

    # This isn't pretty or fast but it doesn't need to be compared to render times
    for section in sections:
        get_needed_scenes(section, args.worlds_dir, args.output_dir, args.y)
