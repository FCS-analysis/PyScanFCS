import pathlib

import numpy as np

from pyscanfcs import sfcs_alg


def test_open_dat():
    here = pathlib.Path(__file__).parent
    f16 = here / "data/n2000_7.0ms_16bit.dat"
    f32 = here / "data/n2000_7.0ms_32bit.dat"
    r16, d16 = sfcs_alg.open_dat(str(f16))
    r32, d32 = sfcs_alg.open_dat(str(f32))
    assert r16 == 60
    assert r32 == 60
    assert np.all(d16==d32)
    assert np.all(d16[-5:] == np.array([1, 1, 21420, 21418, 21420]))


def test_bin_photon_events():
    data = np.array([5,  # 5
                     1, 1, 1,  # 8
                     4, 1, 1, 1,  # 15
                     1, 1, 1,  # 18
                     # blank
                     8, 1, 1,  # 28
                     ], dtype=np.uint32)
    binf = sfcs_alg.bin_photon_events(data=data, t_bin=5.0001)
    binned = np.fromfile(binf, dtype="uint16", count=-1)
    assert np.all(binned == np.array([1, 3, 4, 3, 0, 3]))


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
