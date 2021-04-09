# Intro

## Test layout

Each set of tests are in their own subdirectory.
Each subdirectory contains a `README` file.
The tests are automated with [`snakemake`](https://snakemake.readthedocs.io/en/stable/).

## Building common Docker image

```sh
cd docker
bash build_image.sh
```

## Running the tests

The tests are meant to be run in a Docker container.
Add tests create their own images based on the common image.
We do this so that we don't have to worry about system installs, and Python dependencies are correctly handled for each set of tests.
To run the tests, execute the `generate_report.sh` script found in the test subdirectory.
The output will be an `html` report.

Proper test execution requires specifying the Docker image tag and the number of cores to use.
The tag values must be one of `latest` or `stable`.

For example:

```sh
TAG=latest CORES=12 N REPS=128 bash generate_report.sh
```

### Why not virtual environments?

`snakemake` requires system libraries for report generation.
We don't want to have to worry about that on every possible system, so we use an Ubuntu environment for all test runs via Docker.

