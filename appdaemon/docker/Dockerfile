ARG BASE_IMAGE
#FROM acockburn/appdaemon:${BASE_IMAGE}
FROM ${BASE_IMAGE}

RUN pip3 install \
      attrs==19.1.0 \
      emp_mos_api==0.10 \
      packaging==16.8 \
      python-Levenshtein==0.12.0 \
      voluptuous==0.11.5 \
      noolite==1.4.0 && \ 
      apk add --no-cache libusb-dev
      #apt-get update && apt-get install -y libusb-1.0.0-dev && apt-get clean
