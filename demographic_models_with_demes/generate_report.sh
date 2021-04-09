#!/bin/sh

docker build --build-arg tag=$TAG . -t demes_statistical_tests:$TAG
docker run --rm -v $PWD:/mnt demes_statistical_tests:$TAG /bin/bash -c "snakemake all_models -j $CORES --config nreps=$NREPS && snakemake all_models --report /mnt/report.html"
