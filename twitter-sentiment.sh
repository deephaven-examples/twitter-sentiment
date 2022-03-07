docker build --target ts-server -t twitter-sentiment/ts-server .
docker build --target ts-web -t twitter-sentiment/ts-web .
docker build --target twitter-sent -t twitter-sentiment/twitter-sent .
docker-compose up
