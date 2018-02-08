#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function

import pathlib

import numpy as np

from pyscanfcs import sfcs_alg



def test_open_dat():
    here = pathlib.Path(__file__).parent
    f16 = here / "data/n2000_7.0ms_16bit.dat"
    f32 = here / "data/n2000_7.0ms_32bit.dat"
    r16, d16 = sfcs_alg.OpenDat(str(f16))
    r32, d32 = sfcs_alg.OpenDat(str(f32))
    assert r16 == 60
    assert r32 == 60
    assert np.all(d16==d32)
    assert np.all(d16[-5:] == np.array([    1,     1, 21420, 21418, 21420]))


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
