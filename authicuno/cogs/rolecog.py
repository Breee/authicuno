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
        LOGGER.debug("member", member.name)
        LOGGER.debug("member", member.roles)
        for guild_id, roles in config.GUILDS.items():
            LOGGER.debug("guild ", guild_id)
            for role_id, access_level in roles.items():
                LOGGER.debug(f'role {role_id} = {access_level}')
                if role_id in [role.id for role in member.roles]:
                    LOGGER.debug(f"{member.name} has role: {role_id}")
                    LOGGER.debug(f"{member.name}  curr: {curr_access_lvl}")
                    if access_level > curr_access_lvl:
                        LOGGER.debug(f"{member.name}  new: {access_level}")
                        curr_access_lvl = access_level
        return curr_access_lvl

    def get_access_map(self) -> dict:
        member_to_access_level = dict()
        members: List[Member] = self.bot.get_all_members()
        for member in members:
            member_lvl = self.get_member_lvl(member)
            if member in member_to_access_level:
                if member_lvl > member_to_access_level[member]:
                    member_to_access_level[member] = member_lvl
            else:
                member_to_access_level[member] = member_lvl
        return member_to_access_level

    def update_member(self, member: Member) -> None:
        access_level = self.get_member_lvl(member)
        self.db.update_member(member=member, access_level=access_level)

    @commands.Cog.listener("on_ready")
    @commands.Cog.listener("on_guild_remove")
    @commands.Cog.listener("on_guild_join")
    async def update_members(self):
        access_map: dict = self.get_access_map()
        self.db.update_members(access_map)

    @commands.Cog.listener("on_member_update")
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            LOGGER.info(f"Member {after} updated roles, updating access-level")
            self.update_member(member=after)

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member):
        LOGGER.info(f"Member {member} left server, updating access-level")
        self.update_member(member=member)

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member):
        LOGGER.info(f"Member {member} joined server, updating access-level")
        self.update_member(member=member)

    @commands.command()
    async def print_roles(self, ctx):
        member = ctx.author
        roles = "\n".join([f'{r.name} ({r.id})' for r in member.roles])
        await ctx.send(f'Your roles:\n```\n{roles}\n```')




