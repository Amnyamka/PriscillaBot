import discord
from discord.ext import commands
import asyncio
from discord.utils import get

Pswd =  ("")

TOKEN = ''
bot = commands.Bot(command_prefix='!')

players = {}


@bot.command(pass_context=True)  # разрешаем передавать агрументы
async def test(ctx, arg):  # создаем асинхронную фунцию бота
    await ctx.send('Hello boi!')  # отправляем обратно аргумент


@bot.event
async def on_member_join(member):
    for channel in member.guild.channels:
        if str(channel) == "основной": # We check to make sure we are sending the message in the general channel
            await channel.send(f"""Добро пожаловать на сервер, {member.mention}""")



@bot.event
async def on_ready():
    print("Запущен как:")
    print(bot.user.name)
    print(bot.user.id)
    print('---------------')


@commands.has_permissions(administrator=True)
@bot.command(pass_context = True)
async def dm(ctx, *, ctx2):
    await ctx.send(ctx2)

@bot.command(pass_context=True)
@commands.has_role("dumbass")
async def role(ctx, *, user: discord.Member):
    role = discord.utils.find(lambda r: r.name == 'dumbass', ctx.message.guild.roles)
    if role in user.roles:
        await ctx.send("{} имеет роль {}".format(user, role))
        print(role)
    else:
        await ctx.send('{} не имеет роль {}'.format(user, role))

@bot.command(pass_context = True)
async def join(ctx):
    channel = ctx.message.author.voice.channel
    await bot.join_voice_channel(channel)

@bot.command(pass_context = True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = bot.voice_client_in(server)
    await voice_client.disconnect()


@bot.command(pass_context = True)
async def play(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url)
    players[server.id] = player
    player.start()


@commands.has_permissions(administrator=True)
@bot.command(pass_context = True)
async def send(ctx, rolem, *,content):
    x = ctx.message.guild.members
    print (await ctx.guild.fetch_roles())
    for ctx.message.id in x:
        user = ctx.message.id

        role = discord.utils.find(lambda r: r.name == rolem, ctx.message.guild.roles)
        if role in user.roles:
            try:
                await ctx.message.id.send(content)
                await ctx.send("Сообщение отправлено : {} :white_check_mark: ".format(ctx.message.id))

            except:
                print("ОШИБКА!")
                await ctx.send("Не могу отправить : {} :no_entry: ".format(ctx.message.id))
                print(ctx.message.id)
                print(x)

        else:
            await ctx.send("{} не имеет роли {} :no_entry_sign: ".format(ctx.message.id, role))

bot.run(TOKEN)
