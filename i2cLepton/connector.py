import smbus
from .cmd import *


# https://github.com/PX4/Lepton/blob/master/I2C_Lepton/I2C_Interface.cpp

class LeptonI2C:
    def __init__(self, spi: int, i2c_addr: int):
        self.bus = smbus.SMBus(spi)
        self.i2c_addr = i2c_addr
        self._read_buf = []
        self._write_buf = []

    # def _read_result(self, to_read: int):
    #     output = 0
    #     res = self.bus.read_i2c_block_data(self.i2c_addr, 0x0, 4)
    #     for i in range(int(to_read / 2)):
    #         for j in range(2):
    #             output += self._read_buf[i + j] << 8 * (1 - j)
    #     return output

    def exec_cmd(self, cmd: int):
        self.bus.write_i2c_block_data(self.i2c_addr, 0x0, [1])  # (addr, first_byte, [words_count])
        self.bus.write_i2c_block_data(self.i2c_addr, 0x0, [0x04, (cmd >> 8) & 0xFF, cmd & 0xFF])
        res = self.bus.read_i2c_block_data(self.i2c_addr, 0x0, 4)
        return (res[2] << 8) + res[3]

    def get_cam_temp(self):
        result = self.exec_cmd(LEP_CID_SYS_AUX_TEMPERATURE_KELVIN)
        return ((result / 100) + ((result % 100) * .01)) - 273.15
