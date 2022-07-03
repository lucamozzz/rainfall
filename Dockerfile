FROM node:16.14.2-slim AS frontend

RUN mkdir /app
WORKDIR /app

COPY simple-ui ./

RUN yarn
RUN yarn build


FROM python:3.9-slim AS backend

ARG PORT=5000
ENV PORT=${PORT}
ARG SSH_KEY
ENV MODE=PRODUCTION

RUN mkdir /app
WORKDIR /app
RUN mkdir -p output_repositories/.archive

RUN apt-get -y update
RUN apt-get -y install git

RUN mkdir -p /root/.ssh && chmod 0700 /root/.ssh && ssh-keyscan github.com > /root/.ssh/known_hosts
RUN echo "${SSH_KEY}" > /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa

COPY simple-backend/simple_backend simple_backend/
COPY simple-backend/requirements.txt ./
RUN pip install -r requirements.txt

COPY --from=frontend /app/dist/spa /app/simple_backend/static

CMD gunicorn --bind 0.0.0.0:${PORT} -t 0 -w 4 -k uvicorn.workers.UvicornWorker --pythonpath simple_backend app:create_app

EXPOSE ${PORT}