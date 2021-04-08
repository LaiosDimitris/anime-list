from discord.ext.commands.bot import Bot
from BotCommands import BotCommands
from discord.ext import commands
import json

client = commands.Bot(command_prefix='!')

botCommands = BotCommands()

############ E V E N T S #############
@client.event
async def on_ready():
    print(f"We have logged in as {client.user}\n")
    client.loop.create_task(episodeNotifications())

@client.event
async def on_guild_join(guild):
    botCommands.addServerToDatabase(guild.name)

############ C O M M A N D S ##############
@client.command()
async def anime(ctx, *, query: str):
    if ctx.channel.name != '🈶anime':
        return
    discordEmbed = botCommands.anime(query)
    if discordEmbed == None:
        await ctx.channel.send(f':x: Could not find information about **{query}**')
    else:
        await ctx.channel.send(f"{ctx.message.author.mention} Here's the info you asked!", embed=discordEmbed)

@client.command()
async def notify(ctx, *, query: str):
    if ctx.channel.name != '🈶anime':
        return
    result = botCommands.notify(ctx.guild.name, query)
    if result == None:
        await ctx.channel.send(':x: *An unexpected error occured while fetching information.*')
    elif result[0] == 'Already in database':
        await ctx.channel.send(f":x: **{result[1]['title']}** is already in the database!")
    elif result[0] == 'Not airing':
        await ctx.channel.send(f":x: **{result[1]['title']}** is not currently airing!")
    else:
        await ctx.channel.send(f"{ctx.message.author.mention} You're ready!", embed=result[1])

@client.command()
async def delete(ctx, *, query: str):
    if ctx.channel.name != '🈶anime':
        return
    result = botCommands.delete(ctx.guild.name, query)
    if result == None:
        await ctx.channel.send(':x: *An unexpected error occured while fetching information from the database.*')
    elif result[0] == 'Not in database':
        await ctx.channel.send(f":x: **{result[1]['title']}** is not in the database!")
    else:
        await ctx.channel.send(f":white_check_mark: **{result[1]['title']}** Has been removed from the database!")

@client.command()
async def trailer(ctx, *, query: str):
    if ctx.channel.name != '🈶anime':
        return
    trailerLink = botCommands.trailer(query)
    if trailerLink == None:
        await ctx.channel.send(f':x: Could not trailer about **{query}**')
    else:
        await ctx.channel.send(f"{ctx.message.author.mention} Here's the trailer for **{trailerLink[1]['title']}**!\n{trailerLink[0]}")

@client.command()
async def broadcast(ctx, *, query: str):
    if ctx.channel.name != '🈶anime':
        return
    timeLeft = botCommands.broadcast(query)
    if timeLeft == None:
        await ctx.channel.send(':x: *An unexpected error occured while fetching information.*')
    elif timeLeft == 'Not airing':
        await ctx.channel.send(f':x: **{query.title()}** is not currently airing!')
    else:
        await ctx.channel.send(f"{ctx.author.mention} Japanese broadcast of **{timeLeft['anime']}** Episode {timeLeft['episode']}\nwill start in ***{timeLeft['broadcast']}*** :alarm_clock:")

@client.command()
async def list(ctx):
    if ctx.channel.name != '🈶anime':
        return
    animeListOfServer = botCommands.list(ctx.guild.name)
    if animeListOfServer == None:
        await ctx.channel.send(':x: *An unexpected error occured while fetching information from the database.*')
    if animeListOfServer == 'Empty list':
        await ctx.channel.send(f':x: No anime listed on **{ctx.guild.name}**!')
    else:
        await ctx.channel.send(f"{ctx.message.author.mention} Here's all the anime listed on **{ctx.guild.name}**", embed=animeListOfServer)

async def sendNotification(notif: dict):
    try:
        channel = [channel for guild in client.guilds if guild.name == notif['server'] for channel in guild.text_channels if channel.name == '🈶anime'][0]
        msg = f"@everyone **{notif['anime']}** *Episode {notif['episode']} is out!!!*\n{notif['url']}"
        if notif['title'] != None:
            msg = f"@everyone **{notif['anime']}** *Episode {notif['episode']}: **{notif['title']}** is out!!!*\n{notif['url']}"
        await channel.send(msg)
        if notif['finished']:
            await channel.send('***This is the last episode of this season!***  :sob:')
    except Exception as channelError:
        print('Error occured while searching for text channel...')
        print(channelError)

async def episodeNotifications():
    await client.wait_until_ready()
    while True:
        notifications = await botCommands.episodeNotifications()
        for notification in notifications:
            await sendNotification(notification)
        
############## S T A R T   B O T ################# 
if __name__ == "__main__":
    with open(r'..\data\token.json', 'r') as jsonFile:
        client.run(json.load(jsonFile)['token'])
