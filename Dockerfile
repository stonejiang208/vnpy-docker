# vnpy:dev
FROM ubuntu:18.04 
MAINTAINER Stone Jiang <jiangtao@tao-studio.net>

ENV DEBIAN_FRONTEND noninteractive

#COPY sources.list /etc/apt/sources.list
RUN sed -i 's/archive.ubuntu.com/cn.archive.ubuntu.com/g' /etc/apt/sources.list
RUN apt-get update && apt-get install -y --no-install-recommends \
  software-properties-common \
  build-essential locales sudo tar gzip unzip net-tools \
  python3 python3-pip libpython3-dev \
  python-psycopg2 libpq-dev \
  git wget curl libgl1-mesa-glx tzdata && \
  apt-get autoremove -y && \
  apt-get autoclean && \
  rm -rf /var/lib/apt/lists/*
RUN cp /usr/bin/python3 /usr/bin/python && cp /usr/bin/pip3 /usr/bin/pip
  RUN locale-gen zh_CN.UTF-8 && \
  DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales
RUN locale-gen zh_CN.UTF-8
ENV LANG zh_CN.UTF-8
ENV LANGUAGE zh_CN:zh
ENV LC_ALL zh_CN.UTF-8
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 以下三行根据情况自选
RUN mkdir -p /opt/vnpy

#COPY  https://github.com/vnpy/vnpy/archive/v2.0.7.tar.gz  /opt/vnpy
#RUN git clone -b v2.0.7  https://github.com/vnpy/vnpy.git /opt/vnpy
RUN git clone --depth 1 -b dev git@github.com:stonejiang208/vnpy-docker.git /opt/vnpy
#ADD vnpy /opt/vnpy
RUN cd /opt/vnpy && bash ./install.sh

#RUN mkdir -p /app
#COPY main.py /app/

# WORKDIR /app
# CMD ["python","main.py"]

