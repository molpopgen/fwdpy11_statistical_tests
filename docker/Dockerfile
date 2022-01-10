ARG tag=latest

FROM molpopgen/fwdpy11:$tag

WORKDIR /app

COPY . /app

RUN sed -i '/^#\sdeb-src /s/^#//' "/etc/apt/sources.list" \
  && apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -qq -y install graphviz \
  libgraphviz-dev \
  python3 \
  python3-pip \
  python3-wheel \
  python3-setuptools \
  wget \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf output \
  && useradd testuser \
  && apt-get clean

# install imagemagick 7 from source
RUN apt update
RUN apt -qq -y build-dep imagemagick
RUN apt-get -qq -y install checkinstall libwebp-dev libopenjp2-7-dev librsvg2-dev libde265-dev 
RUN wget https://download.imagemagick.org/ImageMagick/download/ImageMagick-7.1.0-19.tar.gz 
RUN tar xzf ImageMagick-7.1.0-19.tar.gz 
RUN cd ImageMagick-7.1.0-19 \
&& ./configure --enable-shared --with-modules --with-gslib \
&& make -j 4 \
&& make install \
&& cd .. \
&& rm -rf ImageMagick*
RUN ldconfig

RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Make WORKDIR the $HOME for testuser
RUN chown -R testuser:testuser /app \
  && usermod -d /app testuser \
  && rm -f requirements.txt

USER testuser
