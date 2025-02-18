import math
import time
import json
import requests
from discord import app_commands
import discord
from discord.ext import commands, tasks
from typing import Optional
from config.config import Config 

class BanTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Origin": "https://plancke.io",
            "Referer": "https://plancke.io/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        })

        self.channels = []

        self.owd_bans = None
        self.ostaff_bans = None
        self.check_loop.start()

    def cog_unload(self):
        self.check_loop.cancel()



    async def is_whitelisted(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id not in Config.authorized_users:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return False
        return True

    @commands.hybrid_command(name="toggletracker", description="Toggle the ban tracker for a specific channel")
    @app_commands.describe(channel="The channel to toggle tracking in")
    async def toggletracker(self, ctx: commands.Context, channel: Optional[discord.TextChannel] = None):
        # Check user whitelist
        if not await self.is_whitelisted(ctx.interaction):
            return

        channel = channel or ctx.channel
        
        if channel.id in self.channels:
            self.channels.remove(channel.id)
            await ctx.send(f"Ban tracker disabled for {channel.mention}")
        else:
            self.channels.append(channel.id)
            await ctx.send(f"Ban tracker enabled for {channel.mention}")


    async def send_to_channels(self, message: str):
        for channel_id in self.channels:
            try:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await channel.send(message)
            except Exception as e:
                print(f"Error sending to channel {channel_id}: {e}")

    @tasks.loop(seconds=6)
    async def check_loop(self):
        try:
            resp = await self.bot.loop.run_in_executor(
                None, 
                lambda: self.session.get("https://api.plancke.io/hypixel/v1/punishmentStats")
            )
            data = resp.json()
            
            wd_bans = data["record"]["watchdog_total"]
            staff_bans = data["record"]["staff_total"]

            if self.owd_bans is not None and self.ostaff_bans is not None:
                wban_dif = wd_bans - self.owd_bans
                sban_dif = staff_bans - self.ostaff_bans

                if wban_dif > 0:
                    if wban_dif >= 10:
                        message = f"# Ban Wave - Watchdog has banned {wban_dif} players!"
                    else:
                        message = f"🐕 **Watchdog** has banned {wban_dif} player{'s' if wban_dif > 1 else ''}!"
                    await self.send_to_channels(message)

                if sban_dif > 0:
                    if sban_dif >= 10:
                        message = f"# Ban Wave - Staff has banned {sban_dif} players!"
                    else:
                        message = f"🕵️ **Staff** has banned {sban_dif} player{'s' if sban_dif > 1 else ''}!"
                    await self.send_to_channels(message)

            self.owd_bans = wd_bans
            self.ostaff_bans = staff_bans

        except Exception as e:
            print(f"Error in check loop: {e}")

    @check_loop.before_loop
    async def before_check_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(BanTracker(bot))