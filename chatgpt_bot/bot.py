import discord
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path
import os
import re

import traceback

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

async def chatgpt_request(message_list: discord.Message):
    messages = list(map(lambda message: {"role": "assistant" if message.author == bot.user else "user", "content": extract_text(message.content)}, message_list))
    chatgpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    chat_response = chatgpt_response["choices"][0]["message"]["content"]
    return chat_response

def extract_text(message_content):
    text = re.sub(r'<@!?(\d+)>', '', message_content)
    text = re.sub(r'<:(\w+):(\d+)>', '', text)
    text = re.sub(r'<a?:(\w+):(\d+)>', '', text)
    text = text.strip()
    return text


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.listen()
async def on_message(message: discord.Message):
    try:
        if message.author.bot:
            return
        if message.author == bot.user:
            return
        if len(message.mentions) == 1 and bot.user.mentioned_in(message=message):
            async with message.channel.typing():
                chat_message_list = [message]
                if message.reference is not None:
                    past_message = await message.channel.fetch_message(message.reference.message_id)
                    for _ in range(4):
                        chat_message_list.append(past_message)
                        if past_message.reference is None:
                            break
                        past_message = await past_message.channel.fetch_message(past_message.reference.message_id)
                    chat_message_list.reverse()
                bot_message = await chatgpt_request(message_list=chat_message_list)
                await message.reply(bot_message)
    except:
        traceback.print_exc()

bot.run(os.environ.get("DISCORD_TOKEN"))
