docker build --build-arg IMAGE_TYPE=elite -t sovits:latest .
docker-compose -p model up --build --force-recreate -d