FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Vienna
RUN apt update && apt install --no-install-recommends -y \
    tzdata \
    python3-setuptools \
    python3-pip \
    python3 \
    python3-yaml \
    python3-prometheus-client

WORKDIR /usr/src/app
## install python modules
# COPY ./build/requirements.txt ./
RUN pip3 install --break-system-packages --disable-pip-version-check --no-cache-dir bleak
RUN pip3 freeze
# this changes very often so put it at the end of the main section
COPY build/main.py /usr/src/app/main.py

# cleanup
# starting at 471MB
# with updates 473MB
# down to 227MB
RUN apt -y purge python3-pip python3-setuptools; \
    apt -y autoremove; \
    apt -y clean;

# add HEALTHCHECK command to check is container is running
# HEALTHCHECK --interval=5m --timeout=3s CMD curl -I http://localhost:9100/ || exit 1

# as of ubuntu:24.04 there is a ubuntu user preinstalled
USER ubuntu
CMD ["python3", "-u", "/usr/src/app/main.py"]
