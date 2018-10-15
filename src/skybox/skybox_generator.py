import json
import math
import yaml
import os


# Generate the chunks that should be in the render
def generate_chunks(x1, z1, x2, z2):
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


skybox_orientations = {
    "skybox_right": {
        "roll": 0.0,
        "pitch": -1.5707963267948966,
        "yaw": 3.141592653589793
    },

    "skybox_left": {
        "roll": 0.0,
        "pitch": -1.5707963267948966,
        "yaw": 0.0
    },
    "skybox_front": {
        "roll": 0.0,
        "pitch": -1.5707963267948966,
        "yaw": -1.5707963267948966
    },
    "skybox_back": {
        "roll": 0.0,
        "pitch": -1.5707963267948966,
        "yaw": 1.5707963267948966
    }
}

base_scene_path = '../../scenes/base_scene.json'

if __name__ == '__main__':
    with open('../../configs/config.yml') as fp:
        deeper_config = yaml.load(fp)

    for section in deeper_config['sections']:
        section_name = section['name']
        scene_base_name = section_name + '_scene'
        scene_world_path = os.path.abspath('../../worlds/' + section['world'])

        scene_chunks = generate_chunks(*section['region'])

        scene_camera_position = {
            "x": (section['region'][0] + section['region'][2]) / 2,
            "y": 128,
            "z": (section['region'][1] + section['region'][3]) / 2
        }

        with open(base_scene_path) as fp:
            base_scene = json.load(fp)

        base_scene['world']['path'] = scene_world_path
        base_scene['chunkList'] = scene_chunks

        try:
            os.mkdir('../../scenes/' + scene_base_name)
        except Exception:
            pass

        for key,value in skybox_orientations.items():
            name = key + "_" + section_name
            base_scene['name'] = name
            base_scene['camera']['orientation'] = value
            base_scene['camera']['position'] = scene_camera_position

            with open('../../scenes/' + scene_base_name + "/" + name + ".json", 'w+') as fp:
                json.dump(base_scene, fp)
