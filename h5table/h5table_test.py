import unittest
import os

import h5py as h5
import numpy as np
import pandas as pd

import h5table

TMPFILEPATH = 'tmpfile.h5'

class H5TableTest(unittest.TestCase):

    def setUp(self):
        self.f = h5.File(TMPFILEPATH, 'a')

    def testLoadSave(self):
        dframe = pd.DataFrame({
            'Name': ['Emerson', 'Harkin'],
            'Age': [1, 2],
            'Height': [1.1, 2.2]
        })

        h5table.saveH5Table(self.f, 'dataset', dframe)
        loaded = h5table.loadH5Table(self.f, 'dataset')

        self.assertTrue(
            dframe.equals(loaded),
            'Saved and loaded dataframes are not equivalent.'
        )
        self.assertEqual(np.sum(loaded['Age']), 3)
        self.assertTrue(
            np.abs(np.sum(loaded['Height']) - 3.3) < 1e-4
        )

    def tearDown(self):
        self.f.close()
        os.remove(TMPFILEPATH)

if __name__ == '__main__':
    unittest.main()
