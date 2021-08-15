import argparse
import os
import pathlib
from datetime import datetime
from glob import glob
from subprocess import call

FNULL = open(os.devnull, 'w')


def to_scene_data(f_name):
    base_name = os.path.splitext(os.path.basename(f_name))[0]
    index = int(base_name)

    return {
        "path": f_name,
        "base": base_name,
        "index": index,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Skybox Images.')
    parser.add_argument('--spp', type=int, default=100,
                        help="Samples per pixel for rendering")
    parser.add_argument('--threads', type=int, default=1,
                        help="Number of threads to use for render workers")
    parser.add_argument('--scene_dir', type=pathlib.Path,
                        help="Directory containing the chunky scene configs. Also will be output directory of renders.")
    parser.add_argument('--look_above', type=int, default=1, help="How many sections to look up when rendering.")
    parser.add_argument('--look_below', type=int, default=1, help="How many sections to look down when rendering.")

    args = parser.parse_args()

    globalStart = datetime.now()

    scene_dir = str(args.scene_dir) + "/"
    files = glob(scene_dir + '*.json')
    files = sorted([to_scene_data(f_name) for f_name in files], key=lambda a: a["index"])

    for data in files:
        startTime = datetime.now()
        base_name = data["base"]
        index = data["index"]
        if int('{}'.format(index)) < -args.look_above or int('{}'.format(index)) > args.look_below:
            continue

        octree_initial_path = scene_dir + str(index) + "/" + str(index) + '.octree2'
        octree_final_path = scene_dir + str(index) + '.octree2'

        print("Rendering {}...".format(data["path"]))

        call_args = ["java", "-Xms8g", "-cp", "../../bin/*", "-DlogLevel=INFO", "se.llbit.chunky.main.Chunky", "-threads",
                     str(args.threads),
                     "-render", data["path"], "-f",
                     "-target",
                     str(args.spp)]

        print("Chunky command: {}".format(" ".join(call_args)))

        call(call_args)  # "-texture", str(texture_dir)]
        # os.rename(os.path.abspath(snapshot_path), os.path.abspath(render_image_path))
        # if not os.path.isfile(octree_final_path):
        #     print("Moving octree to main directory because chunky is a dumb.")
        #     os.rename(octree_initial_path, octree_final_path)
        endTime = datetime.now()
        print("Rendering {} took {}".format(base_name, endTime - startTime))

    globalEnd = datetime.now()
    print("Total: {}".format(globalEnd - globalStart))
