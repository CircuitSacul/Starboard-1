import sys
import traceback
from typing import Any

import discord
from discord.ext import commands
from discord.ext.commands import errors

import bot_config
import errors as cerrors
import functions


class Logging(commands.Cog):
    """Handle logging stuff"""

    def __init__(
        self,
        bot: commands.Bot
    ) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(
        self,
        guild: discord.Guild
    ) -> None:
        support_server = self.bot.get_guild(
            bot_config.SUPPORT_SERVER_ID
        )
        log_channel = discord.utils.get(
            support_server.channels,
            id=bot_config.SERVER_LOG_ID
        )

        members = guild.member_count
        total = 0
        for g in self.bot.guilds:
            try:
                total += g.member_count
            except AttributeError:
                pass

        embed = discord.Embed(
            description=f"Joined **{guild.name}**!\n"
            f"**{members}** Members",
            color=bot_config.GUILD_JOIN_COLOR
        )
        embed.set_footer(
            text=f"We now have {len(self.bot.guilds)} servers and "
            f"{total} users"
        )

        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(
        self,
        guild: discord.Guild
    ) -> None:
        support_server = self.bot.get_guild(
            bot_config.SUPPORT_SERVER_ID
        )
        log_channel = discord.utils.get(
            support_server.channels,
            id=bot_config.SERVER_LOG_ID
        )

        members = guild.member_count
        total = 0
        for g in self.bot.guilds:
            try:
                total += g.member_count
            except AttributeError:
                pass

        embed = discord.Embed(
            description=f"Left **{guild.name}**.\n"
            f"**{members}** Members",
            color=bot_config.GUILD_LEAVE_COLOR
        )
        embed.set_footer(
            text=f"We now have {len(self.bot.guilds)} servers and "
            f"{total} users"
        )

        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_error(
        self,
        event: Any,
        *args: list,
        **kwargs: dict
    ) -> None:
        owner = self.bot.get_user(bot_config.OWNER_ID)
        await owner.send(
            f"Error on event {event} with args {args} and \
                kwargs {kwargs}\n\n```{traceback.format_exc()}```"
        )

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: commands.Context,
        error: Exception,
        force: bool = False
    ) -> None:
        if hasattr(ctx.command, 'on_error') and not force:
            return

        try:
            error = error.original
        except Exception:
            pass
        if type(error) is discord.ext.commands.errors.CommandNotFound:
            return
        elif type(error) in [
            cerrors.BotNeedsPerms, cerrors.DoesNotExist,
            cerrors.NoPremiumError, cerrors.AlreadyExists,
            cerrors.InvalidArgument, cerrors.NotEnoughCredits
        ]:
            pass
        elif type(error) in [
            errors.BadArgument, errors.MissingRequiredArgument,
            errors.NoPrivateMessage, errors.MissingPermissions,
            errors.NotOwner, errors.CommandOnCooldown,
            errors.ChannelNotFound, errors.BadUnionArgument,
            errors.BotMissingPermissions, errors.UserNotFound,
            errors.MemberNotFound, discord.InvalidArgument,
            errors.RoleNotFound
        ]:
            pass
        elif type(error) is discord.ext.commands.errors.MaxConcurrencyReached:
            pass
        elif type(error) is ValueError:
            pass
        elif type(error) is discord.errors.Forbidden:
            error = "I don't have the permissions to do that!"
        elif type(error) is discord.http.Forbidden:
            error = "I don't have the permissions to do that!"
        else:
            embed = discord.Embed(
                title="Hmmm...",
                description=(
                    "Something went wrong while running that command. "
                    "The error has been reported, and we will fix it "
                    "as soon as we can."
                ),
                color=bot_config.ERROR_COLOR
            )
            tb = ''.join(traceback.format_tb(error.__traceback__))
            context = (
                f"Command: {ctx.command}\nArgs: {ctx.args} "
                f"\nKwargs: {ctx.kwargs}"
            )
            embed.add_field(
                name=f"{error.__class__.__name__}",
                value=str(error)
            )
            await ctx.send(embed=embed)
            full_strings = (
                f"{type(error)}: {error}\n\n"
                f"{context}\n\n"
                f"```\n{tb}\n```"
            ).split('\n')
            p = commands.Paginator(prefix='', suffix='')
            for s in full_strings:
                p.add_line(line=s)
            for page in p.pages:
                await functions.alert_owner(ctx.bot, page)
            return
        try:
            await ctx.send(f"{error}")
        except discord.errors.Forbidden:
            await ctx.message.author.send(
                "I don't have permission to send messages in "
                f"{ctx.channel.mention}, so I can't respond "
                "to your command!"
            )


def setup(
    bot: commands.Bot
) -> None:
    bot.add_cog(Logging(bot))
