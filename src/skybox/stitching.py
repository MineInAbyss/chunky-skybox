import argparse
import os
import pathlib
from functools import reduce
from glob import glob

from PIL import Image


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
        return Image.alpha_composite(x, y)

    def stitch_region(self, paths):
        if not paths:
            return None
        images = {k: self._load_image(v) for (k, v) in paths.items()}

        base = images.pop(0) if 0 in images else Image.new('RGBA', next(iter(images.values())).size)

        top = reduce(self.compose, [v for (k, v) in sorted(images.items(), key=lambda a: a[0]) if k < 0], base)
        bottom = reduce(self.compose,
                        [v for (k, v) in sorted(images.items(), key=lambda a: a[0], reverse=True) if k > 0], base)
        return Image.alpha_composite(Image.alpha_composite(top, bottom), base)

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

        south = self.stitch_region(self.south)
        north = self.stitch_region(self.north)
        east = self.stitch_region(self.east)
        west = self.stitch_region(self.west)
        down = self.stitch_region(self.down)
        up = self.stitch_region(self.up)

        self.stitch_main(skybox_img, postprocess, south, (box_size * 2, 0))
        self.stitch_main(skybox_img, postprocess, north, (box_size, box_size))
        self.stitch_main(skybox_img, postprocess, east, (box_size * 2, box_size))
        self.stitch_main(skybox_img, postprocess, west, (0, box_size))
        self.stitch_main(skybox_img, postprocess, down, (0, 0))
        self.stitch_main(skybox_img, postprocess, up, (box_size, 0))

        return {k: v for (k, v) in
                {"skybox": skybox_img, "south": south, "north": north, "east": east, "west": west, "down": down,
                 "up": up}.items() if v}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Skybox Configs.')
    parser.add_argument('--snapshot_dir', type=pathlib.Path,
                        help="Path to the directory containing chunky snapshots rendered by the skybox generator.")
    parser.add_argument('--prefix', type=str,
                        help="Prefix for image names.")

    args = parser.parse_args()

    directions_to_paths = {}

    files = glob(str(args.snapshot_dir) + "/" + '*_*.png')
    for f_name in files:
        base_name = os.path.splitext(os.path.basename(f_name))[0]
        direction = base_name.split("_")[3]

        directions_to_paths.setdefault(direction, []).append(f_name)

    data = {}

    for key, vals in directions_to_paths.items():
        data[key] = {int(os.path.splitext(os.path.basename(a))[0].split("_")[1]): a for a in vals}

    stitcher = Stitcher(data.setdefault("north", {}), data.setdefault("south", {}), data.setdefault("east", {}),
                        data.setdefault("west", {}), data.setdefault("up", {}), data.setdefault("down", {}))

    for name, image in stitcher.stitch().items():
        image.save(args.snapshot_dir / (args.prefix + name + ".png"))
