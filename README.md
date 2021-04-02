# Intro

## Test layout

Each set of tests are in their own subdirectory.
Each subdirectory contains a `README` file.
The tests are automated with [`snakemake`](https://snakemake.readthedocs.io/en/stable/).

## Running the tests

The tests are meant to be run in a Docker container.
We do this so that we don't have to worry about system installs, and Python dependencies are correctly handled for each set of tests.
To run the tests, execute the `generate_report.sh` script found in the test subdirectory.
The output will be an `html` report.

### Why not virtual environments?

`snakemake` requires system libraries for report generation.
We don't want to have to worry about that on every possible system, so we use an Ubuntu environment for all test runs via Docker.

### Changing default parameters.

* Copy `config.yaml` to `myconfig.yaml`
* Change values in `myconfig.yaml`
* Execute the report generation step.
