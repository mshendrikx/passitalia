docker compose -f /home/msh/docker/compose/docker-compose.yml down passitalia
docker rmi mservatius/passitalia:latest
docker build -t passitalia:latest .
docker tag passitalia:latest mservatius/passitalia:latest
docker push mservatius/passitalia:latest
docker rmi passitalia:latest
docker rmi mservatius/passitalia:latest
docker compose -f /home/msh/docker/compose/docker-compose.yml up passitalia -d