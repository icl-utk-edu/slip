""" sabath/__init__.py - initialization for SABATH

@author: Cade Brown <cade@utk.edu>
"""

import os
import sys
import datetime

import json

# for 'with' blocks
import contextlib

import logging

logging.basicConfig(format="SABATH> %(asctime)s.%(msecs)03d : %(message)s", datefmt="%Y-%m-%dT%H:%M:%S", level=logging.INFO)

slog = logging.getLogger(__name__)


SABATH_DIR = os.getenv("SABATH_DIR")

if SABATH_DIR is None:
    # use the directory
    SABATH_DIR = str(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))



VARS = {
    'SABATH_DIR': SABATH_DIR,
}




"""logging.debug('This message should appear on the console')
logging.info('So should this')
logging.warning('And this, too')
"""

slog.info("SABATH initialized")


#VARS = {
#    'SABATH_DIR': SABATH_DIR,
#}


def varrepl(s, vs={}):
    """ replace variables in string """
    for k, v in { **VARS, **vs }.items():
        s = s.replace(f"$[{k}]", v)
    return s

def runsh(cmd, vs={}):
    """Runs a shell command, throw an exception if it fails"""
    if isinstance(cmd, list):
        # list of commands, so run them all
        for c in cmd:
            runsh(c, vs)
    else:
        # assume string command
        slog.info(f"SHELL> {cmd}")
        #slog(f"running: {cmd}")
        cmd = varrepl(cmd, vs)
        res = os.system(cmd)
        if res != 0:
            slog(f"command failed: {cmd} (in {os.getcwd()})")
            raise Exception(f"command failed: {cmd}")


# pushes directory and automatically pops it
# NOTE: use in 'with' block
@contextlib.contextmanager
def pushd(dir):
    prevdir = os.getcwd()
    os.chdir(dir)
    try:
        yield
    finally:
        os.chdir(prevdir)


class Model():
    """
    A model is a any sort of machine learning model that can be ran, which has machine-readable instructions for every step

    This class is a handle to a DB/JSON entry
    """

    # create from JSON
    def __init__(self, jso):
        self.jso = jso

    def __repr__(self) -> str:
        return f"slip.Model({json.dumps(self.jso, indent=4)})"

    def __str__(self) -> str:
        return f"<slip.Model {self.jso['id']!r}>"

    # return directory where the model should be
    def getdir(self):
        return f"{SABATH_DIR}/cache/{self.jso['id']}"

    def clone(self):
        gd = self.getdir()
        if os.path.exists(gd):
            return gd

        slog.info(f"CLONE {self.jso['id']} ...")
        #slog(f"CLONE {self.jso['id']} ...")

        # try and clone it
        try:
            runsh(f"git clone {self.jso['clone']['git']['url']} {gd}")
        except Exception as e:
            # delete it, if a failure occured
            try:
                os.rmdir(gd)
            except:
                pass
            raise e
        return gd

    def setup(self):
        # ensure we have the data
        gd = self.clone()

        # check cache file to see if we are already set up
        cachefile = f'{gd}/.setup.slip'
        if os.path.exists(cachefile):
            return gd

        slog.info(f"SETUP {self.jso['id']} ...")

        with pushd(gd):
            # run setup script, while in the directory
            runsh(self.jso['setup'])

            # create an empty file to indicate that the model has been setup
            with open(cachefile, 'w') as fp:
                pass
        
        return gd

    def run(self):
        # make sure we are set up
        gd = self.setup()

        slog.info(f"RUN {self.jso['id']} ...")

        # run the commands
        with pushd(gd):
            # give dataset location
            vs = {}
            if self.jso['datasets']:
                vs['DATASET'] = f"{SABATH_DIR}/cache/{self.jso['datasets'][0]}/data"
            runsh(self.jso['run'], vs)

class Dataset():
    """
    A dataset is a collection of files, which can be downloaded and used by a model
    
    This class is a handle to a DB/JSON entry
    """

    # create from JSON
    def __init__(self, jso):
        self.jso = jso

    def __repr__(self) -> str:
        return f"slip.Dataset({json.dumps(self.jso, indent=4)})"

    def __str__(self) -> str:
        return f"<slip.Dataset {self.jso['id']!r}>"

    # return directory where the model should be
    def getdir(self):
        return f"{SABATH_DIR}/cache/{self.jso['id']}"

    def download(self):
        gd = self.getdir()
        if os.path.exists(gd):
            return gd
        
        slog.info(f"DOWNLOAD {self.jso['id']} ...")

        # try and clone it
        try:
            DL = self.jso['download']

            if 'git' in DL:
                runsh(f"git clone {DL['git']['url']} {gd}")

                # now, run steps to intiialize it
                with pushd(gd):
                    runsh(DL['git']['steps'])

            elif 'shell' in DL:
                # just run the shell script, period
                os.makedirs(gd, exist_ok=True)
                with pushd(gd):
                    runsh(DL['shell'])
            else:
                raise Exception("Unknown download type! (had no 'git' or 'shell' keys)")

        except Exception as e:
            # delete it, if a failure occured
            try:
                os.rmdir(gd)
            except:
                pass
            raise e
        return gd
