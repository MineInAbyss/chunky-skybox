import pathlib

from PIL import Image, ImageFilter, ImageChops
from functools import reduce
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

    @staticmethod
    def compose(x, y):
        x.alpha_composite(y)
        return x

    def stitch_region(self, paths):
        if not paths:
            return None
        images_in_order = reversed([self._load_image(path) for path in paths])
        return reduce(self.compose, images_in_order)

    def stitch_main(self, skybox_image, postprocess, composite, region):
        if not composite:
            return
        skybox_image.alpha_composite(postprocess(composite), region)

    def stitch(self, postprocess=lambda img: img):
        box_size = 1024

        width = box_size * 3
        height = box_size * 2

        skybox_img = Image.new('RGBA', (width, height))

        # self._assert_same_size([s_img, n_img, w_img, e_img])

        self.stitch_main(skybox_img, postprocess, self.stitch_region(self.south), (box_size * 2, 0))
        self.stitch_main(skybox_img, postprocess, self.stitch_region(self.north), (box_size, box_size))
        self.stitch_main(skybox_img, postprocess, self.stitch_region(self.east), (box_size * 2, box_size))
        self.stitch_main(skybox_img, postprocess, self.stitch_region(self.west), (0, box_size))
        self.stitch_main(skybox_img, postprocess, self.stitch_region(self.down), (0, 0))
        self.stitch_main(skybox_img, postprocess, self.stitch_region(self.up), (box_size, 0))

        return skybox_img


if __name__ == "__main__":
    scene_dir = '../../scenes/city/'

    data = {}

    files = glob(scene_dir + "snapshots/" + '*_*.png')
    for f_name in files:
        base_name = os.path.splitext(os.path.basename(f_name))[0]
        direction = base_name.split("_")[3]

        data.setdefault(direction, []).append(f_name)

    for key, list in data.items():
        list.sort(key=lambda a: abs(int(os.path.splitext(os.path.basename(a))[0].split("_")[1])))

    # n = "{}{}_skybox_north.png".format(scene_dir,0)
    # s = "{}{}_skybox_south.png".format(scene_dir,0)
    # w = "{}{}_skybox_west.png".format(scene_dir,0)
    # e = "{}{}_skybox_east.png".format(scene_dir,0)
    #
    stitcher = Stitcher(data.setdefault("north", []), data.setdefault("south", []), data.setdefault("east", []),
                        data.setdefault("west", []), data.setdefault("up", []), data.setdefault("down", []))

    pathlib.Path(scene_dir + "renders/").mkdir(parents=True, exist_ok=True)

    # lambda image: image.filter(ImageFilter.GaussianBlur(radius=3))
    result = stitcher.stitch().save(
        scene_dir + "renders/" + "skybox.png")
