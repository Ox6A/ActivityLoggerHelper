import discord
import asyncio
import re
from datetime import datetime, timedelta
import time
from discord import app_commands

PDActivityChannel = 1269777958860492883

token = None
embed1 = None

intents = discord.Intents.default()
intents.message_content = True

class ActivityLogger(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = ActivityLogger(intents=intents)

def timeToSeconds(timeStr):
    hours, mins, seconds = map(int, timeStr.split(":"))
    return (hours * 3600) + (mins * 60) + seconds

async def fetchActivity(channel, steamID):
    global embed1
    totalSeconds = 0
    timeframe = datetime.now() - timedelta(days=7)
    async for message in channel.history(limit=None, after=timeframe):
        if message.embeds:
            content = message.embeds[0].description
            match = re.search(rf"\({steamID}\).*for `(\d{{2}}:\d{{2}}:\d{{2}})`", content)
            if match:
                timeStr = match.group(1)
                totalSeconds += timeToSeconds(timeStr)
    totalActivity = str(timedelta(seconds=totalSeconds))
    embed1 = discord.Embed(title="Activity Logged", description=f"`{steamID}` has been on PD for `{totalActivity}` for the past `1 week`", color=0x0483fb)    

@client.event
async def on_ready():
    print(f"Started as {client.user}")

@client.tree.command(name="activity", description="Fetch activity for a SteamID in the past week")
async def activity(interaction: discord.Interaction, steamid: str):
    global embed1
    global PDActivityChannel
    channelToBeUsed = None

    PDChannelObj = client.get_channel(PDActivityChannel)
    if PDChannelObj:
        permissions = interaction.user.permissions_in(PDChannelObj)
        if permissions.read_messages:
            hasPerms = True
            channelToBeUsed = PDChannelObj
        else:
            embed1 = discord.Embed(title="Permission Denied", description="You do not have the required permsisions to use this bot. If this in error, please contact `teasippingbrit` on Discord.", color=0xFF0000)
            await interaction.response.send_message(embed=embed1, ephemeral=True)
            return

    if channelToBeUsed == None:
        return
    if steamid.startswith("STEAM_"):
        await fetchActivity(channelToBeUsed, steamid)
        await interaction.response.send_message(embed=embed1, ephemeral=True)
    else:
        embed1 = discord.Embed(title="Invalid parameters", description="The SteamID supplied either does not exist, or is of an invalid format. Please enter the ID in this format: `STEAM_0:0:431471716`", color=0x0483fb)
        await interaction.response.send_message(embed=embed1, ephemeral=True)

def loadToken():
    global token
    try:
        with open("token.txt", "r") as f:
            token = f.read()
        return True
    except Exception as e:
        print(f"Error during init: Token loading failure: {repr(e)}")
        return False

def main():
    global token
    loadTokenResult = loadToken()
    if not loadTokenResult:
        return
    client.run(token)

if __name__ == "__main__":
    main()
