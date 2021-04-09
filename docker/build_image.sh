#!/bin/sh

docker build --build-arg tag=$TAG . -t fwdpy11_statistical_tests:$TAG
