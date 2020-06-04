import json
import warnings

import h5py as h5
import pandas as pd
import numpy as np

COLNAMEATTR = '__colnames'
COLTYPEATTR = '__coltypes'


def save_dataframe(filename_or_h5group, dataset_name, dataframe):
    """Save a DataFrame in an HDF5 file.

    Store column names and dtypes in special meta-attributes for loading with
    `loadH5Table()`.

    Arguments
    ---------
    filename_or_h5group : str or h5py.Group
        If filename_or_h5group is a path-like str, open a file with that name
        and save the dataframe in it. If it is an h5py.Group, save the dataframe
        in a new dataset there.
    dataset_name : str
        HDF5 path to dataset in which to save the dataframe.
    dataframe : pandas.DataFrame-like
        Table to save.

    Raises
    ------
    TypeError if argument filename_or_h5group is not a str or h5py.Group.

    """
    if isinstance(filename_or_h5group, str):
        with h5.File(filename_or_h5group, 'a') as f:
            _save_dataframe_to_h5group(f, dataset_name, dataframe)
            f.close()
    elif isinstance(filename_or_h5group, h5.Group):
        _save_dataframe_to_h5group(filename_or_h5group, dataset_name, dataframe)
    else:
        raise TypeError(
            'Expected argument `filename_or_h5group` to be str '
            'filename or instance of h5py.Group, got {} of type {} instead'.format(
                filename_or_h5group, type(filename_or_h5group)
            )
        )


def _save_dataframe_to_h5group(h5group, dataset_name, dataframe):
    """Save a DataFrame to an h5py.Dataset."""
    h5group.create_dataset(
        dataset_name,
        data=np.asarray(dataframe.values, dtype=np.bytes_),
        dtype=h5.special_dtype(vlen=str),
    )
    h5group[dataset_name].attrs[COLNAMEATTR] = json.dumps(
        dataframe.columns.tolist()
    )
    h5group[dataset_name].attrs[COLTYPEATTR] = json.dumps(
        [t.str for t in dataframe.dtypes.tolist()]
    )


def load_dataframe(filename_or_h5group, dataset_name):
    """Load a DataFrame from an HDF5 file.

    Loads DataFrame contents, column names, and data types according to
    format used by `saveH5Table()`.

    Arguments
    ---------
    filename_or_h5group : str or h5py.Group
        If filename_or_group is a path-like str, open the file in read-only
        mode and try to load the specified dataset from it as a table. If
        filename_or_h5group is an h5py.Group, look for the specified dataset
        there and try to load it as a table.
    dataset_name : str
        HDF5 path to the dataset to load as a table.

    Returns
    -------
    pandas.DataFrame with contents, column names, and dtypes from the
    specified dataset.

    Raises
    ------
    TypeError if filename_or_h5group is not a str or h5py.Group.
    AttributeError if column names for the dataset cannot be found.

    Warns
    -----
    UserWarning if the dtypes of the dataframe could not be restored.

    """
    if isinstance(filename_or_h5group, str):
        with h5.File(filename_or_h5group, 'r') as f:
            dframe = _load_dataframe_from_h5group(f, dataset_name)
            f.close()
    elif isinstance(filename_or_h5group, h5.Group):
        dframe = _load_dataframe_from_h5group(filename_or_h5group, dataset_name)
    else:
        raise TypeError(
            'Expected argument `filename_or_h5group` to be str '
            'filename or instance of h5py.Group, got {} of type {} instead'.format(
                filename_or_h5group, type(filename_or_h5group)
            )
        )

    return dframe


def _load_dataframe_from_h5group(h5group, dataset_name):
    if COLNAMEATTR not in h5group[dataset_name].attrs.keys():
        raise AttributeError(
            'Missing column name attribute `{}`. Was this dataset '
            'saved using `saveH5Table()`?'.format(COLNAMEATTR)
        )
    colnames = json.loads(h5group[dataset_name].attrs[COLNAMEATTR])
    dframe = pd.DataFrame(h5group[dataset_name][()], columns=colnames)

    # Convert types if possible.
    if COLTYPEATTR not in h5group[dataset_name].attrs.keys():
        warnings.warn(
            'Could not find column type attribute `{}`. '
            'Skipping type coercion.'.format(COLTYPEATTR)
        )
    else:
        coltypes = json.loads(h5group[dataset_name].attrs[COLTYPEATTR])
        try:
            dframe = dframe.astype(
                {cn: np.dtype(ct) for cn, ct in zip(colnames, coltypes)}
            )
        except:
            warnings.warn('Type coercion failed. Skipping.')

    return dframe
