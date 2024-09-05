import discord
from redbot.core import commands
import aiohttp
import json

class MissingKids(commands.Cog):
    """Cog to interact with the National Center for Missing and Exploited Children"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def ncmec(self, ctx):
        """Primary command group"""
        pass
    
    @ncmec.command()
    async def recent(self, ctx):
        """Fetch information about recently missing children."""
        url = "https://api.missingkids.org/missingkids/servlet/JSONDataServlet?action=publicSearch"
        headers = {"Accept": "application/json"}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        await ctx.send("Failed to fetch data from the MissingKids API.")
                        return

                    try:
                        data = await response.json()
                    except aiohttp.ContentTypeError:
                        text_data = await response.text()
                        await ctx.send("Received unexpected content type from the MissingKids API, attempting to parse as text.")
                        try:
                            data = json.loads(text_data)
                        except json.JSONDecodeError:
                            await ctx.send("Failed to parse the response from the MissingKids API.")
                            return

                    if not data.get("persons"):
                        await ctx.send("No recently missing children found.")
                        return

                    embed = discord.Embed(title="Recently Missing Children", color=discord.Color.red())
                    for person in data["persons"][:10]:  # Limit to first 10 results
                        embed.add_field(
                            name=f"{person.get('firstName', 'Unknown')} {person.get('lastName', 'Unknown')}",
                            value=f"Age: {person.get('age', 'Unknown')}\n"
                                  f"Missing Since: {person.get('missingDate', 'Unknown')}\n"
                                  f"Location: {person.get('missingCity', 'Unknown')}, {person.get('missingState', 'Unknown')}\n"
                                  f"Case Number: {person.get('caseNumber', 'Unknown')}",
                            inline=False
                        )

                    await ctx.send(embed=embed)
            except aiohttp.ClientError as e:
                await ctx.send(f"An error occurred while trying to fetch data: {str(e)}")
            except Exception as e:
                await ctx.send(f"An unexpected error occurred: {str(e)}")

