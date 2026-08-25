#!/bin/bash

cd "$(dirname "$0")"

> .env
chmod 600 .env

STRING=$(aws secretsmanager get-secret-value --secret-id <your-secret-name> --region us-east-1 --query SecretString --output text | jq -c 'to_entries[]')

while read -r line; do
  echo "$line" | jq -r '"\(.key)=\(.value)"' >> .env
done <<< "$STRING"

docker compose -f docker-compose.prod.yaml up -d