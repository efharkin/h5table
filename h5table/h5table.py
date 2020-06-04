import json
import warnings

import h5py as h5
import pandas as pd
import numpy as np

COLNAMEATTR = '_colnames'
COLTYPEATTR = '_coltypes'

def saveH5Table(f, path, dframe):
    """Save a DataFrame in an HDF5 file.

    Store column names and dtypes in special meta-attributes for loading with
    `loadH5Table()`.

    Inputs
    ------
    f : h5py.File
    path : str
      HDF5 path to dataset.
    dframe : pandas.DataFrame-like
      Table to be saved in HDF5 file.

    """
    f.create_dataset(
        path,
        data=np.asarray(dframe.values, dtype=np.bytes_),
        dtype=h5.special_dtype(vlen=str)
    )
    f[path].attrs[COLNAMEATTR] = json.dumps(dframe.columns.tolist())
    f[path].attrs[COLTYPEATTR] = json.dumps(
        [t.str for t in dframe.dtypes.tolist()]
    )

def loadH5Table(f, path):
    """Load a DataFrame from an HDF5 file.

    Loads DataFrame contents, column names, and data types according to
    format used by `saveH5Table()`. Raises an error if column names cannot be
    found, and warns if type coercion cannot be performed.

    Inputs
    ------
    f : Connection to HDF5 file.
    path : str
      HDF5 path to dataset.

    Returns
    -------
    pandas.DataFrame with contents, column names, and dtypes from `f[path]`.
    """
    if COLNAMEATTR not in f[path].attrs.keys():
        raise AttributeError(
            'Missing column name attribute `{}`. Was this dataset '
            'saved using `saveH5Table()`?'.format(COLNAMEATTR)
        )
    colnames = json.loads(f[path].attrs[COLNAMEATTR])
    dframe = pd.DataFrame(f[path][()], columns = colnames)

    # Convert types if possible.
    if COLTYPEATTR not in f[path].attrs.keys():
        warnings.warn(
            'Could not find column type attribute `{}`. '
            'Skipping type coercion.'.format(COLTYPEATTR)
        )
    else:
        coltypes = json.loads(f[path].attrs[COLTYPEATTR])
        try:
            dframe = dframe.astype(
                {cn: np.dtype(ct) for cn, ct in zip(colnames, coltypes)}
            )
        except:
            warnings.warn('Type coercion failed. Skipping.')

    return dframe

