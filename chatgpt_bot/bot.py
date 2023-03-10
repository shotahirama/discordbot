import discord
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path
import os

import openai

load_dotenv(verbose=True)

dotenv_path = Path(os.path.dirname(__file__)) / ".env"

load_dotenv(dotenv_path)

GUILD = discord.Object(os.environ.get("GUILD_ID"))

openai.organization = os.environ.get("OPENAI_ORGANIZATION")
openai.api_key = os.environ.get("OPENAI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='ChatGPT>', intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.listen()
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    if len(message.mentions) == 1 and bot.user.mentioned_in(message=message):
        chatgpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": message.clean_content
                }
            ]
        )
        chat_response = chatgpt_response["choices"][0]["message"]["content"]
        await message.channel.send(f"{message.author.mention} {chat_response}")

bot.run(os.environ.get("DISCORD_TOKEN"))
