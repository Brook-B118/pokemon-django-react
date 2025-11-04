FROM python:3.12-bookworm@sha256:a3dd99f0012a21776ef49aa3698aed044be9c8404dc6c89137ffcc275928e65c

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash"]

