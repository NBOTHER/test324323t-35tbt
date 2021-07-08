
from http import client

print("----------------------------")
import asyncio
import os
import platform
import random
import sys
import json
import discord
import yaml
import aiohttp
import requests
import time
import datetime

from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord import Game
from requests.exceptions import RequestException




if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


intents = discord.Intents.default()

bot = Bot(command_prefix=config["bot_prefix"], intents=intents)

start_time = time.time()

# The code in this even is executed when the bot is ready
@bot.event
async def on_ready():
    print("----------------------------")
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("----------------------------")
    print(f'Servers: {len(bot.guilds)}')
    status_task.start()
    for guild in bot.guilds:
        print(guild.name)
    print("----------------------------")


members = sum([guild.member_count for guild in bot.guilds])

@bot.event
async def on_server_join(server):
  print('Joined ' + server.name)

# Setup the game status task of the bot
@tasks.loop(minutes=1.0)
async def status_task():
    statuses = [ "!help", "Changelog"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))

bot.remove_command("help")

if __name__ == "__main__":
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")


# The code in this event is executed every time someone sends a message, with or without the prefix
@bot.event
async def on_message(ctx):
    # Ignores if a command is being executed by a bot or by the bot itself
    if ctx.author == bot.user or ctx.author.bot:
        return
    # Ignores if a command is being executed by a blacklisted user

    if ctx.author.id in config["blacklist"]:
        return
    await bot.process_commands(ctx)


# The code in this event is executed every time a command has been *successfully* executed
@bot.event
async def on_command_completion(ctx):
    fullCommandName = ctx.command.qualified_name
    split = fullCommandName.split(" ")
    executedCommand = str(split[0])
    print(
        f"Executed {executedCommand} command in {ctx.guild.name} (ID: {ctx.message.guild.id}) by {ctx.message.author} (ID: {ctx.message.author.id})")


# The code in this event is executed every time a valid commands catches an error
@bot.event
async def on_command_error(context, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="Error!",
            description="This command is on a %.2fs cool down" % error.retry_after,
            color=config["error"]
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            description="You are missing the permission `" + ", ".join(
                error.missing_perms) + "` to execute this command!",
            color=config["error"]
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            description="You are missing the required arguments to run this command",
            color=config["error"]
        )
        await context.send(embed=embed)

@bot.command()
async def ping(ctx):
    embed = discord.Embed(title="Ping", description=f'✅ Bots latency is {bot.latency}', color=config["main_color"])
    await ctx.send(embed=embed)

@bot.command()
async def uptime(ctx):
    current_time = time.time()
    difference = int(round(current_time - start_time))
    text = str(datetime.timedelta(seconds=difference))
    embed = discord.Embed(colour=config["main_color"])
    embed.add_field(name="Uptime", value=text)
    embed.set_footer(text=f"{text}")
    await ctx.send(embed=embed)


@bot.command()
async def shutdown(ctx):
    if ctx.author.id in config["owners"]:
        await ctx.send('Shutting down...')
        quit()    
    if ctx.author.id not in config["owners"]:
        await ctx.send('You need to be the owner of the bot to run this command')


bot.run(config["token"])
