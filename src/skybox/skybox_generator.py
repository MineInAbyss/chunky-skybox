from glob import glob
from subprocess import call
import os
import pathlib
from datetime import datetime

from PIL import Image

FNULL = open(os.devnull, 'w')
spp = 1
threads = 1
scene_dir = '../../scenes/city/'
texture_dir = '../../texturepack/Default.zip'
renderFrom = -2  # highest layer above to render
renderTo = 2  # lowest render below to render


def to_scene_data(f_name):
    base_name = os.path.splitext(os.path.basename(f_name))[0]
    index = int(base_name)

    return {
        "path": f_name,
        "base": base_name,
        "index": index,
    }


def get_done_checker():
    done = set()

    def is_done(side, last_path):
        if side in done:
            return True
        if side == "down" or side == "up":
            return False
        try:
            last_img = Image.open(last_path)
        except IOError:
            return False
        size = last_img.size
        complete = all(last_img.getpixel((i, size[1] - 1))[3] == 255 for i in range(size[0]))
        if complete:
            done.add(side)
        return complete

    return is_done


if __name__ == '__main__':
    globalStart = datetime.now()

    # Exclude the annoying 0.json files that get generated
    files = glob(scene_dir + '*.json')
    files = sorted([to_scene_data(f_name) for f_name in files], key=lambda a: a["index"])
    done_checker = get_done_checker()

    for data in files:
        startTime = datetime.now()
        base_name = data["base"]
        index = data["index"]
        if int('{}'.format(index)) < renderFrom or int('{}'.format(index)) > renderTo:
            continue
        snapshot_image_name = '{}-'.format(index) + str(spp) + ".png"
        snapshot_path = scene_dir + "snapshots/" + snapshot_image_name

        render_image_dir = scene_dir + "renders/"
        render_image_name = base_name + '.png'
        render_image_path = render_image_dir + render_image_name

        octree_initial_path = scene_dir + str(index) + "/" + str(index) + '.octree2'
        octree_final_path = scene_dir + str(index) + '.octree2'

        print("Rendering {}...".format(render_image_name))

        # pathlib.Path(render_image_dir).mkdir(parents=True, exist_ok=True)

        if not os.path.isfile(render_image_path):
            if True or not done_checker(data["side"], scene_dir + str(index - 1) + "_skybox_" + data["side"] + ".png"):
                # call(["java", "-jar", "../../bin/ChunkyLauncher.jar", "-set", "name", "rend", f_name], stdout=FNULL)
                call_args = ["java", "-jar", "../../bin/chunky-core.jar", "ChunkyMain", "-threads", str(threads), "-render", data["path"], "-f",
                     "-target",
                     str(spp)]

                print(call_args)

                call(call_args)  # "-texture", str(texture_dir)]
                # os.rename(os.path.abspath(snapshot_path), os.path.abspath(render_image_path))
                # if not os.path.isfile(octree_final_path):
                #     print("Moving octree to main directory because chunky is a dumb.")
                #     os.rename(octree_initial_path, octree_final_path)
                endTime = datetime.now()
                print("Rendering {} took {}".format(base_name, endTime - startTime))
            else:
                print("{} looks done. Skipping render".format(base_name + '.png'))
        else:
            print("{} found. Skipping render".format(scene_dir + base_name + '.png'))

    globalEnd = datetime.now()
    print("Total: {}".format(globalEnd - globalStart))
