from os.path import basename, splitext
from discord.ext.commands import command, Context
import json
import subprocess
import asyncio

from . import util
from .command_info import commands
from .constants import Channel, Role, Section, Pattern

"""
    This file defines all Discord admin commands
"""

base_name = basename(__file__)
file_name = splitext(base_name)[0]
cog_commands = commands[file_name]


class Admin(object):

    def __init__(self, bot):
        self.bot = bot

    @command(**cog_commands['a'])
    async def a(self, ctx: Context, *, message: str):
        if not Role.get_admin_rank(ctx.message.author):
            return await self.bot.say("You are not an administrator.")
        if not Section.in_section(ctx.message.channel.id, Section.ADMINISTRATORS):
            return await self.bot.say("You must use this command in the _ADMINISTRATORS_ section.")

        out = json.dumps({
            "type": "asay",
            "sender": str(ctx.message.author.display_name),
            "message": message
        })

        await util.send_check(self.bot, ctx.message, out)

    @command(**cog_commands['admins'])
    async def admins(self, ctx: Context):
        channel = ctx.message.channel

        out = json.dumps({
            "type": "admins",
            "channel": str(channel.id)
        })

        await util.send_check(self.bot, ctx.message, out)

    @command(**cog_commands['prison'])
    async def prison(self, ctx: Context,  player: str, ptime: int, *, reason: str):
        if not Role.get_admin_rank(ctx.message.author):
            return await self.bot.say("You are not an administrator.")
        if ctx.message.channel.id != Channel.COMMANDS:
            return await self.bot.say("You must use this command in the #commands channel.")

        out = json.dumps({
            "type": "prison",
            "sender": str(ctx.message.author.display_name),
            "player": player,
            "ptime": ptime,
            "reason": reason
        })

        await util.send_check(self.bot, ctx.message, out)

    @command(**cog_commands['getlogs'])
    async def getlogs(self, ctx: Context, pattern: str):
        admin_level = Role.get_admin_rank(ctx.message.author)
        if admin_level is "Probie":
            return await self.bot.say("Probationary admins cannot use this feature.")
        if not admin_level:
            return await self.bot.say("You are not an administrator.")
        if ctx.message.channel.id != Channel.COMMANDS:
            return await self.bot.say("You must use this command in the #commands channel.")

        cmd = ['grep', '-m 3000', '-E', pattern, '/home/sarp/samp03z/server_log.txt']
        with open('./files/log.txt', 'wb') as logf:
            subprocess.Popen(cmd, stdout=logf, shell=False)  # shell=False to avoid shell injection

        await asyncio.sleep(2)
        await self.bot.upload('./files/log.txt')

    @command(**cog_commands['getbanreason'])
    async def getbanreason(self, ctx: Context, player: str):
        is_rp_name = Pattern.contains_pattern(Pattern.RP_NAME_PATTERN, player)
        if not Role.get_admin_rank(ctx.message.author):
            return await self.bot.say("You are not an administrator.")
        if ctx.message.channel.id != Channel.COMMANDS:
            return await self.bot.say("You must use this command in the #commands channel.")
        if not is_rp_name:
            return await self.bot.say("Please use the format: Firstname_Lastname.")

        out = json.dump({
            "type": "getbanreason",
            "name": player
        })

        await util.send_check(self.bot, ctx.message, out)

    @command(**cog_commands['kick'])
    async def kick(self, ctx: Context,  player: str, *, reason: str):
        if not Role.get_admin_rank(ctx.message.author):
            return await self.bot.say("You are not an administrator.")
        if not Section.in_section(ctx.message.channel.id, Section.ADMINISTRATORS + Section.HELPERS):
            return await self.bot.say("You must use this command in the _ADMINISTRATORS_ or _HELPERS_ section.")

        out = json.dumps({
            "type": "kick",
            "sender": str(ctx.message.author.display_name),
            "player": player,
            "reason": reason
        })

        await util.send_check(self.bot, ctx.message, out)

    @command(**cog_commands['w'])
    async def w(self, ctx: Context,  player: str, *, message: str):
        if not Role.get_admin_rank(ctx.message.author):
            return await self.bot.say("You are not an administrator.")
        if not Section.in_section(ctx.message.channel.id, Section.ADMINISTRATORS + Section.HELPERS):
            return await self.bot.say("You must use this command in the _ADMINISTRATORS_ or _HELPERS_ section.")

        out = json.dumps({
            "type": "w",
            "sender": str(ctx.message.author.display_name),
            "player": player,
            "message": message
        })

        await util.send_check(self.bot, ctx.message, out)

    """ Temporarily removing this
    @commands.command(pass_context=True)
    async def stats(self, ctx, *, user : str):
        out = json.dumps({
            "type":"stats",
            "user":user
        })
        await util.send_check(self.bot, ctx.message, out)
    """


# this is important, this basically creates a new object of Admin
def setup(bot):
    bot.add_cog(Admin(bot))
