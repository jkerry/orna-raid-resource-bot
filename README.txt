docker run -d -p 27017-27019:27017-27019 --hostname mongodb -v mongodb:/data/db --name mongodb mongo:latest
docker build . -t jkerry/orna-raid-resource-bot:dev
docker run -d --name orrb `
    --link=mongodb `
    --env DISCORD_BOT_TOKEN="<TOKEN>" `
    --env ORNA_BOT_DATASOURCE="mongodb://mongodb:27017" `
    jkerry/orna-raid-resource-bot:dev