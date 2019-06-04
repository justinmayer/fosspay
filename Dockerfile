FROM python:3.7-alpine as base
LABEL maintainer="Justin Mayer <https://justinmayer.com/>"

FROM base as pydeps

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

RUN \
    apk add --no-cache libpq postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc libffi-dev musl-dev postgresql-dev && \
    python3 -m pip install --install-option="--prefix=/install" -r /requirements.txt --no-cache-dir && \
    apk --purge del .build-deps


FROM base as assets

RUN apk add --no-cache make
RUN mkdir -p /assets/static
WORKDIR /assets

COPY Makefile /assets/Makefile
COPY scripts /assets/scripts
COPY _static /assets/_static

RUN make


FROM base

COPY --from=pydeps /install /usr/local
RUN apk --no-cache add libpq
RUN mkdir /app
COPY --from=assets /assets/static /app/static
COPY . /app

WORKDIR /app

CMD ["gunicorn", "app:app"]
