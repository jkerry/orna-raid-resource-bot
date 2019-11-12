import discord
import discord_parsers
import configargparse

p = configargparse.ArgParser(default_config_files=['./*.conf'])
p.add('-t', '--token', required=True, env_var='DISCORD_BOT_TOKEN', help='Discord bot token')

options = p.parse_args()
client = discord.Client()
parser = discord_parsers.MessageParser()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('%raid'):
        response = parser.parse_command(message)
        await message.channel.send(response)

client.run(options.token.strip())