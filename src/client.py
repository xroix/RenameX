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

    def __init__(self, prefix: str, storage_opt: dict, female_role, male_role, ignore_role: str):
        """ Initialize
        Note: if it any role is a gender than use storage.All()
        :param prefix: the command prefix
        :param storage_opt: options for the storage class
        :param female_role: role that indicates a female role
        :param ignore_role: role that ignores a rename
        """
        super().__init__(command_prefix=prefix)

        self.storage = storage.Storage(**storage_opt)

        self.female_role = female_role
        self.male_role = male_role
        self.ignore_role = ignore_role

        # Help command
        self.remove_command("help")
        self.add_cog(help.HelpCommand(self))

        # Rename command
        self.add_cog(rename.RenameCommand(self))

    async def on_ready(self):
        # Test if there were cached names
        if not self.storage.readNames():
            await self.storage.fetchNewNames()

        print("")
        print("Rename X was started!")
        print("")
        print(self.storage.names_female, self.storage.names_male)
