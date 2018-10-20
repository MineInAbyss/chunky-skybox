from PIL import Image


class Stitcher:
    def __init__(self, north, south, east, west, top, bottom):
        self.south = south
        self.west = west
        self.east = east
        self.top = top
        self.bottom = bottom
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
        s_img = self._load_image(self.south)
        n_img = self._load_image(self.north)
        w_img = self._load_image(self.west)
        e_img = self._load_image(self.east)

        self._assert_same_size([s_img, n_img, w_img, e_img])

        box_size = s_img.size[0]

        width = box_size * 3
        height = box_size * 2

        skybox_img = Image.new('RGBA', (width, height))

        skybox_img.paste(w_img, (0, box_size))
        skybox_img.paste(n_img, (box_size, box_size))
        skybox_img.paste(e_img, (box_size * 2, box_size))
        skybox_img.paste(s_img, (box_size * 2, 0))

        skybox_img.save(output_path)


if __name__ == "__main__":
    scene_dir = '../../scenes/city_scene/'

    n = "{}skybox_north.png".format(scene_dir)
    s = "{}skybox_south.png".format(scene_dir)
    w = "{}skybox_west.png".format(scene_dir)
    e = "{}skybox_east.png".format(scene_dir)

    stitcher = Stitcher(n, s, e, w, None, None)

    stitcher.stitch("skybox.png")
