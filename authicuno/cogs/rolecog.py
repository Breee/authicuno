from discord import Guild, Member, Role, Embed
from discord.ext import commands
from utility.globals import LOGGER
from pmsf.pmsfdbhandler import PmsfDBHandler
import config
import asyncio
from typing import List

class RoleCog(commands.Cog, name="Roles"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = PmsfDBHandler(database=config.PMSF_DB_NAME, user=config.PMSF_DB_USER,
                                password=config.PMSF_DB_PASSWORD, host=config.PMSF_DB_HOST,
                                dialect=config.PMSF_DB_DIALECT, driver=config.PMSF_DB_DRIVER,
                                port=config.PMSF_DB_PORT)

    def get_member_lvl(self, member: Member) -> int:
        curr_access_lvl = 0
        for guild_id, roles in config.GUILDS.items():
            for role_id, access_level in roles.items():
                if role_id in [role.id for role in member.roles]:
                    if access_level > curr_access_lvl:
                        curr_access_lvl = access_level
        return curr_access_lvl

    def get_access_map(self) -> dict:
        member_to_access_level = dict()
        members: List[Member] = self.bot.get_all_members()
        for member in members:
            LOGGER.info(f"Checking {member}")
            LOGGER.info(f"Member roles {member.roles}")
            member_lvl = self.get_member_lvl(member)
            member_to_access_level[member] = member_lvl
        return member_to_access_level

    def update_member(self, member: Member, access_level: int) -> None:
        self.db.update_member(member=member, access_level=access_level)

    @commands.command()
    async def update_members(self, ctx) -> None:
        access_map: dict = self.get_access_map()
        self.db.update_members(access_map)
        #embed = Embed(title="Update Summary", description="\n".join(self.db.get_members()))
        #await ctx.send("Updated.", embed=embed)

    @commands.Cog.listener("on_member_update")
    async def on_member_update(self, before, after):
        LOGGER.info(f"{after} updated")
        access_level = self.get_member_lvl(after)
        self.update_member(member=after,access_level=access_level)



