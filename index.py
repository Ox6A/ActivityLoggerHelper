import discord
import asyncio
import re
import json
from datetime import datetime, timedelta
import time
from discord import app_commands

config = {}
debugMode = False

logo = """
                          ####+
                        +######+
                      +###########
                    +###############
                  +#+################+
                 ######################+
               ##########################+
             ############+++##############++                                     ++
           +#########+  ++##################+                                +##+
         +########+    +######################+                          -+####
       +######+      +#########################+#                     +######
      +###+        +#############################++               ++#######
    ###+         +##################################+         +##########+
  #+           +######################################+    +##########++
             +############+   +#####################################++
           ++#########+          ++################################+
          +########+                 ++###########################
        #######+                         #######################
      #####+                                +#################
    +###                                        +###########+
  +#+                                               #####++
                                                       ++                           """

token = None
embed1 = None

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True


class ActivityLogger(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        self.startTime = datetime.utcnow()
        print(f"\033[1mStarted as {self.user}\033[0m")
        await self.change_presence(activity=discord.Game(name="/activity"))


client = ActivityLogger(intents=intents)


async def sendErrorMsg(interaction):
    embed1 = discord.Embed(
        title="Error occured during runtime",
        description="A critical error occured whilst running the command. Please contact `teasippingbrit` on Discord.",
        color=0xFF0000,
    )
    await interaction.response.send_message(embed=embed1, ephemeral=True)


def timeToSeconds(timeStr):
    hours, mins, seconds = map(int, timeStr.split(":"))
    return (hours * 3600) + (mins * 60) + seconds


async def fetchActivity(channel, steamID):
    global embed1
    global config
    totalSeconds = 0
    timeframe = datetime.now() - timedelta(days=7)
    async for message in channel.history(limit=None, after=timeframe):
        if message.embeds:
            content = message.embeds[0].description
            match = re.search(
                rf"\({steamID}\).*for `(\d{{2}}:\d{{2}}:\d{{2}})`", content
            )
            if match:
                timeStr = match.group(1)
                totalSeconds += timeToSeconds(timeStr)
    totalActivity = str(timedelta(seconds=totalSeconds))
    channelName = list(config.keys())[list(config.values()).index(channel.id)].upper()
    if totalSeconds == 0:
        embed1 = discord.Embed(
            title="No Activity Logged",
            description=f"`{steamID}` has not been on {channelName} in the past `1 week`.",
            color=0x0483FB,
        )
    else:
        embed1 = discord.Embed(
            title="Activity Logged",
            description=f"`{steamID}` has been on {channelName} for `{totalActivity}` for the past `1 week`",
            color=0x0483FB,
        )


@client.tree.command(
    name="activity", description="Fetch activity for a SteamID in the past week"
)
async def activity(interaction: discord.Interaction, steamid: str):
    global embed1
    channelToBeUsed = None
    guildToBeUsed = None
    inEnabledGuild = False
    debuggingUserAllowed = False

    print(
        f"{datetime.now()} - {interaction.user.name} has searched the activity for {steamid}"
    )

    if debugMode == True:
        for i in config["debug_users"]:
            if i == interaction.user.id:
                debuggingUserAllowed = True
        if debuggingUserAllowed == False:
            embed1 = discord.Embed(
                title="Debugging Mode",
                description="The bot is currently in a debuggging mode for testing or maintenance. Sorry for the inconvenience!",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed1, ephemeral=True)
            return

    for i in config["guilds"]:
        if config["guilds"][i] == interaction.guild.id:
            for i1 in config["enabled_dept"]:
                if i1 == i:
                    guildToBeUsed = config["guilds"][i]
                    guildName = i
                    inEnabledGuild = True
    if inEnabledGuild == False:
        print("\033[93m\033[1mWARNING: Command sent in a disallowed guild\033[0m")
        return
    ChannelObj = client.get_channel(config["channelid"][guildName])
    if ChannelObj:
        try:
            caller = interaction.guild.get_member(interaction.user.id)
            if caller:
                permissions = ChannelObj.permissions_for(caller)
                if permissions.read_messages:
                    channelToBeUsed = ChannelObj
                else:
                    embed1 = discord.Embed(
                        title="Permission Denied",
                        description="You do not have the required permsisions to use this bot. If this in error, please contact `teasippingbrit` on Discord.",
                        color=0xFF0000,
                    )
                    await interaction.response.send_message(
                        embed=embed1, ephemeral=True
                    )
                    return
            else:
                await sendErrorMsg(interaction)
                return
        except Exception as e:
            with open("errors.log", "a") as f:
                f.write(e)
            await sendErrorMsg(interaction)
            return
    else:
        embed1 = discord.Embed(
            title="Channel not found",
            description="The logging channel was not found. This is likely a configuration error, or the result of changes to the logging channels. Please contact `teasippingbrit` on Discord.",
            color=0xFF0000,
        )
        await interaction.response.send_message(embed=embed1, ephemeral=True)

    if channelToBeUsed == None:
        return
    if steamid.startswith("STEAM_"):
        await fetchActivity(channelToBeUsed, steamid)
        await interaction.response.send_message(embed=embed1, ephemeral=True)
    else:
        embed1 = discord.Embed(
            title="Invalid parameters",
            description="The SteamID supplied either does not exist, or is of an invalid format. Please enter the ID in this format: `STEAM_0:0:431471716`",
            color=0x0483FB,
        )
        await interaction.response.send_message(embed=embed1, ephemeral=True)


def loadToken():
    global token
    try:
        print("\033[1mLoading token...\033[0m")
        with open("token.txt", "r") as f:
            token = f.read()
        return True
    except Exception as e:
        print("\033[1m\033[91mERROR DURING LOADING BOT TOKEN: " + str(e) + "\033[0m")
        return False


def loadConfig():
    global config
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        return True
    except Exception as e:
        print(
            "\033[93m\033[1mWARNING: Configuration loading failed. Attempting to create configuration files with error: "
            + str(e)
            + "\033[0m"
        )
        print("\033[1mGenerating default configuration...\033[0m")
        try:
            with open("config.json", "w") as f:
                config = {
                    "channelid": {
                        "pd": 1090365529564385310,
                        "so2": 1141061367730806906,
                        "sco": 1081600560060444885,
                        "nca": 1079508453241917653,
                        "nhs": 1117803842646585424,
                        "rs": 1100029126758375485,
                        "t": 1210141399878737920,
                        "test": 1269777958860492883,
                    },
                    "guilds": {
                        "pd": 472520717515096078,
                        "so2": 472520717515096078,
                        "sco": 472534240576143401,
                        "nca": 473075559409385472,
                        "nhs": 472537475605069825,
                        "rs": 472897608759771146,
                        "t": 472715289516048385,
                        "test": 1264515893610680393,
                    },
                    "enabled_dept": ["test", "pd", "so2"],
                    "minimum_role_requirement": {
                        "pd": 1179100367083016233,
                        "so2": 811356656276865034,
                        "sco": 811699338253172736,
                        "nca": 1241570118014599278,
                        "nhs": 752960738544451715,
                        "rs": 752961417606332506,
                        "t": 752961594194919478,
                        "test": 1272168995419717713,
                    },
                    "debug_users": ["743066712810717295"],
                    "debug": False,
                }
                json.dump(config, f)
            return True
        except Exception as e1:
            print(
                "\033[1m\033[91mERROR DURING LOADING CONFIGURATION: "
                + str(e1)
                + "\033[0m"
            )
            return False


def main():
    global token
    global debugMode
    print(
        "\n\033[1m\033[94mRiverside Activity Calculator Bot: Starting...\033[0m\n"
        + logo
    )
    loadTokenResult = loadToken()
    if not loadTokenResult:
        return
    print(
        "\033[1mSuccessfully loaded bot token!\n\nLoading configuration files...\033[0m"
    )
    loadConfigResult = loadConfig()
    if not loadConfigResult:
        return
    print("\033[1mSuccessfully loaded configuration!\033[0m\n")
    if config["debug"] == True:
        debugMode = True
        print("\033[1m\033[91mWARNING: Running in debug mode!\033[0m")
    print("\033[1mStarting bot...\033[0m")
    client.run(token)


if __name__ == "__main__":
    main()
