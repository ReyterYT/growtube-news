import storage
from discord.ext import commands
import os
import json
import asyncio
import traceback

class DB(storage.MockAsyncReplitStorage):

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self._items.update(
            {
                "0": {},
                "1": {},
                "2": {}
            }
        )

class GrowTube(commands.Bot):

    db: storage.AsyncReplitStorage

    def __init__(self, command_prefix, help_command=None, description=None, **options):
        super().__init__(command_prefix, help_command=help_command, description=description, **options)
        self.db = storage.AsyncReplitStorage()
    
    async def close(self):
        await asyncio.gather(self.db.close(), super().close())

class NotPermittedForPublish(commands.CheckFailure):
    pass

def get_bot():
    
    config = None
    config_file = "config.json" if os.path.isfile("config.json") else "default-config.json"
    with open("config.json") as f:
        config = json.load(f)
    
    token = os.getenv("TOKEN")

    if not token:
        import dotenv
        dotenv.load_dotenv()
        token = os.getenv("TOKEN")

    bot = GrowTube(
        command_prefix = config["prefix"],
        owner_ids = config["owners"]
    )
    bot.CHANNEL_LOG = 883936874400452619

    async def _ext_err(e: Exception):
        await bot.wait_until_ready()
        traceback.print_exception(type(e), e, e.__traceback__)

    for extension in config["ext"]:
        try:
            bot.load_extension(config["ext_dir"]+"."+extension)
        except Exception as exc:
            asyncio.create_task(_ext_err(exc))

    if config["debug"]:
        bot.load_extension("jishaku")

    @bot.listen()
    async def on_ready():
        print("Logged in")

    import aiohttp

    async def _job():
        async with aiohttp.ClientSession() as sess:
            await sess.post("http://localhost:8000/restart", data={"token": bot.http.token})

    @bot.command()
    @commands.is_owner()
    async def restart(ctx):
        await ctx.message.add_reaction("\U00002705")
        asyncio.create_task(_job())
        
    return bot, token

if __name__ == "__main__":
    bot, token = get_bot()
    bot.run(token)
