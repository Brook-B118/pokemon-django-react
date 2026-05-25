FROM python:3.12-bookworm@sha256:a3dd99f0012a21776ef49aa3698aed044be9c8404dc6c89137ffcc275928e65c

WORKDIR /app

COPY requirements.txt .

# Install system packages
RUN apt-get update && apt-get install -y \
    redis-server curl && \
    rm -rf /var/lib/apt/lists/*

RUN echo "maxmemory 50mb" >> /etc/redis/redis.conf && \
    echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf

RUN pip install --no-cache-dir -r requirements.txt

CMD ["bash"]

