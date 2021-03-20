"""
MIT License

Copyright (c) 2020 XroixHD

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import datetime
import time
import typing

import discord
from discord.ext import commands

from src import storage


class RenameCommand(commands.Cog):
    """ The rename cog / module / command
        Ever wanted to rename you entire Discord Server?
    """

    def __init__(self, client):
        """ Initialize
        :param client: the client
        """
        super().__init__()

        self.client = client
        self.storage = client.storage

        self.cached_roles = {}

    def cacheRoles(self, guild: discord.Guild, *, override=False):
        """ Caches role objects for guild
        :param guild: the guild
        :param override: prevent caching if already set
        """
        if guild.id in self.cached_roles and not override:
            return

        self.cached_roles.update({
            guild.id: {
                "female": discord.utils.get(guild.roles,
                                            name=self.client.female_role) if self.client.female_role != "" else "",

                "male": discord.utils.get(guild.roles,
                                          name=self.client.male_role) if self.client.male_role != "" else "",

                "ignore": discord.utils.get(guild.roles,
                                            name=self.client.male_role) if self.client.male_role != "" else ""
            }
        })

    async def renameMember(self, member: discord.Member, bypass_ignore: bool) -> str:
        """ Rename a member randomly
        :param member: the person to rename
        :param bypass_ignore: if to bypass ignore role
        :returns: kinda a debug string
        """
        self.cacheRoles(member.guild, override=False)
        roles = self.cached_roles[member.guild.id]

        try:
            # If it is ignored
            if not bypass_ignore and roles["ignore"] in member.roles:
                txt = f"> [?] ignored {member.name}\n"

            # Or female
            elif roles["female"] == "" or roles["female"] in member.roles:
                name = await self.storage.popNames("f")

                txt = f"> [w] {member.name} => {name}\n"

                await member.edit(nick=name)

            # Or male
            elif roles["male"] == "" or roles["male"] in member.roles:
                name = await self.storage.popNames("m")

                txt = f"> [m] {member.name} => {name}\n"

                await member.edit(nick=name)

            # Not specified
            else:
                txt = f"> [?] ignored {member.name}; unspecified Gender!\n"

        except Exception as e:
            txt = f"> [!] ignored {member.name}; error: {e}\n"
            
        return txt

    @commands.command()
    async def test(self, ctx: commands.Context):
        """ Test the mechanism
        :param commands.Context ctx: the context
        """
        _old = len(self.storage.names_male)
        for i, member in enumerate(ctx.guild.members):
            print(i, member, await self.storage.popNames("m"))

        print(self.storage.names_male)
        self.storage.cacheNames()
        await ctx.send(f"List length changed from {_old} to {len(self.storage.names_male)}")

    @commands.command()
    @commands.is_owner()
    @commands.has_any_role("Menschen oberster Klasse", "Edelmann", "Eine Farbe über dir")
    async def rename(self, ctx: commands.Context, victim: typing.Union[discord.Role, discord.Member, str],
                     bypass_ignore: typing.Optional[bool] = False):
        # Only allow 'all' as a string for `victim`
        if isinstance(victim, str) and victim != "all":
            raise commands.BadArgument(f"> Invalid Argument `{victim}`!")

        with ctx.typing():

            # For Profiling
            START_TIME = time.time()

            if isinstance(victim, str) and victim == "all":
                # Vars
                iterable = ctx.guild.members
                confirmation_desc = "All members will be renamed randomly, are you sure?"

            elif isinstance(victim, discord.Member):
                iterable = [victim]
                confirmation_desc = None

            elif isinstance(victim, discord.Role):
                iterable = victim.members
                confirmation_desc = f"All members of `{victim.name}` will be renamed randomly, are you sure?"

            else:
                raise Exception("Fatal Exception: Unknown victim")

            # Send confirmation embed message ONLY for victim**s**
            if confirmation_desc:
                confirmation_embed = discord.Embed(title="Confirmation", description=confirmation_desc,
                                                   timestamp=datetime.datetime.now(), color=discord.Color.random())
                confirmation_msg = await ctx.send(embed=confirmation_embed)

                await confirmation_msg.add_reaction("✅")
                await confirmation_msg.add_reaction("❌")

                try:
                    reply = await self.client.wait_for('reaction_add', timeout=10.0,
                                                       check=lambda reaction, user: user == ctx.author and str(
                                                           reaction.emoji) in ["✅", "❌"])

                except asyncio.TimeoutError:
                    await confirmation_msg.reply("Timeout.")
                    return

                else:
                    if str(reply[0].emoji) == "❌":
                        await confirmation_msg.reply("Understandable. Exiting.")
                        return

            # Send status embed message where status gets updated
            txt = ""
            for i, member in enumerate(iterable):
                
                txt += await self.renameMember(member, bypass_ignore)
                
                # Send status
                if i % 5 == 0 and txt:
                    await ctx.send(txt)
                    txt = ""

            # If there wasn't send something
            if txt:
                await ctx.send(txt)

            # For profiling
            await ctx.send(f"# Renamed {i + 1} user in {str(time.time() - START_TIME)[0:5]}s!")

        # Save new state of names
        self.storage.cacheNames()

    @rename.error
    async def rename_error(self, ctx, exception):
        """ Handle errors
        :param ctx: the context
        :param exception: the error
        """
        print("rename_error", exception)
        await ctx.send(exception)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """ Rename users who join
        :param member: the (now) member
        """
        if self.storage["rename_on_join"]:
            await self.renameMember(member, True)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        """ Handle errors
        :param ctx: the context
        :param exception: the error
        """
        print(exception)
        await ctx.send(exception)
