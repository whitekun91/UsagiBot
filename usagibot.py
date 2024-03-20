import discord
import json


with open('./UsagiBot/config/config.json', 'r') as f:
    json_config = json.load(f)

# Initialize
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
token = json_config['token']

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


client.run(token)
