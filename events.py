 import discord, json, asyncio, traceback
from discord.ext import commands
from discord.ext.commands import errors as cmd


class _events(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.color = 0x303136

  @commands.Cog.listener()
  async def on_command_error(self, ctx, error):

    if isinstance(error, commands.CommandNotFound):
      pass

    elif isinstance(error, commands.CheckFailure):
      pass

    elif isinstance(error, commands.MissingPermissions):
      await ctx.message.add_reaction('❌')

    elif isinstance(error, commands.NoPrivateMessage):
      pass

    elif isinstance(error, (cmd.BadArgument, cmd.BadUnionArgument, cmd.MissingRequiredArgument)):
      if ctx.command.usage:
        separar = ctx.command.usage.split("|", 1)
        embed = discord.Embed(color=self.color, description=f'**Description:** {separar[1]}\n**Example:** {self.client.command_prefix} {ctx.command.name} {separar[0]}')
        embed.set_author(name=f'{ctx.author.name}, how to use the {ctx.command.name} command:', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
      else:
        pass


def setup(client):
  client.add_cog(_events(client))