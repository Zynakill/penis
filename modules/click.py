import disnake
from disnake.ext import commands
import aiosqlite
from datetime import datetime as dt, timedelta


async def get_db():
    db = await aiosqlite.connect("db.db")
    return db


async def get_balance(_id):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM USERS WHERE id = ?", (_id,))
    if bal := await cursor.fetchone():
        return bal[1]
    await db.execute("INSERT INTO USERS VALUES (?, ?)", (_id, 0))
    await db.commit()
    await db.close()
    return 0


class ClickCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        self.eblan = {}

    @commands.Cog.listener("on_connect")
    async def create_db(self):
        db = await get_db()
        await db.execute("CREATE TABLE IF NOT EXISTS USERS (id INT, click INT)")
        await db.commit()
        await db.close()

    @commands.Cog.listener("on_button_click")
    async def click(self, inter: disnake.MessageInteraction):
        if time := self.eblan.get(inter.author.id):
            time: dt
            if time + timedelta(seconds=5) > dt.now():
                return await inter.send(ephemeral=True,
                                        content=f"иди нахуй жди еще `{(time+timedelta(seconds=5))-dt.now()}s`")
        else:
            self.eblan[inter.author.id] = dt.now()
        await inter.send("+1 клик", ephemeral=True)
        db = await get_db()
        clicks = await get_balance(inter.author.id)
        clicks += 1
        await db.execute("UPDATE USERS SET click = ? WHERE id = ?", (clicks, inter.author.id))
        await db.commit()
        await db.close()
        self.eblan[inter.author.id] = dt.now()

    @commands.slash_command(
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def message(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        embed = disnake.Embed()
        embed.title = "Кликер"
        embed.set_footer(text="кликни для получения денег")
        await inter.delete_original_response()
        await inter.channel.send(embed=embed, components=[
            disnake.ui.Button(
                emoji="<:rot:1023146941187625000>",
                custom_id="click"
            )
        ])

    @commands.slash_command()
    async def balance(self, inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed()
        embed.title = "Клик насрал"
        embed.set_footer(text="кликни для получения денег")
        clicks = await get_balance(inter.author.id)
        embed.add_field(name="> клики", value=f"```{clicks}```")
        embed.add_field(name="> в рублях", value=f"```{round(clicks/100, 1)}```")
        await inter.send(embed=embed)


def setup(bot):
    bot.add_cog(ClickCog(bot))
