import sys
import numpy as np
import cv2
import json

from config import Config
from lepton import Lepton


def main(conf: Config):
    lepton_cam = Lepton(conf.spi_device, conf.i2c_device, conf.i2c_addr)
    img = lepton_cam.get_image_with_max_temp()
    lepton_cam.save_png(img)


if __name__ == '__main__':
    with open("config.json") as f:
        conf = Config(**json.load(f))
    main(conf)
