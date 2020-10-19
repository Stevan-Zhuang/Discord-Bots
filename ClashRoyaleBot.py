# Unfinished

import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import clashroyale
from collections import Counter

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN_CLASH')
DEVELOPER_TOKEN = os.getenv('DEVELOPER_TOKEN_CLASH')

bot = commands.Bot(command_prefix='!', case_insensitive=True)
cr_client = clashroyale.official_api.Client(DEVELOPER_TOKEN)

class Globals:
    bot_id = 749852814892728352
    player_tags = {}
    stats_message = None
    log_message = None
    log = None
    log_index = 0
    usage_message = None

globals = Globals()

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online")

@bot.command(name='save')
async def save(ctx, player_tag=None):
    player = None
    try: player = cr_client.get_player(player_tag)
    except: await ctx.send("Player tag not found.")
    if player is not None:
        globals.player_tags[f"{ctx.message.author.id}"] = player_tag
        await ctx.send("Player tag saved.")

@bot.command(name='get')
async def get(ctx, player_tag=None):
    if player_tag is None:
        try: player_tag = globals.player_tags[f"{ctx.message.author.id}"]
        except: await ctx.send("No player tag specified.")
    player = None
    if player_tag is not None:
        try: player = cr_client.get_player(player_tag)
        except: await ctx.send("Player tag not found.")

    if player is not None:
        stats_panel = get_stats_panel(player)
        globals.stats_message = await ctx.send(embed=stats_panel)

        globals.log = cr_client.get_player_battles(player_tag)
        globals.log_index = 0
        log_panel = get_log_panel(globals.log, globals.log_index)
        globals.log_message = await ctx.send(embed=log_panel)
        await globals.log_message.add_reaction('\u25c0')
        await globals.log_message.add_reaction('\u25b6')

def get_stats_panel(player):
    panel_title = f"{player['name']} | {player['tag']}"
    stats_panel = discord.Embed(title=panel_title, color=0xf8f8ff)

    personal_best = player['bestTrophies']
    stats_panel.add_field(name="Personal Best", value=personal_best,
                          inline=True)
    win_percent = f"{(player['wins'] / (player['wins'] + player['losses'])) * 100:.1f}%"
    stats_panel.add_field(name="Win Percent", value=win_percent,
                          inline=True)
    max_challenge_wins = player['challengeMaxWins']
    stats_panel.add_field(name="Max Challenge Wins", value=max_challenge_wins,
                          inline=True)

    return stats_panel

def get_log_panel(player_log, idx):
    player_log = [match for match in player_log
                  if match['gameMode']['name'] != "ClanWar_BoatBattle"]

    error_title = f"Match number {idx + 1} is out of range."
    try: match = player_log[idx]
    except: return discord.Embed(title=error_title, color=0xf8f8ff)

    team = match['team'][0]
    opponent = match['opponent'][0]

    game_mode = match['gameMode']['name']
    result = f"{team['crowns']} - {opponent['crowns']}"
    panel_title = f"Match Number {idx + 1} : {game_mode} | {result}"
    log_panel = discord.Embed(title=panel_title, color=0xf8f8ff)

    name_header = f"{team['name']} | {team['tag']}"
    field_header = name_header
    team_deck = ", ".join(card['name'] for card in team['cards'])
    log_panel.add_field(name=field_header, value=team_deck,
                        inline=True)

    name_header = f"{opponent['name']} | {opponent['tag']}"
    field_header = name_header
    opponent_deck = ", ".join(card['name'] for card in opponent['cards'])
    log_panel.add_field(name=field_header, value=opponent_deck,
                        inline=True)

    return log_panel

@bot.event
async def on_reaction_add(reaction, user):    
    if user.id != globals.bot_id:
        if reaction.message.id == globals.log_message.id:
            await globals.log_message.remove_reaction(reaction, user)

            globals.log_index += -1 if reaction.emoji == "\u25c0" else 0
            globals.log_index += 1 if reaction.emoji == "\u25b6" else 0
            globals.log_index = max(0, globals.log_index)

            log_panel = get_log_panel(globals.log, globals.log_index)
            await globals.log_message.edit(embed=log_panel)

bot.run(DISCORD_TOKEN)
