import discord, traceback, json
from datetime import datetime
from discord.ext import commands

  
f = open('config.json')
bot_data = json.load(f)

extensions = ['cmds', 'events']


intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.reactions = True
intents.members = True 

client = commands.Bot(
  command_prefix = bot_data["prefix"],
  case_insensitive = True,
  intents = intents
)

@client.event
async def on_ready():
  print(client.user.name, datetime.now().strftime('%H:%M'))
  print(client.user.id)
  print('=' * 18)

  # unmute members that were not unmuted due to bot failures
  muted_users_data = bot_data["muted_users_data"]
  my_guild = client.get_guild(bot_data["guild"])
  muted_role = my_guild.get_role(bot_data['roles']['muted'])

  for muted_user in muted_users_data:
    member = my_guild.get_member(muted_user)
    await member.remove_roles(muted_role)

  bot_data['muted_users_data'] = []

  with open("config.json", "w") as jsonFile:
    json.dump(bot_data, jsonFile)



if __name__ == '__main__':
  for extension in extensions:
    try:
      client.load_extension(extension)
    except Exception as error:
      print(f'[{extension}] error. [{error}]\n\n', traceback.print_exc())
  client.run(bot_data["token"])