import sys
import numpy as np
import cv2
import json

from config import Config
from pylepton import Lepton
from i2cLepton import LeptonI2C


def main(conf: Config):
    def capture_img():
        lepton_i2c = LeptonI2C(conf.i2c_device, conf.i2c_addr)

        temperature_map = []

        with Lepton(f"/dev/spidev0.{conf.spi_device}") as lepton_spi:
            a, _ = lepton_spi.capture(debug_print=False)
            temp = lepton_i2c.get_cam_temp()
            for k1, i in enumerate(a):
                for k2, i2 in enumerate(i):
                    for k3, i3 in enumerate(i2):
                        temperature_map.append((k1, k2, int(i3 * 0.03385 - 276.96) + temp))
        cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(a, 8, a)
        return np.uint8(a), temperature_map

    image, temp_map = capture_img()
    image = cv2.applyColorMap(image.astype(np.uint8), cv2.COLORMAP_INFERNO)

    if max_temp := max(temp_map, key=lambda x: x[2]):
        x, y, t = max_temp
        print(f"max temp point: {x=} {y=} {t=}")
        cv2.putText(image, str(t), (x, y), cv2.FONT_HERSHEY_DUPLEX, 0.2, (255, 255, 255), 1)

    cv2.imwrite("out.png", image)


if __name__ == '__main__':
    with open("config.json") as f:
        conf = Config(**json.load(f))
    main(conf)
