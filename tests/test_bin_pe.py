import numpy as np

from pyscanfcs import bin_pe


def test_bin_photon_events():
    data = np.array([5,  # 5
                     1, 1, 1,  # 8
                     4, 1, 1, 1,  # 15
                     1, 1, 1,  # 18
                     # blank
                     8, 1, 1,  # 28
                     ], dtype=np.uint32)
    binf = bin_pe.bin_photon_events(data=data, t_bin=5.0001)
    binned = np.fromfile(binf, dtype="uint16", count=-1)
    assert np.all(binned == np.array([1, 3, 4, 3, 0, 3]))


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
