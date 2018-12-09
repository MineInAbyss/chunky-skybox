import json
import math
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
    "skybox_down" : {
        "roll": 0.0,
        "pitch": 0.0,
        "yaw": -1.5707963267948966
    },
    "skybox_up" : {
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
def get_needed_scenes(section):
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
        "y": 128,
        "z": center_y
    }

    root = '../../scenes/' + section.name + '/'

    try:
        os.mkdir(root)
    except Exception:
        pass

    generate_cardinal_scenes(section, 0, camera_pos, root)

    current = section
    below = section.below
    center_to_translate = (center_x, 128, center_y)

    index = 1

    while below:
        center_to_translate = convert_to_central(center_to_translate, current.refBottom, below.refTop)
        x, y, z = center_to_translate

        camera_pos = {
            "x": x,
            "y": y,
            "z": z
        }
        generate_cardinal_scenes(below, index, camera_pos, root)
        generate_vertical_scene(below, index, camera_pos, root, "skybox_down")

        index += 1
        current = below
        below = current.below


    current = section
    above = section.above
    center_to_translate = (center_x, 128, center_y)
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
        if index > -3:  # There is essentially never a useful cardinal scene 3 sections above, so we can ignore them
            generate_cardinal_scenes(above, index, camera_pos, root)
        generate_vertical_scene(above, index, camera_pos, root, "skybox_up")

        index -= 1
        current = above
        above = current.above


def generate_cardinal_scenes(section, index, camera_pos, root):
    for name, orientation in skybox_orientations.items():
        scene = copy.deepcopy(base_scene)
        world_path = os.path.abspath('../../worlds/' + section.world)
        chunks = generate_chunks(*section.region)

        scene['world']['path'] = world_path
        scene['chunkList'] = chunks

        # All these scenes will share chunks so use the same name!
        scene['name'] = str(index)
        scene['camera']['orientation'] = orientation
        scene['camera']['position'] = camera_pos

        with open(root + str(index) + '_' + name + ".json", 'w+') as fp:
            json.dump(scene, fp)


def generate_vertical_scene(section, index, camera_pos, root, flag):
    scene = copy.deepcopy(base_scene)
    world_path = os.path.abspath('../../worlds/' + section.world)
    chunks = generate_chunks(*section.region)

    scene['world']['path'] = world_path
    scene['chunkList'] = chunks

    # All these scenes will share chunks so use the same name!
    scene['name'] = str(index)
    scene['camera']['orientation'] = vertical_orientations[flag]
    scene['camera']['position'] = camera_pos

    with open(root + str(index) + '_' + flag + ".json", 'w+') as fp:
        json.dump(scene, fp)


if __name__ == '__main__':
    with open('../../configs/config.yml') as fp:
        deeper_config = yaml.load(fp)

    sections_data = deeper_config['sections']

    sections = []

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
        needed_scenes = get_needed_scenes(section)

    # center_x = center_y = None
    # prev_ref = (0,0)
    #
    # for section in deeper_config['sections']:
    #     section_name = section['name']
    #     scene_base_name = section_name + '_scene'
    #     scene_world_path = os.path.abspath('../../worlds/' + section['world'])
    #
    #     own_ref_top = section['refTop'][::2]
    #
    #     scene_chunks = generate_chunks(*section['region'])
    #
    #
    #     if not center_x:
    #         center_x = (section['region'][0] + section['region'][2]) / 2
    #         center_y = (section['region'][1] + section['region'][3]) / 2
    #     else:
    #         center_x, center_y = convert_to_central((center_x, center_y), prev_ref,own_ref_top)
    #
    #
    #     scene_camera_position = {
    #         "x": center_x,
    #         "y": 128,
    #         "z": center_y
    #     }
    #
    #     with open(base_scene_path) as fp:
    #         base_scene = json.load(fp)
    #
    #     base_scene['world']['path'] = scene_world_path
    #     base_scene['chunkList'] = scene_chunks
    #
    #     try:
    #         os.mkdir('../../scenes/' + scene_base_name)
    #     except Exception:
    #         pass
    #
    #     for key,value in skybox_orientations.items():
    #         name = key
    #         base_scene['name'] = name
    #         base_scene['camera']['orientation'] = value
    #         base_scene['camera']['position'] = scene_camera_position
    #
    #         with open('../../scenes/' + scene_base_name + "/" + name + ".json", 'w+') as fp:
    #             json.dump(base_scene, fp)
    #
    #
    #     prev_ref = section['refBottom'][::2]
