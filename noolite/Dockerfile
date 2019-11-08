FROM python:latest

RUN pip3 install homie noolite && \
    apt-get update && apt-get install -y libusb-1.0.0-dev && apt-get clean
ADD noolitemqtt.py /noolitemqtt.py

CMD python3 /noolitemqtt.py