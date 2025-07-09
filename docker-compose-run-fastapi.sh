# #!/bin/bash
# source ./.env

# cp ./build/fastapi/dockerfile .
# cp ./build/fastapi/docker-compose.yaml .
# docker compose down -v && docker compose up --build 
# rm -fr ./docker-compose.yaml
# rm -fr ./dockerfile

#!/bin/bash
set -e

source ./.env

# Copy Dockerfile & docker-compose.yaml dengan nama yang dikenali Docker
cp ./build/fastapi/dockerfile ./Dockerfile
cp ./build/fastapi/docker-compose.yaml ./docker-compose.temp.yaml

# Jalankan Docker Compose
docker compose -f docker-compose.temp.yaml down -v --remove-orphans
docker compose -f docker-compose.temp.yaml up --build

# Bersihkan file sementara
rm -f ./docker-compose.temp.yaml
rm -f ./Dockerfile
