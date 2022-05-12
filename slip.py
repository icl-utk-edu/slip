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
    for k, v in { **VARS, **vs }.items():
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

