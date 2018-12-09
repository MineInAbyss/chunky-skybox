from glob import glob
from subprocess import call
import os
import shlex
from datetime import datetime

from PIL import Image

FNULL = open(os.devnull, 'w')
spp = 200
cpuLoad = 100
scene_dir = '../../scenes/l1s1/'
texture_dir = '../../texturepack/Default.zip'
renderFrom = 0  # highest layer above to render
renderTo = 0  # lowest render below to render

def to_scene_data(f_name):
    base_name = os.path.splitext(os.path.basename(f_name))[0]
    index = int(base_name.split('_')[0])
    side = base_name.split('_')[2]

    return {
        "path": f_name,
        "base": base_name,
        "index": index,
        "side": side
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
        complete = all(last_img.getpixel((i, size[1]-1))[3] == 255 for i in range(size[0]))
        if complete:
            done.add(side)
        return complete
    return is_done

if __name__ == '__main__':
    globalStart = datetime.now()
    for remove_filename in glob(scene_dir+'*.dump'): os.remove(remove_filename)

    # Exclude the annoying 0.json files that get generated
    files = glob(scene_dir+'*_*.json')
    files = sorted([to_scene_data(f_name) for f_name in files], key=lambda a: a["index"])
    done_checker = get_done_checker()

    for data in files:
        startTime = datetime.now()
        base_name = data["base"]
        index = data["index"]
        if int('{}'.format(index)) < renderFrom or int('{}'.format(index)) > renderTo:
            continue
        image_name = '{}-'.format(index) + str(spp) + ".png"
        image_path = scene_dir + image_name

        print("Rendering {}...".format(base_name + '.png'))

        if not os.path.isfile(scene_dir + base_name + '.png'):
            if not done_checker(data["side"], scene_dir + str(index-1)+"_skybox_"+data["side"]+".png"):
                # call(["java", "-jar", "../../bin/ChunkyLauncher.jar", "-set", "name", "rend", f_name], stdout=FNULL)
                call(["java", "-jar", "../../bin/ChunkyLauncher.jar", "-set", "cpuLoad", str(cpuLoad), "-render", data["path"], "-target", str(spp), "-texture", str(texture_dir)])
                for remove_filename in glob(scene_dir+'*.dump'): os.remove(remove_filename)
                os.rename(os.path.abspath(image_path), os.path.abspath(scene_dir + base_name + '.png'))
                endTime = datetime.now()
                print("Rendering {} took {}".format(base_name, endTime - startTime))
            else:
                print("{} looks done. Skipping render".format(base_name + '.png'))
        else:
            print("{} found. Skipping render".format(scene_dir + base_name + '.png'))

    globalEnd = datetime.now()
    print("Total: {}".format(globalEnd - globalStart))
