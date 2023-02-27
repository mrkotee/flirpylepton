import sys
import numpy as np
import cv2
import json
import dataclasses
from statistics import mean

from config import Config
from lepton import Lepton


def main(conf: Config):
    raws = []
    results = {}
    lepton_cam = Lepton(conf.spi_device, conf.i2c_device, conf.i2c_addr, 0, 0)
    while 1:
        while 1:
            target_temp = input("Введите температуру (напр. 36.6) измеряемого предмета: ")
            try:
                target_temp = float(target_temp)
                break
            except ValueError:
                pass

        cam_temp = lepton_cam.lepton_i2c.get_cam_temp()
        raw = lepton_cam._capture()

        print(f"{cam_temp=:.2}")

        min_max_raw = (min([j[0] for i in raw[int(len(raw) / 2) - 2:int(len(raw) / 2) + 2] for j in
                            i[int(len(i) / 2) - 2:int(len(i) / 2) + 2]]),
                       max([j[0] for i in raw[int(len(raw) / 2) - 2:int(len(raw) / 2) + 2] for j in
                            i[int(len(i) / 2) - 2:int(len(i) / 2) + 2]]))
        print(f"{min_max_raw=}")

        raws.append((target_temp, mean([j[0] for i in raw[int(len(raw) / 2) - 2:int(len(raw) / 2) + 2] for j in
                                        i[int(len(i) / 2) - 2:int(len(i) / 2) + 2]]), cam_temp))
        if len(raws) == 1:
            continue

        left = np.array([[raws[0][1], -1], [raws[1][1], -1]])
        right = np.array([raws[0][0]-raws[0][2], raws[1][0]-raws[1][2]])
        a, k = np.linalg.inv(left).dot(right)

        print(f"{a=} {k=}")

        conf.a_coefficient = a
        conf.k_coefficient = k
        with open("config.json", 'w') as f:
            json.dump(dataclasses.asdict(conf), f)


if __name__ == '__main__':
    with open("config.json") as f:
        conf = Config(**json.load(f))
    main(conf)
