FROM python:3
ADD . /opt/fileserver007
WORKDIR /opt/fileserver007
RUN pip install .
RUN rm -r /opt/fileserver007
WORKDIR /
CMD fileserver007 -m web