# SABATH

SABATH is a is a software ecosystem for downloading and running ML/AI benchmarks, which produces a report that can be used to reproduce the results.


## Setup

To set up, run:

```shell
$ pip3 install -r requirements.txt
```

I also have a setup script for ICL's guyot machine:

```shell
# load my packages
$ source ~cade/load_guyot.sh
```

NOTE: other packages may need to be loaded for models that use other tech stacks


## Usage

To view the usage, you can run with `--help`:

```shell
$ python3 -msabath --help              
usage: __main__.py [-h] [--cache CACHE] {run} ...

SABATH: a platform for running ML surrogate models

positional arguments:
  {run}          sub-commands help
    run          run a model, producing a report

optional arguments:
  -h, --help     show this help message and exit
  --cache CACHE  cache directory, for storing models and datasets

```

Some example model IDs are:

  * `test-mnist-keras`: A simple smoke test that runs quickly (also, shows how to record visualization data for Tensorboard)
  * `CloudMask-0`: A more complex example that runs for a longer time, and requires ~2TB of storage for the dataset

### Example

```shell
$ python3 -msabath run test-mnist-keras
SABATH> 2022-05-17T20:50:07.829 : SABATH initialized
...
SABATH> 2022-05-17T20:50:28.966 : REPORT DIRECTORY: ./report-.../
```

Afterwards, all relevant information is stored in the report directory (which has a timestamp of when it was ran)

To prevent re-downloading, SABATH uses a cache directory (`./.sabath`, by default, which is ignored by git) to store models and datasets. If you already have a dataset downloaded, you can create a symbolic link to that other path. For example, on ICL's guyot machine, I have a `/data` directory that contains some datasets already. So, I recommend running:


```shell
$ ln -s /data/slstr_cloud_ds1 ./.sabath/slstr_cloud_ds1
```

To prevent re-downloading the large dataset. You can also specify running with different cache directories with `--cache` option


### Tensorboard

For visualization with Tensorboard, specifically on a remote server, you can use the following command:

```shell 
# forward port 9999 to your local machine
$ ssh -L 9999:127.0.0.1:9999 user@guyot.icl.utk.edu
# run visualization from the report's tensorboard directory
$ tensorboard --port 9999 --logdir ./report-.../tensorboard
```

# OLD PROTOTYPE - slip

SLIP (Surrogate Launching and Integration Platform) is a software ecosystem for downloading and running ML/AI benchmarks.

This is currently an expiremental prototype. There will be bugs!

## Usage

To get started, first clone this repo:

```sh
$ git clone https://github.com/icl-utk-edu/slip
```

Then, install any dependencies:

```sh
$ pip3 install -r requirements.txt
```

(TODO: dependencies are actually more complicated. it is assumed that Tensorflow/etc are installed via your distribution/hardware configuration)

To actually run a benchmark, type:

```sh
$ python3 slip.py run test-mnist-keras
...
[==============================] - 1s 1ms/step - loss: 0.1663 - sparse_categorical_accuracy: 0.9524 - val_loss: 0.1478 - val_sparse_categorical_accuracy: 0.9552
Epoch 3/6
...
```

Some nice example models:

  * `python3 slip.py run test-mnist-keras`: simple, fast example using MNIST
  * `python3 slip.py run CloudMask-0`: implementation of a real-world scientific benchmark (**requires 180GB of disk usage**)


When running a benchmark, SLIP automatically downloads and sets up the code and data.

**IMPORTANT**: If you have corrupted files, or want to restart, either remove the entire `./cache` directory (all datasets/models), or a specific ID within that directory

## Machine-Specific

### ICL's guyot

To run on guyot (ICL's DGX machine), you will need to:

```shell
# load my packages
$ source ~cade/load_guyot.sh
```

NOTE: you may need to load other packages, depending on what libraries the model you're running requires


