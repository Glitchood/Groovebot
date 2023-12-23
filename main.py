#import required dependencies
import os
from datetime import datetime as dt
from datetime import timezone as tz
from termcolor import colored

import discord
import inflect
import spotipy
from discord import app_commands
from discord.ext import commands
from spotipy.oauth2 import SpotifyClientCredentials
from reactionmenu import ViewMenu, ViewButton

import database
import keep_alive
import spotipy_integ


bot_token = os.environ['DISCORD_BOT_SECRET']
intents = discord.Intents.default()
intents.members = True
p = inflect.engine()

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())



# client.remove_command("help")

# USAGE OF cmd() 🔽
# username = interaction.user.name
# params = f'param1[{param1}]'
# await cmd(interaction.command.name,username,params)

async def cmd(cmd, username, params=None):
  date_time = dt.now()
  date_time = date_time.replace(microsecond=0)
  cmd = cmd.upper()
  timestamp_text = colored(f'{date_time}', 'grey', attrs=['bold'])
  cmd_text = colored(f'{cmd}', 'light_blue', attrs=['bold'])
  user_text = colored(f'{username}', 'magenta')
  params_text = colored(f'{params}', 'green')
  print(f'\n{timestamp_text} {cmd_text}   {user_text}   {params_text}')

# USAGE OF cmdlink() 🔽
# (DO AT BOTTOM OF COMMAND)
# interaction_link = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel_id}/{interaction.id}"
# await cmdlink(interaction_link)

async def cmdlink(link):
  link_text = colored(f'{link}', 'light_cyan', attrs=['underline'])
  print(f'{link_text}')


@client.event
async def on_ready():
  print("GrooveBot is online!")
  print("-----------------------------")
  try:
    # 1155003686959980647 --> Development Server
    # 1178193307541712906 --> GrooveBot Beta Testers
    guild = discord.Object(id=1178193307541712906)
    client.tree.copy_global_to(guild=guild)
    synced = await client.tree.sync(guild=guild)
    print(f"Synced {len(synced)} command(s)")
    print("-----------------------------")
  except Exception as e:
    print(e)


async def gen_embed(interaction,top_songs,embed, num_start: int, num_fields: int):
  num_start -= 1
  rank = num_start
  embed.clear_fields()
  num_end = num_start + num_fields
  print(f'num_end = {num_end}')
  for i in range (num_start,num_end):
    top_artistname = top_songs[i]['artist']
    top_trackname = top_songs[i]['track']
    top_shares = top_songs[i]['shares']
    top_popularity = 10
    rank += 1
    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    results = spotify.search(q="track:" + top_trackname + " artist:" +
                             top_artistname,
                             type='track',
                             limit=1)
    items = results['tracks']['items']
    count = 0
    for track in items:
      count += 1
      top_popularity = track['popularity']

    top_embedaddfield(embed, rank, top_artistname, top_trackname,
                      top_popularity, top_shares)
    
    

