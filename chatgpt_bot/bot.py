import discord
import discord.app_commands
from dotenv import load_dotenv
from pathlib import Path
import os

import traceback

import openai

load_dotenv(verbose=True)

dotenv_path = Path(os.path.dirname(__file__)) / ".env"

load_dotenv(dotenv_path)

GUILD = discord.Object(os.environ.get("GUILD_ID"))

openai.organization = os.environ.get("OPENAI_ORGANIZATION")
openai.api_key = os.environ.get("OPENAI_API_KEY")


class MyClient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("-----------")

    async def setup_hook(self) -> None:
        await self.tree.sync(guild=GUILD)


class Feedback(discord.ui.Modal, title="ChatGPT"):
    chat = discord.ui.TextInput(
        label="ChatGPTに聞きたいことは?",
        style=discord.TextStyle.long,
        placeholder="Type your here...",
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        chatgpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": self.chat.value
                }
            ]
        )
        chat_response = chatgpt_response["choices"][0]["message"]["content"]

        username = interaction.user.name
        send_txt = f"{username}：\n{self.chat.value}\n\nChatGPT：\n{chat_response.strip()}"

        await interaction.followup.send(f"{send_txt}", ephemeral=False)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("Oops! Something went wrong.", ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)


client = MyClient()


@client.tree.command(guild=GUILD, description="ChatGPT")
async def chatgpt(interaction: discord.Interaction):
    await interaction.response.send_modal(Feedback())

client.run(os.environ.get("DISCORD_TOKEN"))
