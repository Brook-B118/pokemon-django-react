FROM python:3.12-bookworm@sha256:a3dd99f0012a21776ef49aa3698aed044be9c8404dc6c89137ffcc275928e65c

WORKDIR /app

COPY pokemon-project/ .

RUN groupadd -r appuser && \
    useradd  -r -g appuser appuser &&\
    chown -R appuser /app

RUN pip install --no-cache-dir -r requirements.txt

USER appuser:appuser

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

