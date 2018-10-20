from glob import glob
from subprocess import call
import os
from datetime import datetime

FNULL = open(os.devnull, 'w')

if __name__ == '__main__':

    scene_dir = '../../scenes/city_scene/'

    globalStart = datetime.now()

    render_name = "rend"
    for remove_filename in glob(scene_dir+'*.dump'): os.remove(remove_filename)

    files = glob(scene_dir+'*.json')
    for f_name in files:
        startTime = datetime.now()

        base_name = os.path.splitext(os.path.basename(f_name))[0]

        call(["java", "-jar", "../../bin/ChunkyLauncher.jar", "-set", "name", "rend", f_name], stdout=FNULL)
        call(["java", "-jar", "../../bin/ChunkyLauncher.jar", "-render", f_name, "-target", "100", "-threads", "12"], stdout=FNULL)

        for remove_filename in glob(scene_dir+'*.dump'): os.remove(remove_filename)

        os.rename(os.path.abspath(scene_dir+'rend-100.png'), os.path.abspath(scene_dir+base_name+'.png'))
        endTime = datetime.now()

        print("Rendering {} took {}".format(base_name, endTime - startTime))

    globalEnd = datetime.now()

    print("Total: {}".format(globalEnd - globalStart))