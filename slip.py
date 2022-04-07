#!python3
""" slip.py - Surrogate Launching and Integration Platform python driver

To run:
$ python3 slip.py run <MODELID>

@author: Cade Brown <me@cade.site>
"""

import os
import sys

import json

# for 'with' blocks
import contextlib

# SLIP directory (should be where 'slip.py' is)

# variables exposed 
SLIP_DIR = os.path.dirname(os.path.realpath(__file__))
VARS = {
    'SLIP_DIR': SLIP_DIR,
}


class Model():

    # create from JSON
    def __init__(self, jso):
        self.jso = jso

    def __repr__(self) -> str:
        return f"slip.Model({json.dumps(self.jso, indent=4)})"

    def __str__(self) -> str:
        return f"<slip.Model {self.jso['id']!r}>"

    # return directory where the model should be
    def getdir(self):
        return f"{SLIP_DIR}/cache/{self.jso['id']}"

    def clone(self):
        gd = self.getdir()
        if os.path.exists(gd):
            return gd
        
        slog(f"CLONE {self.jso['id']} ...")

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

        slog(f"SETUP {self.jso['id']} ...")

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

        slog(f"RUN {self.jso['id']} ...")

        # run the commands
        with pushd(gd):
            # give dataset location
            vs = {}
            if self.jso['datasets']:
                vs['DATASET'] = f"{SLIP_DIR}/cache/{self.jso['datasets'][0]}/data"
            runsh(self.jso['run'], vs)

class Dataset():

    # create from JSON
    def __init__(self, jso):
        self.jso = jso

    def __repr__(self) -> str:
        return f"slip.Dataset({json.dumps(self.jso, indent=4)})"

    def __str__(self) -> str:
        return f"<slip.Dataset {self.jso['id']!r}>"

    # return directory where the model should be
    def getdir(self):
        return f"{SLIP_DIR}/cache/{self.jso['id']}"

    def download(self):
        gd = self.getdir()
        if os.path.exists(gd):
            return gd
        
        slog(f"DOWNLOAD {self.jso['id']} ...")

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


# slip log function
def slog(msg, pfx='slip>'):
    print(pfx, msg)

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

def varrepl(s, vs={}):
    """ replace variables in string """
    for k, v in (VARS | vs).items():
        s = s.replace(f"$[{k}]", v)
    return s

# runs command(s)
def runsh(cmd, vs={}):
    if isinstance(cmd, list):
        # list of commands, so run them all
        for c in cmd:
            runsh(c, vs)
    else:
        # assume string command
        slog(f"running: {cmd}")
        cmd = varrepl(cmd, vs)
        res = os.system(cmd)
        if res != 0:
            slog(f"command failed: {cmd} (in {os.getcwd()})")
            raise Exception(f"command failed: {cmd}")

def main(argv):
    # TODO: parse arguments
    try:
        assert argv[1] == 'run'
        id = argv[2]
    except:
        slog("usage: python3 slip.py run <MODELID>")
        exit(1)

    try:
        model = Model(json.load(open(f"{SLIP_DIR}/db/models/{id}.json")))
    except:
        slog(f"unknown model '{id}', try something in `./db/datasets` (for example, 'CloudMask-0')")
        exit(1)

    print (repr(model))
    
    if model.jso['datasets']:
        ds = Dataset(json.load(open(f"{SLIP_DIR}/db/datasets/{model.jso['datasets'][0]}.json")))

        # download the dataset
        ds.download()

    # run the model, after the dataset has been downloaded
    model.run()


if __name__ == '__main__':
    main(sys.argv)



""" misc old useful code:

# pushes directory and automatically pops it
@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)

"git": {
    "url": "https://github.com/stfc-sciml/sciml-bench.git",
    "steps": [
        "pip3 install -r requirements.txt",
        "python3 -msciml_bench.core.command download slstr_cloud_ds1 --dataset_root_dir ./data"
    ]
}

def dataset_setup(dataset):
    assert 'git' in dataset['setup']

    # our installation instructions
    # TODO: make other than GIT
    inst = dataset['setup']['git']
    
    run('mkdir -p tmp')
    with pushd(f"tmp"):

        dirname = dataset['name']
        
        # clone it if needed
        if not os.path.exists(dirname):
            run(f"git clone {inst['url']} {dirname}")

        with pushd(dirname):
            run(f"git pull")

            # now, run commands
            for cmd in inst['steps']:
                run(cmd)

    # our installation instructions

"""

