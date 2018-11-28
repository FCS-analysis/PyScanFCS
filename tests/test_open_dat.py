import pathlib

import numpy as np

from pyscanfcs import openfile


def test_open_dat():
    here = pathlib.Path(__file__).parent
    f16 = here / "data/n2000_7.0ms_16bit.dat"
    f32 = here / "data/n2000_7.0ms_32bit.dat"
    info16 = openfile.openDAT(str(f16))
    info32 = openfile.openDAT(str(f32))
    
    assert info16["system_clock"] == 60
    assert info32["system_clock"]== 60
    assert np.all(info16["data_stream"] == info32["data_stream"])
    ref = np.array([1, 1, 21420, 21418, 21420])
    assert np.all(info16["data_stream"][-5:] == ref)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
