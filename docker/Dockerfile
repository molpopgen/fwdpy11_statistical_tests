ARG tag=latest

FROM molpopgen/fwdpy11:$tag

WORKDIR /app

COPY . /app

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -qq -y install graphviz \
  libgraphviz-dev \
  imagemagick \
  python3 \
  python3-pip \
  python3-wheel \
  python3-setuptools \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf output \
  && useradd testuser \
  && apt-get clean

RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Make WORKDIR the $HOME for testuser
RUN chown -R testuser:testuser /app \
  && usermod -d /app testuser \
  && rm -f requirements.txt

USER testuser