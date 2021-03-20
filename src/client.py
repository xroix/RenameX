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

import discord
from discord.ext import commands

from src import storage, rename, help


class Client(commands.Bot):
    """ The command bot (will classify it as client)
    """

    def __init__(self, storage: storage.Storage):
        """ Initialize
        Note: if it any role is a gender than use storage.All()
        :param storage: the storage instance
        """
        intents = discord.Intents.default()
        intents.members = True

        super().__init__(command_prefix=storage["prefix"], intents=intents)

        self.storage = storage

        self.female_role = storage["identifiers"]["female"]
        self.male_role = storage["identifiers"]["male"]
        self.ignore_role = storage["identifiers"]["ignore"]

        # Help command
        self.add_cog(help.HelpCommand(self))

        # Rename command
        self.add_cog(rename.RenameCommand(self))

    async def on_ready(self):
        # Test if there were cached names
        if not self.storage.readNames():
            await self.storage.fetchNewNames()
            self.storage.cacheNames()

        # Set presence
        activity = discord.Activity(type=discord.ActivityType.competing, name="renaming people")
        await self.change_presence(activity=activity)

        print("")
        print("Rename X was started!")
        print("")
