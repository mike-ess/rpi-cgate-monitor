# Pull base images
FROM resin/raspberrypi3-python:3.6.1

# Install requests library (sourced from https://pypi.python.org/pypi/requests)
WORKDIR /tmp/python-packages/requests
ADD python-packages/requests/requests-2.19.1.tar.gz .
WORKDIR requests-2.19.1
RUN python3 setup.py install

# Install requests-oauthlib library (sourced from https://pypi.org/project/requests-oauthlib/)
WORKDIR /tmp/python-packages/requests-oauthlib
ADD python-packages/requests-oauthlib/requests-oauthlib-1.0.0.tar.gz .
WORKDIR requests-oauthlib-1.0.0
RUN python3 setup.py install

# Install C-Gate Monitor scripts
WORKDIR /python/cgate-monitor
COPY cgate-monitor/cgate_monitor.py /python/cgate-monitor/
COPY cgate-monitor/cgate_client.py  /python/cgate-monitor/

# Install other scripts
WORKDIR /python/utilities
COPY utilities/messenger.py  /python/utilities/
COPY utilities/logger_ini.py /python/utilities/

# Install shell script
WORKDIR /python
COPY cgate-monitor.sh /python
RUN chmod 755 /python/cgate-monitor.sh

WORKDIR /python
ENTRYPOINT ["/python/cgate-monitor.sh"]

