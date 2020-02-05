docker run -d -p 27017-27019:27017-27019 --hostname mongodb --restart always -v mongodb:/data/db --name mongodb mongo:latest
docker build . -t jkerry/orna-raid-resource-bot:dev
docker run -d --name orrb `
    --link=mongodb `
    --env DISCORD_BOT_TOKEN="<token>" `
    --env ORNA_BOT_DATASOURCE="mongodb://mongodb:27017" `
    --restart always `
    jkerry/orna-raid-resource-bot:dev