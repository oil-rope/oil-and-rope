from discord.ext.commands import command, context


def test():
    pass


@command()
async def logout(ctx: context.Context):
    await ctx.send('Hello!')
    await ctx.bot.logout()


@command()
async def not_test(ctx: context.Context):
    pass
