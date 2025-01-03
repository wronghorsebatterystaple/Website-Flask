# SYNC: all filepaths and names

FROM nikolaik/python-nodejs:python3.10-nodejs23-slim

EXPOSE 8008

RUN mkdir personal-website/
WORKDIR /personal-website/

COPY app/ app/
COPY migrations/ migrations/
COPY personal_website.py config.py ./

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR ./app/static/
RUN npm run compile_bootstrap
WORKDIR ../../

COPY deployment/docker/flask/entrypoint.sh ./
RUN chmod a+x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
