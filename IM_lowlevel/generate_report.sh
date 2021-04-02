#!/bin/sh

docker build --build-arg cores=12 --build-arg tag=stable . -t im_lowlevel
docker run -v $PWD:/mnt im_lowlevel cp report.html /mnt/report.html
# docker image rm -f im_lowlevel
