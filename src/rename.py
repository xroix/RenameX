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
import time
import typing

import discord
from discord.ext import commands

from src import client, storage


class RenameCommand(commands.Cog):
    """ The rename cog / module / command
    Ever wanted to rename you entire Discord Server?
    """

    def __init__(self, _client):
        """ Initialize
        :param _client: the client
        """
        super().__init__()

        self.client = _client
        self.storage = _client.storage

    @commands.command()
    async def test(self, ctx: commands.Context):
        """ Test the mechanism
        :param commands.Context ctx: the context"""
        _old = len(self.storage.names_male)
        for i, member in enumerate(ctx.guild.members):
            print(i, member, await self.storage.popNames("m"))

        print(self.storage.names_male)
        self.storage.cacheNames()
        await ctx.send(f"List length changed from {_old} to {len(self.storage.names_male)}")

    @commands.command()
    @commands.has_any_role("Menschen erster Klasse", "Edelmann")
    async def rename(self, ctx: commands.Context, victim: typing.Union[discord.Role, discord.Member, str],
                     bypass_ignore: typing.Optional[str] = "false"):
        """ Rename the entire server or perhaps only one player?
        :param ctx: the context
        :param victim: the victim
        :param bypass_ignore: if it bypasses the ignore feature
        """

        # Parse parameters
        if isinstance(victim, str) and victim != "all":
            raise commands.BadArgument(f"> Invalid Argument `{victim}`!")

        bypass_ignore = True if bypass_ignore.lower() == "true" else False

        with ctx.typing():
            await ctx.send(f"**# Log**:\n┌────────────────────────────\n> "
                           f"Ignore-Role **bypass** activated: `{bypass_ignore}`")

            # Roles
            female_role_obj = discord.utils.get(ctx.guild.roles, name=self.client.female_role) \
                if not isinstance(self.client.female_role, storage.All) else storage.All()

            male_role_obj = discord.utils.get(ctx.guild.roles, name=self.client.male_role) \
                if not isinstance(self.client.male_role, storage.All) else storage.All()

            ignored_role_obj = discord.utils.get(ctx.guild.roles, name=self.client.ignore_role)

            # For Profiling
            START_TIME = time.time()
            STATS = {"count": 0}

            # If it is a role
            if isinstance(victim, discord.Role) or isinstance(victim, str):
                _iter = None

                # If all
                if isinstance(victim, str) and victim == "all":
                    # Vars
                    _iter = ctx.guild.members
                    _msg = await ctx.send(f"> Will change nicknames of everyone! Are you sure?")

                # Or just a role
                else:
                    _iter = victim.members
                    _msg = await ctx.send(f"> Will change nicknames of role `{victim.name}`! Are you sure?")

                # Ask user
                # Add reactions
                await _msg.add_reaction("✅")
                await _msg.add_reaction("❌")

                def check(reaction, user):
                    """Check the reaction
                    """
                    return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]

                try:
                    _reply = await self.client.wait_for('reaction_add', timeout=10.0, check=check)

                except asyncio.TimeoutError:
                    await _msg.edit(content="> Timeout :(")

                else:
                    if str(_reply[0].emoji) == "✅":
                        await ctx.send("> O.K.")

                    elif str(_reply[0].emoji) == "❌":
                        await ctx.send("> Exit")
                        return

                txt = ""

                # Iterate over each member of guild or role
                for i, member in enumerate(_iter):
                    text = ""

                    # If it is ignored
                    if not bypass_ignore and ignored_role_obj in member.roles:
                        txt += f"> [?] ignored {member.name}\n"
                        print(f"> [?] ignored {member.name}\n")

                    # Or female
                    elif isinstance(female_role_obj, storage.All) or female_role_obj in member.roles:
                        name = await self.storage.popNames("f")

                        txt += f"> [w] {member.name} => {name}\n"
                        print(f"> [w] {member.name} => {name}\n")

                        await member.edit(nick=name)

                    # Or else => male
                    elif isinstance(male_role_obj, storage.All) or male_role_obj in member.roles:
                        name = await self.storage.popNames("m")

                        txt += f"> [m] {member.name} => {name}\n"
                        print(f"> [m] {member.name} => {name}\n")

                        await member.edit(nick=name)

                    # Not specified
                    else:
                        txt += f"> [?] ignored {member.name}; unspecified Gender!\n"
                        print(f"> [?] ignored {member.name}\n; unspecified Gender!")

                    # Send status
                    if i % 5 == 0:
                        await ctx.send(txt)
                        txt = ""

                # If there wasn't send something
                if txt:
                    await ctx.send(txt)

                # For profiling
                STATS["count"] = i + 1

            # Or a member
            elif isinstance(victim, discord.Member):
                txt = ""
                name = None

                # If it is ignored
                if not bypass_ignore and ignored_role_obj in victim.roles:
                    txt = f"> [?] ignored {victim.name}\n"
                    print(f"[?] ignored {victim.name}\n")

                # Or female
                elif isinstance(female_role_obj, storage.All) or female_role_obj in victim.roles:
                    name = await self.storage.popNames(g="f")

                    txt = f"> [w] {victim.name} => {name}\n"
                    print(f"> [w] {victim.name} => {name}\n")

                    await victim.edit(nick=name)

                # Or else => male
                elif isinstance(male_role_obj, storage.All) or male_role_obj in victim.roles:
                    name = await self.storage.popNames(g="m")

                    txt = f"> [m] {victim.name} => {name}\n"
                    print(f"> [m] {victim.name} => {name}\n")

                    await victim.edit(nick=name)

                else:
                    txt = f"> [?] ignored {victim.name}; unspecified Gender!\n"
                    print(f"> [?] ignored {victim.name}\n; unspecified Gender!")

                await ctx.send(txt)

                # For profiling
                STATS["count"] = 1

            # For all types
            await ctx.send(f"# Renamed {STATS['count']} user in {str(time.time() - START_TIME)[0:5]}s!")

        self.storage.cacheNames()

    @rename.error
    async def rename_error(self, ctx, exception):
        """ Handle errors
        :param ctx: the context
        :param exception: the error
        """
        print(exception)
        await ctx.send(exception)

    async def on_command_error(self, ctx, exception):
        """ Handle errors
        :param ctx: the context
        :param exception: the error
        """
        print(exception)
        await ctx.send(exception)
