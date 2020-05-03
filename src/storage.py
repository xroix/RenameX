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


class All:
    """ Indicates that every role will get triggered
    """
    pass


class Storage:
    """ Handles cached names or fetch them from the api.
    Big thanks to `randomname.de` for their great free service!
    Note: It'll generate **german** names
    """

    def __init__(self, api_url: str, fetch_count: int):
        """ Initialize
        :param str api_url: the url of the used api, {} indicates the parameters
        :param int fetch_count: how many names will get fetched
        """
        self.API_URL = api_url
        self.FETCH_COUNT = fetch_count

        self.names_female = []
        self.names_male = []

    def readNames(self):
        """ Read names from file
        """
        with open("res/names.json", "a+") as f:
            f.seek(0)

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
        """ Write names to file
        :param g: gender
        """
        print("# Loading new names")
        async with aiohttp.ClientSession() as session:
            # Parse gender
            g = {g} if g else {"f", "m"}

            # Iterate over the given genders / gender
            for gender in g:
                async with session.get(
                        self.API_URL.format(self.FETCH_COUNT, gender)) as r:
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
        :param g: the gender
        """
        try:
            return self.names_female.pop() if g == "f" else self.names_male.pop()

        except IndexError:
            # List is empty
            await self.fetchNewNames(g=g)
            return self.names_female.pop() if g == "f" else self.names_male.pop()
