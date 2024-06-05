import os
import pandas as pd
import numpy as np
from numpy.testing import assert_equal
import pytest


def test_PPStats(tmp_path):

    from sorcha.modules.PPStats import stats

    # make some simple test data
    ObjID = (["object_one"] * 10) + (["object_two"] * 5)
    Linked = ([True] * 10) + ([False] * 5)
    optFilter = (["r"] * 6) + (["g"] * 4) + (["r"] * 5)
    trailedSourceMag = np.concatenate(
        (np.linspace(18, 21, 6), np.linspace(19, 22, 4), np.linspace(20, 23, 5))
    )
    phase_deg = np.concatenate((np.linspace(3, 10, 6), np.linspace(4, 11, 4), np.linspace(5, 10, 5)))

    test_dict = {
        "ObjID": ObjID,
        "Linked": Linked,
        "optFilter": optFilter,
        "trailedSourceMag": trailedSourceMag,
        "phase_deg": phase_deg,
    }
    test_df = pd.DataFrame(test_dict)

    filepath_stats = os.path.join(tmp_path, "test_stats.csv")
    stats(test_df, filepath_stats)

    stats_df = pd.read_csv(filepath_stats)

    # check that the dataframe is just three rows long
    assert len(stats_df) == 3

    # check for correct column names
    expected_columns = np.array(
        [
            "ObjID",
            "optFilter",
            "number_obs",
            "min_apparent_mag",
            "max_apparent_mag",
            "median_apparent_mag",
            "min_phase",
            "max_phase",
            "isLinked",
        ],
        dtype=object,
    )

    assert_equal(expected_columns, stats_df.columns.values)

    # check correct population
    expected_row_one = np.array(["object_one", "g", 4, 19.0, 22.0, 20.5, 4.0, 11.0, True], dtype=object)
    expected_row_two = np.array(["object_one", "r", 6, 18.0, 21.0, 19.5, 3.0, 10.0, True], dtype=object)
    expected_row_three = np.array(["object_two", "r", 5, 20.0, 23.0, 21.5, 5.0, 10.0, False], dtype=object)

    assert_equal(expected_row_one, stats_df.iloc[0].values)
    assert_equal(expected_row_two, stats_df.iloc[1].values)
    assert_equal(expected_row_three, stats_df.iloc[2].values)
