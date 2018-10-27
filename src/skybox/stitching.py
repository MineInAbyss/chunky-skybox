from PIL import Image
import os
from glob import glob


class Stitcher:
    def __init__(self, north, south, east, west, up, bottom):
        self.south = south
        self.west = west
        self.east = east
        self.up = up
        self.down = bottom
        self.north = north

    def _load_image(self, path):
        return Image.open(path)

    def _assert_same_size(self, imgs: list):
        if not imgs:
            return
        else:
            im1 = imgs[0]

            assert im1.size[0] == im1.size[1]

            for img in imgs[1:]:
                assert im1.size == img.size

    def stitch(self, output_path):
        box_size = 1024

        width = box_size * 3
        height = box_size * 2

        skybox_img = Image.new('RGBA', (width, height))

        # self._assert_same_size([s_img, n_img, w_img, e_img])

        for path in reversed(self.south):
            img = self._load_image(path)
            skybox_img.alpha_composite(img, (box_size * 2, 0))

        for path in reversed(self.north):
            img = self._load_image(path)

            skybox_img.alpha_composite(img, (box_size, box_size))

        for path in reversed(self.east):
            img = self._load_image(path)
            skybox_img.alpha_composite(img, (box_size * 2, box_size))

        for path in reversed(self.west):
            img = self._load_image(path)
            skybox_img.alpha_composite(img, (0, box_size))

        for path in reversed(self.down):
            img = self._load_image(path)
            skybox_img.alpha_composite(img, (0, 0))

        for path in reversed(self.up):
            img = self._load_image(path)
            skybox_img.alpha_composite(img, (0, 0))


        skybox_img.save(output_path)


if __name__ == "__main__":
    scene_dir = '../../scenes/l1s2/'

    data = {}

    files = glob(scene_dir+'*_*.png')
    for f_name in files:
        base_name = os.path.splitext(os.path.basename(f_name))[0]
        direction = base_name.split("_")[2]

        data.setdefault(direction, []).append(f_name)


    for key, list in data.items():
        list.sort(key=lambda a: abs(int(os.path.splitext(os.path.basename(a))[0].split("_")[0])))

    # n = "{}{}_skybox_north.png".format(scene_dir,0)
    # s = "{}{}_skybox_south.png".format(scene_dir,0)
    # w = "{}{}_skybox_west.png".format(scene_dir,0)
    # e = "{}{}_skybox_east.png".format(scene_dir,0)
    #
    stitcher = Stitcher(data.setdefault("north", []), data.setdefault("south", []), data.setdefault("east", []), data.setdefault("west", []), data.setdefault("up", []), data.setdefault("down", []))

    stitcher.stitch(scene_dir+"skybox.png")
