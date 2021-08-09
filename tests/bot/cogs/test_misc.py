import pytest

from bot.cogs.misc import Miscellaneous


@pytest.mark.asyncio
async def test_shutdown_not_owner_ko(bot, member, mocker):
    ctx = mocker.AsyncMock(author=member)
    cog = Miscellaneous(bot)
    await cog.shutdown(cog, ctx)

    ctx.send.assert_called_once_with('You don\'t have permission to perform this command.')
