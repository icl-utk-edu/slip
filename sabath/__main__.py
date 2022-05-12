""" sabath/__init__.py - SABATH CLI definition

@author: Cade Brown <cade@utk.edu>
"""

import sabath


import sys
import logging
import json

slog = logging.getLogger(__name__)

def main(argv):
    # TODO: parse arguments
    try:
        assert argv[1] == 'run'
        id = argv[2]
    except:
        raise Exception("usage: python3 slip.py run <MODELID>")

    # load the model
    try:
        model = sabath.Model(json.load(open(f"{sabath.SABATH_DIR}/db/models/{id}.json")))
    except:
        slog.info(f"unknown model '{id}', try something in `./db/datasets` (for example, 'CloudMask-0')")
        raise

    print (repr(model))
    
    # download the datasets[0], if it was available
    if model.jso['datasets']:
        ds = sabath.Dataset(json.load(open(f"{sabath.SABATH_DIR}/db/datasets/{model.jso['datasets'][0]}.json")))

        # download the dataset
        ds.download()

    # run the model, after the dataset has been downloaded
    model.run()


if __name__ == '__main__':
    main(sys.argv)

