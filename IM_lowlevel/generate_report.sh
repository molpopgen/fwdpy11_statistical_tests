#!/bin/sh

docker build --build-arg tag=$TAG . -t im_lowlevel:$TAG
docker run -v $PWD:/mnt im_lowlevel:$TAG /bin/bash -c "snakemake -j $CORES --config nreps=$NREPS && snakemake --report /mnt/report.html"
docker image rm -f im_lowlevel:$TAG
