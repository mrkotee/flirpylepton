import cv2
import numpy as np

from .spilepton import SpiLepton
from .i2cLepton import LeptonI2C


class Lepton:
    def __init__(self, spi_device: int, i2c_device: int, i2c_addr: int):
        self.lepton_i2c = LeptonI2C(i2c_device, i2c_addr)
        self.lepton_spi = SpiLepton(f"/dev/spidev0.{spi_device}")

    def _capture(self):
        with self.lepton_spi:
            a, _ = self.lepton_spi.capture(debug_print=False)
        return a

    def _create_temp_map(self, image):
        temp_map = []
        cam_temp = self.lepton_i2c.get_cam_temp()

        for k1, i in enumerate(image):
            for k2, i2 in enumerate(i):
                temp_map.append((k1, k2, int(i2[0] * 0.03385 - 276.96) + cam_temp))
        return temp_map

    def get_temperature_map(self):
        """
        Get 60x80 map of temperature from Flir Lepton cam
        """
        image = self._capture()
        return self._create_temp_map(image)

    def _get_image(self, image, colormap):
        cv2.normalize(image, image, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(image, 8, image)
        return cv2.applyColorMap(np.uint8(image), colormap)

    def get_image(self, colormap=cv2.COLORMAP_INFERNO):
        image = self._capture()
        return self._get_image(image, colormap)

    def get_image_with_max_temp(self, colormap=cv2.COLORMAP_INFERNO):
        image = self._capture()
        temp_map = self._create_temp_map(image)
        image = self._get_image(image, colormap)

        if max_temp := max(temp_map, key=lambda x: x[2]):
            x, y, t = max_temp
            cv2.putText(image, str(round(t, 1)), (x, y), cv2.FONT_HERSHEY_DUPLEX, 0.2, (255, 255, 255), 1)

        return image

    def save_png(self, image, filename="out.png"):
        cv2.imwrite(filename, image)
