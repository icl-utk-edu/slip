""" sabath/__init__.py - SABATH CLI definition

@author: Cade Brown <cade@utk.edu>
"""

from genericpath import exists
from operator import truediv
import sabath

import sys
import logging
import json
import time
import os

import argparse

slog = logging.getLogger(__name__)

def main(argv):
    
    parser = argparse.ArgumentParser(description='SABATH: a platform for running ML surrogate models')
    parser.add_argument('--cache', help='cache directory, for storing models and datasets', default=None)

    subparsers = parser.add_subparsers(help='sub-commands help')

    parser_a = subparsers.add_parser('run', help='run a model, producing a report')
    parser_a.add_argument('model', help='model to run')

    # TODO: parse arguments
    args = parser.parse_args(argv[1:])

    # store variables
    if args.cache is not None:
        sabath.SABATH_CACHE = args.cache
    elif sabath.SABATH_CACHE is None:
        # we need a default, so choose the sabath directory itself
        sabath.SABATH_CACHE = os.getenv("SABATH_CACHE", os.path.join(sabath.SABATH_DIR, ".sabath"))

    # make the directory if needs to
    os.makedirs(sabath.SABATH_CACHE, exists_ok=True)

    id = args.model
    #try:
    #    assert argv[1] == 'run'
    #    id = argv[2]
    #except:
    #    raise Exception("usage: python3 slip.py run <MODELID>")


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

