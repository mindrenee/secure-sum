FROM python:3
ADD peer.py /
CMD [ "python", "./peer.py" ]