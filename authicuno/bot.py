import discord
import aiohttp
import traceback
import collections
from discord.ext import commands
from discord import DMChannel
from _datetime import datetime
from utility.globals import LOGGER
from cogs.utilscog import UtilsCog
from cogs.rolecog import RoleCog
from core.coredbhandler import CoreDBHandler

import config

class Authicuno(commands.Bot):

    def __init__(self, description, intents):
        super().__init__(command_prefix=[], description=description, pm_help=None,
                         help_attrs=dict(hidden=True), intents=intents)

        self.add_cog(UtilsCog(self))
        self.add_cog(RoleCog(self))
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.db = CoreDBHandler(database=config.CORE_DB_NAME, user=config.CORE_DB_USER,
                                password=config.CORE_DB_PASSWORD, host=config.CORE_DB_HOST,
                                dialect=config.CORE_DB_DIALECT, driver=config.CORE_DB_DRIVER,
                                port=config.CORE_DB_PORT)

    '################ EVENTS ###############'

    async def on_ready(self):
        LOGGER.info('Bot is ready.')
        self.start_time = datetime.utcnow()
        await self.change_presence(activity=discord.Game(name=config.PLAYING))
        # make mentionable.
        self.command_prefix.extend([f'<@!{self.user.id}> ', f'<@{self.user.id}> '])

    def run(self):
        super().run(config.BOT_TOKEN, reconnect=True)

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_resumed(self):
        print('resumed...')

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            LOGGER.critical(f'In {ctx.command.qualified_name}:')
            traceback.print_tb(error.original.__traceback__)
            LOGGER.critical(f'{error.original.__class__.__name__}: {error.original}')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(
                    'Sorry. This command is not how this command works, !help <command_name> to display usage')
        else:
            LOGGER.critical(error)

    async def get_prefix(self, message):
        """|coro|

        Retrieves the prefix the bot is listening to
        with the message as a context.

        Parameters
        -----------
        message: :class:`discord.Message`
            The message context to get the prefix of.

        Returns
        --------
        Union[List[:class:`str`], :class:`str`]
            A list of prefixes or a single prefix that the bot is
            listening for.
        """
        prefix = ret = self.command_prefix

        if not isinstance(message.channel, DMChannel):
            server_prefix = self.db.get_prefix(message.guild.id)
            if server_prefix:
                prefix.append(server_prefix)
        else:
            prefix.append("!")

        if callable(prefix):
            ret = await discord.utils.maybe_coroutine(prefix, self, message)

        if not isinstance(ret, str):
            try:
                ret = list(ret)
            except TypeError:
                # It's possible that a generator raised this exception.  Don't
                # replace it with our own error if that's the case.
                if isinstance(ret, collections.abc.Iterable):
                    raise

                raise TypeError("command_prefix must be plain string, iterable of strings, or callable "
                                "returning either of these, not {}".format(ret.__class__.__name__))

            if not ret:
                raise ValueError("Iterable command_prefix must contain at least one prefix")

        return ret
