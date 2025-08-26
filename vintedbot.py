import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # get token from Render env
CATEGORY_ID = int(os.getenv("DISCORD_CATEGORY_ID", "0"))  # put your category ID in Render env

# --- background loop (replace with real Vinted API later) ---
async def poll_loop():
    await asyncio.sleep(5)  # wait until bot ready
    while True:
        print("🔎 Checking Vinted...")
        # TODO: fetch listings & send messages
        await asyncio.sleep(60)  # check every 60s


# --- custom bot class with setup_hook ---
class MyBot(commands.Bot):
    async def setup_hook(self):
        # start background task
        self.loop.create_task(poll_loop())
        # sync slash commands
        await self.tree.sync()

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

bot = MyBot(command_prefix="!", intents=intents)


# --- events ---
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


# --- slash command: /add ---
@bot.tree.command(name="add", description="Create a Vinted channel from a link")
@app_commands.describe(vinted_link="Paste your Vinted link with filters", channel_name="Name for the channel")
async def add_channel(interaction: discord.Interaction, vinted_link: str, channel_name: str):

    guild = interaction.guild
    category = discord.utils.get(guild.categories, id=CATEGORY_ID)

    if not category:
        await interaction.response.send_message("❌ Category not found. Check DISCORD_CATEGORY_ID.", ephemeral=True)
        return

    # create channel
    channel = await guild.create_text_channel(name=channel_name, category=category)

    # send first message with link
    await channel.send(f"🔗 Vinted link: {vinted_link}")

    await interaction.response.send_message(f"✅ Created channel <#{channel.id}> for {vinted_link}")


# --- run bot ---
bot.run(TOKEN)
