# Intro

## Running the tests

### Docker

```sh
docker build --build-arg cores=12 . -t stat_tests
```

To run the suite against the latest stable release:

```sh
docker build --build-arg cores=12 --build-arg tag=stable . -t stat_tests
```

#### Copying results back from Docker

```sh
docker run -v $PWD:/mnt stat_tests cp report.html /mnt/report_tagname.html
```

#### Changing default parameters.

* Copy `config.yaml` to `myconfig.yaml`
* Change values in `myconfig.yaml`
* Execute the `docker build` step.
