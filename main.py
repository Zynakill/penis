import disnake
from disnake.ext import commands


bot = commands.InteractionBot(
    intents=disnake.Intents.all()
)
bot.load_extensions("modules")
bot.run(open("token").read().strip())
