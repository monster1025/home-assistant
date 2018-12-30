ARG VERSION
FROM acockburn/appdaemon:${VERSION}

#log encoding temporary fix
RUN sed -i -e 's/safe_enc = lambda s: str(s).encode("utf-8", "replace").decode("ascii", "replace")/safe_enc = lambda s: str(s)/g' /usr/src/app/appdaemon/utils.py

RUN pip3 install \
      emp_mos_api==0.9 \
      sqlalchemy \
      mysqlclient