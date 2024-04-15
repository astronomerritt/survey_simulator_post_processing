import pandas as pd
import os
import sqlite3
import logging

# this is for suppressing a warning in PyTables when writing to HDF5
import warnings
from tables import NaturalNameWarning


def PPOutWriteCSV(padain, outf):
    """
    Writes a pandas dataframe out to a CSV file at a location given by the user.

    Parameters
    -----------
    padain : pandas dataframe
        Dataframe of output.

    outf : string
        Location to which file should be written.

    Returns
    -----------
    None.

    """

    padain = padain.to_csv(path_or_buf=outf, mode="a", header=not os.path.exists(outf), index=False)

    return


def PPOutWriteHDF5(pp_results, outf, keyin):
    """
    Writes a pandas dataframe out to a HDF5 file at a location given by the user.

    Parameters
    -----------
    padain : pandas dataframe
        Dataframe of output.

    outf : string
        Location to which file should be written.

    keyin : string
        Key at which data will be located.

    Returns
    -----------
    None.

    """

    # pytables doesn't like the Pandas extension dtype StringDtype
    # converting the ObjID to 'str' type fixes this
    pp_results = pp_results.astype({"ObjID": str})

    # this suppresses a warning when ObjIDs begin with a number
    # as long as the user isn't going to use PyTables to access the data this doesn't matter
    warnings.filterwarnings("ignore", category=NaturalNameWarning)

    of = pp_results.to_hdf(outf, mode="a", format="table", append=True, key=keyin)

    return of


def PPOutWriteSqlite3(pp_results, outf):
    """
    Writes a pandas dataframe out to a CSV file at a location given by the user.

    Parameters
    -----------
    pp_results : pandas dataframe
        Dataframe of output.

    outf : string
        Location to which file should be written.

    Returns
    -----------
    None.

    """
    pplogger = logging.getLogger(__name__)

    pp_results = pp_results.drop("level_0", axis=1, errors="ignore")

    cnx = sqlite3.connect(outf)

    pp_results.to_sql("sorcha_results", con=cnx, if_exists="append", index=False)

    pplogger.info("SQL results saved in table sorcha_results in database {}.".format(outf))


def PPWriteOutput(cmd_args, configs, observations_in, endChunk=0, verbose=False):
    """
    Writes the output in the format specified in the config file to a location
    specified by the user.

    Parameters
    -----------
    cmd_args : dictionary
        Dictonary of command line arguments.

    configs : Dictionary
        Dictionary of config file arguments.

    observations_in : Pandas dataframe
        Dataframe of output.

    endChunk : integer, optional
        Integer of last object in chunk. Used only for HDF5 output key.
        Default = 0

    verbose : boolean, optional
        Verbose logging mode on or off. Default = False

    Returns
    -----------
    None.

    """

    pplogger = logging.getLogger(__name__)
    verboselog = pplogger.info if verbose else lambda *a, **k: None

    if configs["output_size"] == "basic":
        observations = observations_in.copy()[
            [
                "ObjID",
                "fieldMJD_TAI",
                "fieldRA_deg",
                "fieldDec_deg",
                "RA_deg",
                "Dec_deg",
                "astrometricSigma_deg",
                "optFilter",
                "trailedSourceMag",
                "trailedSourceMagSigma",
                "fiveSigmaDepth_mag",
                "phase_deg",
                "Range_LTC_km",
                "RangeRate_LTC_km_s",
            ]
        ]
    elif configs["output_size"] == "all":
        observations = observations_in.copy()

    observations["fieldMJD_TAI"] = observations["fieldMJD_TAI"].round(decimals=5)

    if configs["position_decimals"]:
        for position_col in [
            "fieldRA_deg",
            "fieldDec_deg",
            "RA_deg",
            "Dec_deg",
            "astrometricSigma_deg",
            "RATrue_deg",
            "DecTrue_deg",
        ]:
            try:  # depending on type of output selected, some of these columns may not exist.
                observations[position_col] = observations[position_col].round(
                    decimals=configs["position_decimals"]
                )
            except KeyError:
                continue

    if configs["magnitude_decimals"]:
        for magnitude_col in [
            "PSFMag",
            "trailedSourceMag",
            "trailedSourceMagTrue",
            "PSFMagTrue",
            "PSFMagSigma",
            "trailedSourceMagSigma",
            "fieldFiveSigmaDepth_mag",
            "fiveSigmaDepth_mag",
        ]:
            try:  # depending on type of output selected, some of these columns may not exist.
                observations[magnitude_col] = observations[magnitude_col].round(
                    decimals=configs["magnitude_decimals"]
                )
            except KeyError:
                continue

    verboselog("Constructing output path...")

    if configs["output_format"] == "csv":
        outputsuffix = ".csv"
        out = os.path.join(cmd_args.outpath, cmd_args.outfilestem + outputsuffix)
        verboselog("Output to CSV file...")
        observations = PPOutWriteCSV(observations, out)

    elif configs["output_format"] == "sqlite3":
        outputsuffix = ".db"
        out = os.path.join(cmd_args.outpath, cmd_args.outfilestem + outputsuffix)
        verboselog("Output to sqlite3 database...")
        observations = PPOutWriteSqlite3(observations, out)

    elif configs["output_format"] == "hdf5" or configs["output_format"] == "h5":
        outputsuffix = ".h5"
        out = os.path.join(cmd_args.outpath, cmd_args.outfilestem + outputsuffix)
        verboselog("Output to HDF5 binary file...")
        observations = PPOutWriteHDF5(observations, out, str(endChunk))
