docker build --target ts-server -t twitter-sentiment/ts-server .
docker build --target ts-web -t twitter-sentiment/ts-web:latest .
docker build --target twitter-sent -t twitter-sentiment/twitter-sent:latest .
docker-compose up
