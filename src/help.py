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

import datetime

import discord
from discord.ext import commands


class HelpCommand(commands.Cog):
    """ /help
    """

    def __init__(self, client):
        """ Initialize
        :param client: the client
        """
        super().__init__()
        self.client = client

        # Remove old
        self.client.remove_command("help")

    @commands.command()
    async def help(self, ctx: commands.Context):
        """ Overwrite the default help command
        :param ctx: the context
        """
        embed = discord.Embed(title="RenameX Commands :tools:", timestamp=datetime.datetime.now(),
                              color=discord.Color.green())
        embed.add_field(name=":arrow_right: **`/rename [member;role;'all'] {bool: bypass_ignore}`**",
                        value="Change the nicknames of a player or perhaps even an entire server!")
        await ctx.send("", embed=embed)

    @commands.command()
    async def info(self, ctx: commands.Context):
        embed = discord.Embed(title="RenameX Info :question:", timestamp=datetime.datetime.now(),
                              color=discord.Color.green())
        embed.add_field(name=":telephone: **Author**",
                        value="Created by XroixHD", inline=False)
        embed.add_field(name=":keyboard: **Source Code**",
                        value="https://github.com/XroixHD/RenameX", inline=False)
        await ctx.send("", embed=embed)
