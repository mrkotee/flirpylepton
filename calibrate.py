import sys
import numpy as np
import cv2
import json
from statistics import mean

from config import Config
from lepton import Lepton


def main(conf: Config):
    raws = []
    results = {}
    lepton_cam = Lepton(conf.spi_device, conf.i2c_device, conf.i2c_addr)
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

        min_max_raw = (min([j[0] for i in raw[int(len(raw) / 2) - 2:int(len(raw) / 2) + 2] for j in
                            i[int(len(i) / 2) - 2:int(len(i) / 2) + 2]]),
                       max([j[0] for i in raw[int(len(raw) / 2) - 2:int(len(raw) / 2) + 2] for j in
                            i[int(len(i) / 2) - 2:int(len(i) / 2) + 2]]))
        print(f"{min_max_raw=}")

        raws.append((target_temp, mean([j[0] for i in raw[int(len(raw) / 2) - 2:int(len(raw) / 2) + 2] for j in
                                        i[int(len(i) / 2) - 2:int(len(i) / 2) + 2]]), cam_temp))
        if len(raws) == 1:
            continue

        for t, r, c_t in raws:
            results[t] = []
            a = 0.00001
            # T = a·RAW + T_C - k
            while a < 0.1:
                a += 0.00001
                res = a * r
                if res - c_t < 0:
                    a += 0.0001
                    continue
                if res + c_t - t < 500:
                    k = res + c_t - t
                    results[t].append((a, k))
        if not len(results):
            continue
        print(f"len results = {sum([len(v) for v in results.values()])}")
        means = []
        results2 = []
        for _ in range(len(results)):
            t, ress = results.popitem()
            for a1, k1 in ress:
                a1, k1 = round(a1, 4), round(k1, 1)
                for ress2 in results.values():
                    for a2, k2 in ress2:
                        if round(a2, 4) != a1:
                            continue
                        if round(k2, 1) != k1:
                            continue
                        results2.append((a2, k2))
        print(f"{len(results2)=}")
        # print(f"{len(means)=} {means=}")

        if len(results2):
            print(f"{len(results2)=} {results2[0]=}")
            with open("res.json", 'w') as f:
                json.dump(results2, f)
            break


# means = [(0.03177, 254.24802865690444), (0.03361, 250.32532149317547), (0.031735, 250.1941263879817),
#          (0.031735, 250.1941263879817), (0.03361, 250.32532149317547), (0.03361, 250.32532149317547)]

# results = [(0.0028799999999999997, 0.8607999999999976), (0.0028799999999999997, 0.9080800000000266),
#            (0.0028799999999999997, 0.8607999999999976), (0.0028799999999999997, 0.9080800000000266),
#            (0.0028799999999999997, 0.8523200000000415), (0.0028799999999999997, 0.8607999999999976),
#            (0.0028799999999999997, 0.9080800000000266), (0.0028799999999999997, 0.8523200000000415),
#            (0.0028799999999999997, 0.4064000000000263), (0.0010100000000000003, 0.5245200000000239)]

if __name__ == '__main__':
    with open("config.json") as f:
        conf = Config(**json.load(f))
    main(conf)
