FROM python:3.10

EXPOSE 8008

RUN mkdir personal-website/
WORKDIR /personal-website/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app/ app/
COPY migrations/ migrations/
# SYNC: entrypoint script path
COPY personal_website.py config.py deployment/docker/flask/entrypoint.sh ./
RUN chmod a+x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
