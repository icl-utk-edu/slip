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
$ python3 slip.py run CloudMask-0
... (lots of output, perhaps errors)
```

When running a benchmark, SLIP automatically downloads and sets up the code and data.
