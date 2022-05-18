""" sabath/__init__.py - SABATH CLI definition

@author: Cade Brown <cade@utk.edu>
"""

import sabath


import sys
import logging
import json
import time

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
        with open(f"{sabath.SABATH_DIR}/db/models/{id}.json") as fp:
            model = json.load(fp)
    except:
        raise Exception(f"unknown model '{id}', try something in `./db/datasets` (for example, 'CloudMask-0')")

    # load dataset, if applicable
    if model['datasets']:
        with open(f"{sabath.SABATH_DIR}/db/datasets/{model['datasets'][0]}.json") as fp:
            dataset = json.load(fp)
    else:
        dataset = None

    # create report
    report = sabath.Report(f"./report-{id}-{int(time.time())}", model, dataset)

    # run the report
    report.run()


if __name__ == '__main__':
    main(sys.argv)

