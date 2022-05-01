# slip

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


