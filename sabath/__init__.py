""" sabath/__init__.py - initialization for SABATH

@author: Cade Brown <cade@utk.edu>
"""

import os
import sys
import datetime
import subprocess
import shlex
import json

# for 'with' blocks
import contextlib

import logging

logging.basicConfig(format="SABATH> %(asctime)s.%(msecs)03d : %(message)s", datefmt="%Y-%m-%dT%H:%M:%S", level=logging.INFO)


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


#VARS = {
#    'SABATH_DIR': SABATH_DIR,
#}


def varrepl(s, vs={}):
    """ replace variables in string """
    for k, v in { **VARS, **vs }.items():
        s = s.replace(f"$[{k}]", v)
    return s



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


class Report():
    """
    A report is a run of a model (and optionally a dataset) that records metadata, launch configuration, and results

    This includes:
      * metadata (as JSON files)
      * launch configuration
      * results (as JSON files)
      * logs (as JSON files)
      * result data (as JSON/HDF files)
      * artifacts, such as model weights/architectures

    """

    def __init__(self, path, model, dataset=None) -> None:
        self.path = os.path.realpath(path)
        self.model = model
        self.dataset = dataset
        self.log = None

    def download(self):
        gd = f"{SABATH_DIR}/cache/{self.dataset['id']}"
        if os.path.exists(gd):
            return gd

        self.log.info(f"DOWNLOAD {self.dataset['id']} ...")

        # try and clone it
        try:
            DL = self.dataset['download']

            if 'git' in DL:
                self.runsh(f"git clone {DL['git']['url']} {gd}")

                # now, run steps to intiialize it
                with pushd(gd):
                    self.runsh(DL['git']['steps'])

            elif 'shell' in DL:
                # just run the shell script, period
                os.makedirs(gd, exist_ok=True)
                with pushd(gd):
                    self.runsh(DL['shell'])
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


    def clone(self):
        gd = f"{SABATH_DIR}/cache/{self.model['id']}"
        if os.path.exists(gd):
            return gd

        self.log.info(f"CLONE {self.model['id']} ...")
        #self.log(f"CLONE {self.jso['id']} ...")

        # try and clone it
        try:
            self.runsh(f"git clone {self.model['clone']['git']['url']} {gd}")
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

        self.log.info(f"SETUP {self.model['id']} ...")

        with pushd(gd):
            # run setup script, while in the directory
            self.runsh(self.model['setup'])

            # create an empty file to indicate that the model has been setup
            with open(cachefile, 'w') as fp:
                pass
        
        return gd

    def runsh(self, cmds, vs={}):
        """Runs a shell command, throw an exception if it fails"""
        if not isinstance(cmds, list):
            cmds = [cmds]

        with open(f'{self.path}/stdout.txt', 'a') as out_, open(f'{self.path}/stderr.txt', 'a') as err_:
            for cmd in cmds:
                self.log.info(f"SHELL> {cmd}")
                #self.log(f"running: {cmd}")
                cmd = varrepl(cmd, vs)
                res = subprocess.call(shlex.split(cmd), stdout=out_, stderr=err_)
                if res != 0:
                    self.log.error(f"command failed: {cmd} (in {os.getcwd()})")
                    raise Exception(f"command failed: {cmd}")

            """

            res = os.system(cmd)
            if res != 0:
                self.log.error(f"command failed: {cmd} (in {os.getcwd()})")
                raise Exception(f"command failed: {cmd}")
            """

    def run(self):
        os.makedirs(self.path, exist_ok=True)

        # start the report, setting up the logger
        self.log = logging.getLogger("sabath.report")
        fh = logging.FileHandler(f"{self.path}/log.txt")
        fh.setLevel(logging.DEBUG)
        self.log.addHandler(fh)
        self.log.info(f"START report: {self.path}")

        # set up environment variables
        os.environ['SABATH_REPORT'] = self.path
        # add to the python path, so imports in child programs work
        os.environ['PYTHONPATH'] = os.getenv("PYTHONPATH", "") + ":" + SABATH_DIR

        """ save the report to a directory """
        with open(f"{self.path}/model.json", "w") as f:
            json.dump(self.model, f, indent=4)
        if self.dataset:
            with open(f"{self.path}/dataset.json", "w") as f:
                json.dump(self.dataset, f, indent=4)

        # download dataset, if required
        if self.dataset:
            self.download()

        # make sure we are set up with the model
        gd = self.setup()

        # run the commands
        self.log.info(f"RUN {self.model['id']} ...")
        with pushd(gd):
            # give dataset location
            vs = {}
            if self.model['datasets']:
                vs['DATASET'] = f"{SABATH_DIR}/cache/{self.model['datasets'][0]}"
            self.runsh(self.model['run'], vs)

        # stop the report
        self.log.info(f"REPORT DIRECTORY: {self.path}")


def setup_tensorflow():
    import tensorflow as tf

    # report directory
    reportdir = os.getenv('SABATH_REPORT')
    print("SABATH SETUP TENSORFLOW: ", reportdir)

    # set up the logger
    logdir = f"{reportdir}/tensorboard"
    callback = tf.keras.callbacks.TensorBoard(log_dir=logdir)
    return [callback]
