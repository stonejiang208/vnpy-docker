# vnpy:dev
FROM mastone208/python-dev:v2 
MAINTAINER Stone Jiang <jiangtao@tao-studio.net>

ENV DEBIAN_FRONTEND noninteractive

ADD vnpy /opt/vnpy
RUN cd /opt/vnpy && python -m pip install . --user


