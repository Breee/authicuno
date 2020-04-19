from discord.ext import commands
from discord import Role, TextChannel
import time
from core.coredbhandler import CoreDBHandler
import config
from utility.globals import LOGGER



class UtilsCog(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        self.db = CoreDBHandler(database=config.CORE_DB_NAME, user=config.CORE_DB_USER,
                                password=config.CORE_DB_PASSWORD, host=config.CORE_DB_HOST,
                                dialect=config.CORE_DB_DIALECT, driver=config.CORE_DB_DRIVER,
                                port=config.CORE_DB_PORT)

    @commands.command(help="Ping the bot")
    async def ping(self, ctx):
        await ctx.send('pong!')

    @commands.command(help="Return how long the bot is operational.")
    async def uptime(self, ctx):
        seconds = time.time() - self.start_time
        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24
        await ctx.send('Online for %.3f seconds (that are %.3f minutes or %.3f hours or %.3f days)' % (
            seconds, minutes, hours, days))

    @commands.command(aliases=['dracarys'])
    @commands.is_owner()
    async def purge(self, ctx, number):
        async for message in ctx.channel.history(limit=int(number)):
            await message.delete()
        await ctx.send("Dracarys! Purged %s messages!" % number)

    @commands.command(help="Show all servers (owner only)")
    @commands.is_owner()
    async def servers(self, ctx):
        guilds = []
        async for guild in self.bot.fetch_guilds(limit=150):
            guilds.append("- %s (%s)" % (guild.name, guild.id))
        await ctx.send("__**Servers**__\n%s" % "\n".join(guilds))

    @commands.command(help="Show all servers (owner only)")
    @commands.is_owner()
    async def notify_servers(self, ctx, message):
        admin_ids = set()
        admins = set()
        for member in self.bot.get_all_members():
            if member.guild_permissions.administrator and not member.bot:
                if member.id not in admin_ids:
                    admins.add(member)
                    admin_ids.add(member.id)
        app = await self.bot.application_info()
        if app.team:
            owners = [m.mention for m in app.team.members]
        else:
            owners = [app.owner.mention]
        message_prefix = f"Hey there,\nYou are the administrator of a server on which I am and I got an important " \
                         f"notification from my owner(s) {' '.join(owners)}:\n\n"
        LOGGER.info(f"Admins I notify: {[a.name for a in admins]}")
        for admin in admins:
            try:
                await admin.send(message_prefix + message)
            except:
                LOGGER.error(f"Could not send notification to {admin.name}")

    @commands.command(help="Leave a server (owner only)")
    @commands.is_owner()
    async def leave(self, ctx, id):
        guild = self.bot.get_guild(int(id))
        channel = ctx.channel
        await ctx.send("Are you sure you want to leave Server %s?" % guild)

        def check(m):
            return m.channel == channel

        msg = await self.bot.wait_for('message', check=check, timeout=10)
        if msg.content == "yes":
            await ctx.send("you said yes, leaving")
            await guild.leave()
        elif msg.content == "no":
            await ctx.send("you said no")
        else:
            await ctx.send("No valid answer")

    async def check_is_moderator_or_owner(self, ctx: commands.Context) -> bool:
        moderator_roles = self.db.get_moderator_roles(ctx.guild.id)
        user_roles = [str(role.id) for role in ctx.author.roles]
        has_admin_permissions = ctx.author.guild_permissions.administrator
        is_authorized = any(role in user_roles for role in moderator_roles) or await self.bot.is_owner(ctx.author) or has_admin_permissions
        if is_authorized:
            return True
        else:
            await ctx.send(f"You are not allowed to do this (ノಠ益ಠ)ノ彡┻━┻")
            return False

    @commands.command(help="Add moderator (owner only)")
    async def add_mod_role(self, ctx, role):
        role_id = None
        if isinstance(role, Role):
            role_id = role.id
        elif isinstance(role,int):
            role_id = str(role)
        elif isinstance(role, str):
            role_id = role

        if role_id:
            if await self.check_is_moderator_or_owner(ctx):
                guild_id = ctx.guild.id
                self.db.add_moderator_roles(guild_id, [role_id])
                await ctx.send(f"Added moderator roles {[role]}")

    @commands.command(help="Get moderator roles (owner only)")
    async def get_mods(self, ctx):
        guild_id = ctx.guild.id
        roles = self.db.get_moderator_roles(guild_id)
        await ctx.send(f"moderator roles {roles}")    \

    @commands.command(help="Get moderator roles (owner only)")
    async def reset_mods(self, ctx):
        if await self.check_is_moderator_or_owner(ctx):
            guild_id = ctx.guild.id
            self.db.reset_moderator_roles(guild_id)
            await ctx.send(f"resetted moderator roles.")

    @commands.command(help="Set prefix of the bot")
    async def set_prefix(self, ctx: commands.Context, prefix : str) -> None:
        if await self.check_is_moderator_or_owner(ctx):
            guild_id = ctx.guild.id
            self.db.set_prefix(server_id=guild_id, prefix=prefix)
            await ctx.send(f"Set prefix to {prefix}")


    @commands.command(help="Get prefix of the bot")
    async def get_prefix(self, ctx: commands.Context) -> None:
        guild_id = ctx.guild.id
        prefix = self.db.get_prefix(server_id=guild_id)
        await ctx.send(f"Prefix for this server: {prefix}")

    @commands.command(help="Get prefix of the bot")
    async def reset_prefix(self, ctx: commands.Context) -> None:
        if await self.check_is_moderator_or_owner(ctx):
            guild_id = ctx.guild.id
            self.db.reset_prefix(server_id=guild_id)
            await ctx.send(f"Cleared Prefix for this server.")