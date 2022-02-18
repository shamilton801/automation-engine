docker stop $(docker container ls -q)
docker system prune -af