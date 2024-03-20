from config.config import token
from utils.logManager import logger
from routes.websocket import on_ready
from routes.messages import on_message
import discord


class MyClient(discord.Client):
    async def on_ready(self):
        await on_ready(self)

    async def on_message(self, message):
        await on_message(self, message)


if __name__ == '__main__':
    try:
        # Initialize
        intents = discord.Intents.default()
        intents.message_content = True
        client = MyClient(intents=intents)
        client.run(token)

    except Exception as e:
        print('Error')
        logger.exception(e)
        raise
