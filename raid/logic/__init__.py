import discord
from raid.logic.discord_parsers import MessageParser

client = discord.Client()
parser = MessageParser(client)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('%raid post allotment'):
        response = await parser.send_allotment(message)
        if response is None:
            return response
        await message.channel.send(response)
    elif message.content.startswith('%raid'):
        response = parser.parse_command(message)
        if response is None:
            return response
        await message.channel.send(response)

def init(options):
    parser.set_datasource(options.datasource.strip())
    client.run(options.token.strip())
