from dataclasses import dataclass


@dataclass
class Config:
    i2c_device: int
    i2c_addr: int
    spi_device: int

    def __post_init__(self):
        self.i2c_addr = int(self.i2c_addr, 16)
