ARG tag=latest
ARG cores=6

FROM molpopgen/fwdpy11:$tag

WORKDIR /app

COPY . /app

RUN if [ -e myconfig.yaml ]; then cat myconfig.yaml > config.yaml; fi

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -qq -y install graphviz \
  libgraphviz-dev \
  imagemagick \
  python3 \
  python3-pip \
  python3-wheel \
  python3-setuptools \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf output

RUN python3 -m pip install -r requirements.txt

RUN snakemake -j $cores

RUN snakemake --report report.html
