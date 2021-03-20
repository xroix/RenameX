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

import json
import aiohttp


class SettingsParser:
    """ Parses the settings.json file for settings
    """

    DEFAULT_PATH = "res/settings.json"
    DEFAULT_TEMPLATE = {
        "prefix": "/",
        "api_url": "https://randomname.de/?format=json&count={}&gender={}",
        "fetch_count": "100",
        "token": "",
        "rename_on_join": False,
        "identifiers": {
            # For example: (dont ask me for the naming scheme, it's because of friends)
            # "NAME TYPE FOR API": "ROLE TO DETECT",
            "female": "E-Girl",
            "male": "",  # gets no role
            "ignore": "ignore"
        }
    }
    DEFAULT_STRUCTURE = {
        "prefix": str,
        "api_url": str,
        "fetch_count": str,
        "token": str,
        "rename_on_join": bool,
        "identifiers": {
            "female": str,
            "male": str,
            "ignore": str
        }
    }

    def __init__(self):
        self.cached = {}

    def __getitem__(self, item):
        """ Access settings via []
        :param item: item name
        """
        # Load settings if not loaded
        if not self.cached:
            self.load_settings()

        if item in self.cached:
            return self.cached[item]

    def load_settings(self):
        """ Loads settings and cache them for editing
        """
        try:
            with open(self.DEFAULT_PATH, "r") as f:
                self.cached = self.check_settings(json.load(f), self.DEFAULT_STRUCTURE, self.DEFAULT_TEMPLATE)

        except FileNotFoundError:
            print("# Setting file not found. Creating. Loading DEFAULT_TEMPLATE.")
            with open(self.DEFAULT_PATH, "w+") as f:
                json.dump(self.DEFAULT_TEMPLATE, f, ident=4)

            self.cached = self.DEFAULT_TEMPLATE.copy()

        except json.JSONDecodeError:
            print("# Setting file invalid! Loading DEFAULT_TEMPLATE")
            self.cached = self.DEFAULT_TEMPLATE.copy()

    def check_settings(self, tile, check_tile, default, *, is_starting_point=True):
        """ Checks given dict if it is compliant with `DEFAULT_TEMPLATE` && `DEFAULT_STRUCTURE`
            Note: It doesn't change `tile` because it creates an copy
        :param tile: the tile to check, if a part is iterable, it will check them recursively
        :param check_tile: the current layer of DEFAULT_STRUCTURE
        :param default: the current layer of DEFAULT_TEMPLATE
        :param is_starting_point: if it is the starting point
        :returns: the parsed and corrected settings
        """
        # "Remove" reference
        if is_starting_point:
            tile = tile.copy()

        # For dictionary
        if isinstance(tile, dict):
            for check_key, check_type in check_tile.items():
                # Get the provided value
                if check_key in tile:
                    value = tile[check_key]
                    key = check_key

                else:
                    print(f"# {check_key} is missing, loading default")
                    tile.update({check_key: default[check_key]})
                    continue

                # Recursion
                if isinstance(value, dict):
                    self.check_settings(tile[key], check_tile[key], default[key], is_starting_point=False)  # tile[key] for reference
                    continue

                # Wrong type
                if not isinstance(value, check_type):
                    # Load in default, works because of references
                    # Dont use value because .items() creates a copy
                    print(f"# {key} is invalid, loading default")
                    tile[key] = default[key]

        return tile


class Storage:
    """ Handles cached names or fetches them from the api.
    Big thanks to `randomname.de` for their great free service!
    Note: It'll generate **german** names
    """

    def __init__(self):
        """ Initialize
        """
        self.settings_parser = SettingsParser()
        self.settings_parser.load_settings()

        self.names_female = []
        self.names_male = []

    def __getitem__(self, item):
        """ Access settings via []
        :param item: item name
        """
        return self.settings_parser[item]

    def readNames(self):
        """ Read names from file
        """
        with open("res/names.json", "r+") as f:
            # If empty, load in default
            # if not f.read():
            #     print("# Loading default template for names.json")
            #     json.dump({"female": [], "male": []}, f)
            #     f.seek(0)

            _data = json.load(f)

        if _data["female"] and _data["male"]:
            self.names_female = _data["female"]
            self.names_male = _data["male"]

            print("# Loaded cache of names from file!")
            return True

        else:
            print("# No cache of names were found!")
            return False

    async def fetchNewNames(self, *, g: str = None):
        """ Fetch new names from api
        :param g: if to fetch names **only** for gender g
        """
        print("# Loading new names")
        async with aiohttp.ClientSession() as session:
            # Parse gender
            g = {g} if g else {"f", "m"}

            # Iterate over the given genders / gender
            for gender in g:
                async with session.get(self["api_url"].format(self["fetch_count"], gender)) as r:
                    if r.status == 200:
                        js = await r.json()

                        # Female
                        if gender == "f":
                            self.names_female = [x["firstname"] + " " + x["lastname"] for x in js]

                        # Male
                        elif gender == "m":
                            self.names_male = [x["firstname"] + " " + x["lastname"] for x in js]

                        # Error
                        else:
                            raise Exception(f"Invalid gender {gender}")

    def cacheNames(self):
        """ Write names to file
        """
        with open("res/names.json", "w+") as f:
            f.seek(0)

            json.dump({"female": self.names_female, "male": self.names_male}, f, indent=4)

        print("# Cached names to file!")

    async def popNames(self, g: str) -> str:
        """ Pop the first name of given category
        :param g: the gender to pop out
        """
        try:
            return self.names_female.pop() if g == "f" else self.names_male.pop()

        except IndexError:
            # List is empty
            await self.fetchNewNames(g=g)
            return self.names_female.pop() if g == "f" else self.names_male.pop()
