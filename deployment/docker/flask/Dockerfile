# SYNC: all filepaths and names

FROM python:3.10

EXPOSE 8008

RUN mkdir personal-website/
WORKDIR /personal-website/

COPY app/ app/
COPY migrations/ migrations/
COPY personal_website.py config.py ./

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY requirements_testpypi.txt requirements_testpypi.txt
RUN pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple -r requirements_testpypi.txt

WORKDIR ./app/static/
RUN apt update -y
RUN apt upgrade -y
RUN apt install npm -y
RUN npm run compile_bootstrap
WORKDIR ../../

COPY deployment/docker/flask/entrypoint.sh ./
RUN chmod a+x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