@client.tree.command(name='showtop', description='Show the top shared songs in the server!')
@app_commands.describe(pages="Number of pages you want to generate. (Default = 2)",rows="Number of song entries shown per page. (Default = 5")
async def showtop(interaction: discord.Interaction, pages: int=2,rows: int=5):
  # if it's too long
  top_songs = database.get_top_songs("song_list.csv")
  selected_total_entries = pages*rows
  if selected_total_entries > len(top_songs):
    response = f'**ERROR:** You chose to list `{selected_total_entries}` entries, but there are only `{len(top_songs)}` entries! Try a lower number.'

    await interaction.response.send_message(response,ephemeral=True)
    return
  username = interaction.user.name
  displayname = interaction.user.display_name
  params = f'pages[{pages}], rows[{rows}]'
  await cmd(interaction.command.name,username,params)
  await interaction.response.defer()
    
  top_embed_template = discord.Embed(title=f"Top Songs in **{interaction.guild}**",
                        colour=0x00b0f4,
                        timestamp=dt.now())
  top_embed_template.set_author(
      name="GrooveBot",
      url="https://gg.gg/groovebot",
      icon_url=
      "https://cdn-0.emojis.wiki/emoji-pics/microsoft/musical-keyboard-microsoft.png"
  )

  menu = ViewMenu(interaction, menu_type=ViewMenu.TypeEmbed, wrap_in_codeblock='asci')
  num = 0
  start_field = 1
  i = 1
  for i in range (0,pages):
    print(i)
    globals()[f'embed{i}'] = 0
    print(f"0 == {globals()[f'embed{i}']}")
    globals()[f'embed{i}'] = discord.Embed(title=f"Top Songs in **{interaction.guild}**",
                          colour=0x00b0f4,
                          timestamp=dt.now())
    globals()[f'embed{i}'].set_author(
        name="GrooveBot",
        url="https://gg.gg/groovebot",
        icon_url=
        "https://cdn-0.emojis.wiki/emoji-pics/microsoft/musical-keyboard-microsoft.png"
    )
    globals()[f'embed{i}'].set_thumbnail(
        url=
        "https://cdn-0.emojis.wiki/emoji-pics/microsoft/input-numbers-microsoft.png"
    )

    globals()[f'embed{i}'].set_footer(
        text="Generated by GrooveBot",
        icon_url="https://cdn-0.emojis.wiki/emoji-pics/microsoft/counterclockwise-arrows-button-microsoft.png")
    print(f"embeds == {globals()[f'embed{i}']}")
    await gen_embed(interaction,top_songs,globals()[f'embed{i}'],start_field,rows)
    menu.add_page(globals()[f'embed{i}'])
    num += 1
    start_field = 1+num*rows
    print(f"embeds == {globals()[f'embed{i}']}")

  msg_followup = ViewButton.Followup(f'**`/showtop`** shows the top songs in the server ordered by how many times they were shared. There are `{len(top_songs)}` total songs that have been shared. You selected `{pages}` pages and `{rows}` rows, `{pages*rows}` total entries!', ephemeral=True)
  menu.add_button(ViewButton(style=discord.ButtonStyle.grey, emoji='ℹ️', custom_id=ViewButton.ID_SEND_MESSAGE, followup=msg_followup))

  menu.add_button(ViewButton(style=discord.ButtonStyle.danger, emoji='✖️', custom_id=ViewButton.ID_END_SESSION, followup=msg_followup))
  
  menu.add_button(ViewButton(style=discord.ButtonStyle.blurple, emoji='◀️', custom_id=ViewButton.ID_PREVIOUS_PAGE))
  
  menu.add_button(ViewButton(style=discord.ButtonStyle.blurple, emoji='▶️', custom_id=ViewButton.ID_NEXT_PAGE))
  
  
  await menu.start()
  
  interaction_link = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel_id}/{interaction.id}"
  await cmdlink(interaction_link)


@client.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
  displayname = interaction.user.display_name
  username = interaction.user.name
  await cmd(interaction.command.name,username)
  await interaction.response.send_message(f"Pong, {interaction.user.mention}!")
  
  # Get the link to the interaction
  interaction_link = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel_id}/{interaction.id}"
  await cmdlink(interaction_link)

# ADD EXTRA INFO PER COMMAND USING HELP GROUP
# @client.command(aliases=['commands'])
# async def help(ctx):
#   helpEmbed = discord.Embed(title = "Commands List", color = discord.Color.blue())
#   helpEmbed.add_field(name = "Moderation", value = "`clear`, `help`")
#   helpEmbed.add_field(name = "Fun", value = "`ping`")
#   helpEmbed.add_field(name = "Music", value = "`showtop`, `share`")

#   await ctx.send(embed = helpEmbed)


@client.tree.command(name="say")
@app_commands.describe(thing_to_say="What the bot should say")
async def say(interaction: discord.Interaction, thing_to_say: str = 'hi'):
  username = interaction.user.name
  params = f'thing_to_say[{thing_to_say}]'
  await cmd(interaction.command.name,username,params)
  await interaction.response.send_message(
      f"{username} said '{thing_to_say}'")
  # Get the link to the interaction
  interaction_link = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel_id}/{interaction.id}"
  await cmdlink(interaction_link)


def top_embedaddfield(embed, rank, artist, track, popularity, shares): 
  embed.add_field(
      name=f"**{rank}.   __{track}__    —    `{artist}`**",
      value=f"```ansi\n📈 – \033[37;49;1m Popularity:\033[0m {popularity}%\n🔗 – \033[37;49;1m Shares:\033[0m {shares}\n```",
      inline=False)

