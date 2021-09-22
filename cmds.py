
import discord, time, asyncio, aiohttp, json
from datetime import datetime
from discord.ext import commands


class cmds(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.color = 0x303136

    # discord invitation template
    self.server_invite1 = ["discord.gg/", "discordapp.com/invite/"]
    # external sites that can be used to invite
    self.server_invite2 = ["discord.me/servers", "discordservers.com/", "disboard.org/", "disc.gg/", "top.gg/servers"]

    self.config_file = open('config.json')
    self.bot_data = json.load(self.config_file)

    # sec
    self.discord_invite_warn = [] # users who sent external invitations [this is a cooldown]
    self.muted_users = []    # users who have been silenced for some reason [this is a cooldown]
    
    # flood sec
    self.floodSafetyList = [[], [], [], []] # list to control the cooldown individually for each message sent



  # interaction with the config.json file
  async def loadJsonFile(self):
    config_file = open('config.json')
    self.bot_data = json.load(config_file)
  # loadJsonFile EMD

  async def updateJsonFile(self, jsonKey, keyValue):
    with open("config.json", "r") as jsonFile:
      bot_data = json.load(jsonFile)

    bot_data[jsonKey] = keyValue

    with open("config.json", "w") as jsonFile:
      json.dump(bot_data, jsonFile)
  # updateJsonFile END


  # data check
  def verifyInteger(self, numberToVerify):
    try: int(numberToVerify); return True
    except: return False
  # verifyInteger END
  
  def isStaff(self, message):
    staff_role = message.guild.get_role(self.bot_data['roles']['staff'])

    return staff_role in message.author.roles
  # isStaff END
  


  # interaction with channels
  async def deleteMessage(self, messageToDelete):
    try: await messageToDelete.delete()
    except: pass
  # deleteMessage END

  async def sendMessage(self, messageContent, channelSend, delAfter = None, isEmbed = 1):
    try: 
      if isEmbed:
        return await channelSend.send(embed = messageContent, delete_after = delAfter)
      else:
        return await channelSend.send(messageContent, delete_after = delAfter)

    except discord.errors.NotFound:
      pass
  # sendMessage END



  # applies a cooldown to a given member as per the arguments provided 
  async def applyCooldown(self, member_, list_, time_):
    list_.append(member_), await asyncio.sleep(time_), list_.remove(member_)
  # applyCooldown END


  # reports automatic punishment actions in a predetermined channel
  async def logBotAction(self, punishedUser, moreInfo, channel):
    bot_log = self.client.get_channel(self.bot_data['channels']['bot_log'])
    separar = moreInfo.split("|", 1)

    embed = discord.Embed(color=self.color, description=f'**punishment:** {separar[0]}\n**reason:** {separar[1]}\n**channel**: {channel.mention}')
    embed.set_author(name=f'{punishedUser} was punished', icon_url=punishedUser.avatar_url)
    embed.timestamp = datetime.now()
    log_message = await self.sendMessage(embed, bot_log)
    return [log_message, embed]
  # logBotAction END


  async def muteUser(self, message, log_message, embed, timeMuted = 300):
    muted_role = message.author.guild.get_role(self.bot_data['roles']['muted'])
    await self.loadJsonFile()
    muted_users_data = self.bot_data["muted_users_data"]

    await message.author.add_roles(muted_role)
    self.muted_users.append(message.author.id)

    muted_users_data.append(message.author.id)
    await self.updateJsonFile("muted_users_data", muted_users_data if self.bot_data["muted_users_data"] else [message.author.id])

    await asyncio.sleep(timeMuted)

    await message.author.remove_roles(muted_role)
    self.muted_users.remove(message.author.id)

    await self.loadJsonFile()
    muted_users_data = self.bot_data["muted_users_data"]
    try:
      muted_users_data.remove(message.author.id)
      await self.updateJsonFile("muted_users_data", muted_users_data)

      embed.insert_field_at(0, name='status', value='the punishment time is over')

      print(log_message.id)
      await log_message.edit(embed=embed)
    except ValueError:
      pass
  # muteUser END

  
  # checks if the message contains an invitation to an external server
  async def discordInviteVerify(self, message):
    try:
      for invite_type in self.server_invite1:
        if invite_type in message.content:
          invite_server = message.content.split(invite_type)[1].split(" ")[0]

          invite = await self.client.fetch_invite(invite_server)

          if not invite.guild.id == message.guild.id:
            await self.deleteMessage(message)

            if message.author.id in self.discord_invite_warn:
              embed = discord.Embed(color=self.color, description="you will be demuted automatically after the specified time. Otherwise, please contact the staff\nwe apologize for that. it's a way to keep our community organized... we hope you understand")
              embed.set_author(name=f'{message.author.name}, you have been silenced for 5 minutes', icon_url=message.author.avatar_url)
              await self.sendMessage(embed, message.author)

              log_message, log_message_embed = await self.logBotAction(message.author, 'muted for 5 minutes|sent external server invitation without staff permission', message.channel)

              await self.muteUser(message, log_message, log_message_embed) 

            else:
              embed = discord.Embed(color=self.color, description="please do not share other servers without permission from staff\nI'm programmed to silence you if I do this again (sorry)")
              embed.set_author(name=f'{message.author.name}, your message is linked to a server invitation', icon_url=message.author.avatar_url)
              await self.sendMessage(embed, message.author)

              await self.applyCooldown(message.author.id, self.discord_invite_warn, 300)
              return

      for invite_type in self.server_invite2: 
        if invite_type in message.content:
          invite_server = message.content.split(invite_type)[1].split(" ")[0]

          if invite_server:
            print('NAO PODE')
            await self.deleteMessage(message)
            
            if message.author.id in self.discord_invite_warn:
              embed = discord.Embed(color=self.color, description="you will be demuted automatically after the specified time. Otherwise, please contact the staff\nwe apologize for that. it's a way to keep our community organized... we hope you understand")
              embed.set_author(name=f'{message.author.name}, you have been silenced for 5 minutes', icon_url=message.author.avatar_url)
              await self.sendMessage(embed, message.author)

              log_message, log_message_embed = await self.logBotAction(message.author, 'muted for 5 minutes|sent external server invitation without staff permission', message.channel)

              await self.muteUser(message, log_message, log_message_embed)

            else:
              embed = discord.Embed(color=self.color, description="please do not share other servers without permission from staff\nI'm programmed to silence you if I do this again (sorry)")
              embed.set_author(name=f'{message.author.name}, your message is linked to a server invitation', icon_url=message.author.avatar_url)
              await self.sendMessage(embed, message.author)
              await self.applyCooldown(message.author.id, self.discord_invite_warn, 300)
              return

    except IndexError:
      print('index error')
    except discord.errors.NotFound:
      print('not found')
  # discordInviteVerify END


  # main checks for on_message event and derivatives
  async def onMessageCheck(self, message):
    # ignore private messages and messages from bots
    if "Direct Message" in str(message.channel) or message.author.bot:
      return False

    # check if the user is a staff member (the security functions will not apply to staff members)
    elif self.isStaff(message):
      return False

    else:
      return True
  # onMessageCheck END


  # ####
  # events
  # ####

  @commands.Cog.listener()
  async def on_member_join(self, member):
    """if the member was silenced and leaves the server, he will lose the Muted role.
       this event will return the Muted role if it returns to the server """

    if member.id in self.muted_users:
      muted_role = member.guild.get_role(self.bot_data['roles']['muted'])
      await member.add_roles(muted_role)


  @commands.Cog.listener()
  async def on_message_edit(self, before, after):
    """checks if an external server invitation has been inserted into an edited message"""

    if not await self.onMessageCheck(after):
      return
    await self.discordInviteVerify(after)


  @commands.Cog.listener()
  async def on_message(self, message):
    if not await self.onMessageCheck(message):
      return

    await self.discordInviteVerify(message)

    # structure responsible for monitoring each message sent from each member
    # when analyzing and noting that the behavior is suspicious, automatic moderation actions will be performed

    mauthorid = message.author.id
    flist1 = self.floodSafetyList[0]
    flist2 = self.floodSafetyList[1]
    flist3 = self.floodSafetyList[2]
    flist4 = self.floodSafetyList[3]

    
    if not mauthorid in flist1:
      await self.applyCooldown(mauthorid, flist1, 3) # <<< you can increase or decrease the seconds according to the desired security level
                                                     # if you increase the seconds, the user will stay longer in the list
                                                     # so the chances of a user going to the next safelist are higher

    elif not mauthorid in flist2:
      await self.applyCooldown(mauthorid, flist2, 2) # <<<

    elif not mauthorid in flist3:
      await self.applyCooldown(mauthorid, flist3, 1) # <<<

    elif not mauthorid in flist4:
      muted_role = message.author.guild.get_role(self.bot_data['roles']['muted'])
      await message.author.add_roles(muted_role)
      
      embed = discord.Embed(color=self.color)
      embed.set_author(name=f'{message.author.name}, please do not send messages too fast', icon_url=self.client.user.avatar_url)
      await self.sendMessage(embed, message.channel, 8)

      await asyncio.sleep(3)
      await message.author.remove_roles(muted_role)

      await self.applyCooldown(mauthorid, flist4, 20) # <<<
    else:
      await self.deleteMessage(message)

      embed = discord.Embed(color=self.color, description="you will be demuted automatically after the specified time. Otherwise, please contact the staff\nwe apologize for that. it's a way to keep our community organized... we hope you understand")
      embed.set_author(name=f'{message.author.name}, you have been silenced for 5 minutes for sending messages too fast', icon_url=message.author.avatar_url)
      await self.sendMessage(embed, message.author)

      log_message, log_message_embed = await self.logBotAction(message.author, 'muted for 5 minutes|flood', message.channel)

      await self.muteUser(message, log_message, log_message_embed)


  @commands.Cog.listener()
  async def on_guild_channel_create(self, channel):
    """automatically configure permissions when a channel is created"""

    muted_role = channel.guild.get_role(self.bot_data['roles']['muted'])
    await channel.set_permissions(muted_role, send_messages=False)

    embed = discord.Embed(color=self.color)
    embed.set_author(name=f'the "muted" role has been properly configured', icon_url=self.client.user.avatar_url)
    await self.sendMessage(embed, channel)


  @commands.command(name='info')
  @commands.has_permissions(manage_messages=True)
  @commands.guild_only()
  async def info_(self, ctx):
    """returns client latency, discord websocket latency, and bot prefix"""

    timep = time.time()
    embed = discord.Embed(title='🌐 (｡•́︿•̀｡)', color=self.color)
    editembed = await self.sendMessage(embed, ctx)

    ping = (time.time() - timep)
    embed = discord.Embed(color=self.color, description=f'• **Client latency:** {ping:.2f} sec\n• **Discord WebSocket:** {self.client.latency:.2f} sec\n• **Prefix:** {self.client.command_prefix}')
    embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
    await editembed.edit(embed=embed)

    await self.deleteMessage(ctx)


  @commands.command(name='lock')
  @commands.has_permissions(manage_messages=True)
  @commands.guild_only()
  async def lock_channel_(self, ctx):
    """lock the channel where the command was executed"""

    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)

    embed = discord.Embed(color=self.color)

    if overwrite.send_messages == False:
      await ctx.channel.set_permissions(ctx.channel.guild.default_role, send_messages=None)
      embed.description = 'Now everyone can talk again'
      embed.set_author(name='The channel has been unlocked', icon_url=self.client.user.avatar_url)
    else:
      await ctx.channel.set_permissions(ctx.channel.guild.default_role, send_messages=False)
      embed.description = "Don't worry it will only be for a few minutes"
      embed.set_author(name='The channel has been locked', icon_url=self.client.user.avatar_url)
    
    await self.sendMessage(embed, ctx)


  @commands.command(name='purge', aliases=['pur'], usage=f'20 <@427957969582292996>\n**arguments:** [integer number] [user mention (optional)]|Deletes a certain number of messages. Mention a user to delete only their messages')
  @commands.has_permissions(manage_messages=True)
  @commands.guild_only()
  async def purge_messages_(self, ctx, arg, member: discord.Member=None):
    """purges a specified number of messages. It is possible to pass a mention as an argument so that only the messages of the mentioned user are deleted"""

    if int(arg) < 5 or int(arg) > 100:
      embed = discord.Embed(color=self.color)
      embed.set_author(name=f'{ctx.author.name}, please enter a number between 5 and 100', icon_url=ctx.author.avatar_url)
      return await self.sendMessage(embed, ctx)

    if not self.verifyInteger(arg):
      embed = discord.Embed(color=self.color)
      embed.set_author(name=f'{ctx.author.name}, you must enter only numbers as argument', icon_url=ctx.author.avatar_url)
      return await self.sendMessage(embed, ctx)


    embed = discord.Embed(color=self.color, description='react with ✅ to confirm')
    embed.set_author(name=f'{ctx.author.name}, do you really want to delete {arg} messages?', icon_url=ctx.author.avatar_url)
    wait_for_mesage = await self.sendMessage(embed, ctx)

    await wait_for_mesage.add_reaction('✅')
    await wait_for_mesage.add_reaction('❌')


    def wait_for_reaction_check(reaction, user):
      return user.id == ctx.author.id and reaction.message.id == wait_for_mesage.id and not user.bot

    try:
      reaction, user = await self.client.wait_for('reaction_add', timeout=50, check=wait_for_reaction_check)
    except:
      await self.deleteMessage(wait_for_mesage)
    else:
      if reaction.emoji == '✅':
        await self.deleteMessage(ctx.message)
        await self.deleteMessage(wait_for_mesage)

        if member:
          user_messages = []
          async for message in ctx.channel.history():
            if len(user_messages) == int(arg):
              break

            if message.author.id == member.id:
              user_messages.append(message)
          try:
            await ctx.channel.delete_messages(user_messages)
          except discord.NotFound:
            embed = discord.Embed(color=self.color, description='You tried to delete messages that have already been deleted')
            embed.set_author(name=f'{ctx.author.name}, please use the command again', icon_url=ctx.author.avatar_url)
            await self.sendMessage(embed, ctx)
            
        else:
          await ctx.channel.purge(limit=int(arg), check=lambda msg: not msg.pinned)

      await self.deleteMessage(wait_for_mesage)




  @commands.command(name='prefix', usage=f'!\n**arguments:** [prefix]|Change the bot prefix. Enter "reset" as argument to reset default prefix')
  @commands.has_permissions(manage_messages=True)
  @commands.guild_only()
  async def changePrefix_(self, ctx, arg):
    """change the bot prefix"""

    if str(arg) == 'reset'.lower():
      arg = '!'

    await self.updateJsonFile("prefix", str(arg))
    self.client.command_prefix = str(arg)
    await ctx.message.add_reaction('✅')


def setup(client):
  client.add_cog(cmds(client))