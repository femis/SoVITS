docker build --build-arg IMAGE_TYPE=elite -t sovits:latest .
docker-compose up --build --force-recreate -d