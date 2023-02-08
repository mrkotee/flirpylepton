
import sys
import numpy as np
import cv2
from pylepton import Lepton
from i2cLepton import LeptonI2C


def get_cam_temp():
  l = LeptonI2C(1, 0x2a)
  return l.get_cam_temp()


finded_points = []

def capture(flip_v = False, device = "/dev/spidev0.0"):
  global finded_points
  with Lepton(device) as l:
    a,_ = l.capture(debug_print =False)
    print(f"{len(a)=} {len(a[0])=} {len(a[0][2])=}")
    temp = get_cam_temp()
    for k1, i in enumerate(a):
      for k2, i2 in enumerate(i):
        for k3, i3 in enumerate(i2):
          finded_points.append((k1, k2, int(i3*0.03385 - 276.96)+temp))
  if flip_v:
    cv2.flip(a,0,a)
  cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(a, 8, a)
  return np.uint8(a)

if __name__ == '__main__':
  from optparse import OptionParser

  usage = "usage: %prog [options] output_file[.format]"
  parser = OptionParser(usage=usage)

  parser.add_option("-f", "--flip-vertical",
                    action="store_true", dest="flip_v", default=False,
                    help="flip the output image vertically")

  parser.add_option("-d", "--device",
                    dest="device", default="/dev/spidev0.0",
                    help="specify the spi device node (might be /dev/spidev0.1 on a newer device)")

  (options, args) = parser.parse_args()

  if len(args) < 1:
    print("You must specify an output filename")
    sys.exit(1)

  image = capture(flip_v = options.flip_v, device = options.device)
  #print(image)
  image = cv2.applyColorMap(image.astype(np.uint8), cv2.COLORMAP_INFERNO)

  #print(finded_points)
  #for x, y, t in finded_points:
  x, y, t = max(finded_points, key=lambda x: x[2])
  print(f"{x=} {y=} {t=}")
  cv2.putText(image, str(t), (x, y), cv2.FONT_HERSHEY_DUPLEX, 0.2, (255, 255, 255), 1)

  cv2.imwrite(args[0], image)
