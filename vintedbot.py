import os, sqlite3, asyncio
import discord
from discord import app_commands
from discord.ext import commands

TOKEN        = os.environ["DISCORD_TOKEN"]
CATEGORY_ID  = int(os.environ["DISCORD_CATEGORY_ID"])  # put your category ID here

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Database setup
conn = sqlite3.connect("subscriptions.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS subs (channel_id INTEGER, url TEXT)")
conn.commit()

@bot.event
async def on_ready():
    await bot.tree.sync()  # sync slash commands
    print(f"✅ Logged in as {bot.user}")

# /vinted command
@bot.tree.command(name="vinted", description="Create a Vinted watcher channel")
@app_commands.describe(url="The Vinted search URL with filters", channel_name="Name of the new channel")
async def vinted(interaction: discord.Interaction, url: str, channel_name: str):
    category = discord.utils.get(interaction.guild.categories, id=CATEGORY_ID)
    if not category:
        await interaction.response.send_message("❌ Category not found.", ephemeral=True)
        return

    # Create the channel
    channel = await interaction.guild.create_text_channel(channel_name, category=category)

    # Save mapping
    cur.execute("INSERT INTO subs (channel_id, url) VALUES (?, ?)", (channel.id, url))
    conn.commit()

    await interaction.response.send_message(f"✅ Created {channel.mention} for {url}")

# Example polling loop (placeholder)
async def poll_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        cur.execute("SELECT channel_id, url FROM subs")
        for channel_id, url in cur.fetchall():
            channel = bot.get_channel(channel_id)
            if channel:
                # TODO: replace with actual fetching (email/RSS)
                await channel.send(f"(Checking for new items for: {url})")
        await asyncio.sleep(60)

class MyBot(commands.Bot):
    async def setup_hook(self):
        self.loop.create_task(poll_loop())

bot = MyBot(command_prefix="/", intents=discord.Intents.all())
bot.run(TOKEN)
