#!/bin/sh

docker build --build-arg tag=$TAG . -t im_lowlevel
docker run -v $PWD:/mnt im_lowlevel /bin/bash -c "snakemake -j $CORES && snakemake --report /mnt/report.html"
docker image rm -f im_lowlevel