async def embedFormat(interaction, artistName, trackName, albumName,releaseDate, popularity, duration, URL, image, shares,followup):

  # Convert milliseconds to seconds
  dur_secs = duration // 1000
  # Calculate minutes and seconds
  mins = dur_secs // 60
  secs = dur_secs % 60
  # Format the output as "min:sec"
  duration = f"{mins}:{secs:02d}"
  
  displayname = interaction.user.display_name
  avatar = interaction.user.display_avatar
  embed = discord.Embed(title=f"_{trackName}_   —    **{artistName}**",
                        url=f"{URL}",
                        colour=0x00b0f4,
                        timestamp=dt.now())

  embed.set_author(
      name=displayname,
      icon_url=avatar
  )

  embed.add_field(
      name="Song Information:",
      value=
      f"```ansi\n🎹 – \033[37;49;1m Artist:\033[0m {artistName}\n📀 – \033[37;49;1m Album:\033[0m {albumName}\n⏱️ – \033[37;49;1m Duration:\033[0m {duration}\n📆 – \033[37;49;1m Released:\033[0m {releaseDate}\n📈 – \033[37;49;1m Popularity:\033[0m {popularity}%\n```",
      inline=True)
  embed.add_field(name="Server Statistics:",
                  value=f"```ansi\n🔗 – \033[37;49;1m Shares: \033[0m {shares}\n```",
                  inline=True)

  embed.set_thumbnail(url=f"{image}")

  embed.set_footer(
      text="Generated by GrooveBot",
      icon_url=
      "https://cdn-0.emojis.wiki/emoji-pics/microsoft/counterclockwise-arrows-button-microsoft.png"
  )
  if not followup:
    await interaction.response.send_message(embed=embed)
  else:
    await interaction.followup.send(embed=embed)


@client.tree.command(name='share', description='Share a song with someone!')
@app_commands.describe(artist_name="Artist for track. If unknown, put '$'",
                       track_name="Artist for track. If unknown, put '$'")
async def share(interaction: discord.Interaction, artist_name: str,track_name: str):
  username = interaction.user.name
  displayname = interaction.user.display_name
  params = f'artist_name[{artist_name}], track_name[{track_name}]'
  await cmd(interaction.command.name,username,params)
  view = ButtonView()

  print(f"\033[37;49;1m Artist: [{artist_name}] -- Track: [{track_name}]")
  # ------------------------------------------------------------------
  if artist_name == '$':
    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    results = spotify.search(q="track:" + track_name, type='track', limit=5)
    items = results['tracks']['items']
    tracks_found = []
    artists_found = []
    rank_found = []
    for count in range(5):
      tracks_found.append(items[count]['name'])
      artists_found.append(items[count]['artists'][0]['name'])
    print()
    print(tracks_found)
    print()
    print(artists_found)
    print()
    print(rank_found)
    print()
    response = f"## Top 5 song results for your query: `{track_name}` \n\n"
    for count in range(5):
      rank = p.number_to_words(count + 1)
      entry_track_name = tracks_found[count]
      entry_artist_name = artists_found[count]
      results_of_item = spotify.search(q="track:" + entry_track_name +" artist:" + entry_artist_name,type='track',limit=1)
      items = results_of_item['tracks']['items']
      for track in items:
        response += f"## :{rank}: \n```🎵 – Song: {track['name']}\n🎹 – Artist: {track['artists'][0]['name']}\n📀 – Album: {track['album']['name']}\n⏱️ – Duration (ms): {track['duration_ms']}\n📆 – Released: {track['album']['release_date']}\n📈 – Popularity: {track['popularity']}%\n``` \n"
    print(response)
    await interaction.response.send_message(response, ephemeral=True)
    await interaction.followup.send(view=view, ephemeral=True)
    await view.wait()
    selected_track_data = results['tracks']['items'][view.value]
    print(f"\n\n SELECTED_TRACK={view.value}")

    selected_track_name = selected_track_data['name']
    selected_artist_name = selected_track_data['artists'][0]['name']

    print(f"\n\n TRACK={selected_track_name}\n\n ARTIST={selected_artist_name}")

    query_artistName, query_trackName, query_albumName, query_releaseDate, query_popularity, query_duration, query_trackURL, query_albumImage, query_id = spotipy_integ.shareTrack(selected_artist_name, selected_track_name)

    share_count = database.add_song_to_database("song_list.csv",query_artistName,query_trackName, query_id)
    followup = True
    await embedFormat(interaction, query_artistName, query_trackName,query_albumName, query_releaseDate, query_popularity,query_duration, query_trackURL, query_albumImage,share_count, followup)

    await interaction.followup.send(f"[⠀]({query_trackURL})")


# ------------------------------------------------------------------
  elif track_name == '$':
    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    results = spotify.search(q="artist:" + artist_name, type='track', limit=5)
    items = results['tracks']['items']
    tracks_found = []
    artists_found = []
    rank_found = []
    for count in range(5):
      tracks_found.append(items[count]['name'])
      artists_found.append(items[count]['artists'][0]['name'])
    print()
    print(tracks_found)
    print()
    print(artists_found)
    print()
    print(rank_found)
    print()
    response = f"## Top 5 song results for your query: `{artist_name}` \n\n"
    for count in range(5):
      rank = p.number_to_words(count + 1)
      entry_track_name = tracks_found[count]
      entry_artist_name = artists_found[count]
      results_of_item = spotify.search(q="track:" + entry_track_name +
                                       " artist:" + entry_artist_name,
                                       type='track',
                                       limit=1)
      items = results_of_item['tracks']['items']
      for track in items:
        response += f"## :{rank}: \n```ansi🎵 – Song: {track['name']}\n🎹 – \033[37;49;1m Artist: {track['artists'][0]['name']}\n📀 – \033[37;49;1m Album: {track['album']['name']}\n⏱️ – Duration (ms): {track['duration_ms']}\n📆 – \033[37;49;1m Released: {track['album']['release_date']}\n📈 – \033[37;49;1m Popularity: {track['popularity']}%\n``` \n"
    print(response)
    await interaction.response.send_message(response, ephemeral=True)
    await interaction.followup.send(view=view, ephemeral=True)
    await view.wait()
    selected_track_data = results['tracks']['items'][view.value]
    print(f"\n\n SELECTED_TRACK={view.value}")

    selected_track_name = selected_track_data['name']
    selected_artist_name = selected_track_data['artists'][0]['name']

    print(
        f"\n\n TRACK={selected_track_name}\n\n ARTIST={selected_artist_name}")

    query_artistName, query_trackName, query_albumName, query_releaseDate, query_popularity, query_duration, query_trackURL, query_albumImage, query_id = spotipy_integ.shareTrack(
        selected_artist_name, selected_track_name)

    share_count = database.add_song_to_database("song_list.csv",query_artistName,query_trackName,query_id)
    followup = True
    await embedFormat(interaction, query_artistName, query_trackName,query_albumName, query_releaseDate, query_popularity,query_duration, query_trackURL, query_albumImage,share_count, followup)

    await interaction.followup.send(f"[⠀]({query_trackURL})")

  else:
    query_artistName, query_trackName, query_albumName, query_releaseDate, query_popularity, query_duration, query_trackURL, query_albumImage, query_id = spotipy_integ.shareTrack(artist_name, track_name)
    
    share_count = database.add_song_to_database("song_list.csv",query_artistName,query_trackName, query_id)
    followup = False
    await embedFormat(interaction, query_artistName, query_trackName,query_albumName, query_releaseDate, query_popularity,query_duration, query_trackURL, query_albumImage,share_count, followup)

    await interaction.followup.send(f"[⠀]({query_trackURL})")
    
  # Get the link to the interaction
  interaction_link = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel_id}/{interaction.id}"
  await cmdlink(interaction_link)


class ButtonView(discord.ui.View):

  def __init__(self):
    super().__init__()
    self.value = None

  @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="1️⃣")
  async def select1(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
    self.value = 0
    await interaction.response.send_message(
        f"You chose song option {self.value+1}!", ephemeral=True)
    self.stop()

  @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="2️⃣")
  async def select2(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
    self.value = 1
    await interaction.response.send_message(
        f"You chose song option {self.value+1}!", ephemeral=True)
    self.stop()

  @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="3️⃣")
  async def select3(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
    self.value = 2
    await interaction.response.send_message(
        f"You chose song option {self.value+1}!", ephemeral=True)
    self.stop()

  @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="4️⃣")
  async def select4(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
    self.value = 3
    await interaction.response.send_message(
        f"You chose song option {self.value+1}!", ephemeral=True)
    self.stop()

  @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="5️⃣")
  async def select5(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
    self.value = 4
    await interaction.response.send_message(
        f"You chose song option {self.value+1}!", ephemeral=True)
    self.stop()

  @discord.ui.button(label="Cancel Command",
                     style=discord.ButtonStyle.danger,
                     emoji="✖️")
  async def cancel(self, interaction: discord.Interaction,
                   button: discord.ui.Button):
    await interaction.response.send_message(
        f"Cancelled, {interaction.user.mention}!", ephemeral=True)
    self.stop()


keep_alive.keep_alive()
client.run(bot_token, root_logger=True)
