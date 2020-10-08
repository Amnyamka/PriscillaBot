import discord
from discord.ext import commands



bot = commands.Bot(command_prefix='!')

TOKEN = ''

@bot.command(pass_context=True)  # allow the transfer of arguments
async def test(ctx, arg):  # create an asynchronous bot function
    await ctx.send('Hello boi!')  # send back the argument


@bot.event
async def on_member_join(member):
    for channel in member.guild.channels:
        if str(channel) == "основной": # We check to make sure we are sending the message in the general channel
            await channel.send(f"""Добро пожаловать на сервер, {member.mention}""")



@bot.event
async def on_ready():
    print("Launched as:")
    print(bot.user.name)
    print(bot.user.id)
    print('Version: 0.2')
    print('---------------')

@bot.command(pass_context=True)
async def role(ctx, userrole, *,user: discord.Member):                                                                  # checking the role of the user
                                                                                                                        # Example: !role role Amnyam
                                                                                                                        # Use a roles only with 1 word or it will NOT work.username = discord.Membe

#Amnyam --> Amnyam#2062 need more time to solve this. I know the problem with Member "" not found.
    try:
        role = discord.utils.find(lambda r: r.name == userrole, ctx.message.guild.roles)

        if role in user.roles:
            await ctx.send("{} has role: {} :white_check_mark:".format(user, role))
            print("{} has role: {}".format(user, role))
            print('==========================')

        elif role == None:
            await ctx.send("There is no such role: {} :no_entry:".format(userrole))
            print("There is no such role: {}".format(userrole))
            print('==========================')

        else:
            await ctx.send('{} has no role: {} :no_entry_sign:'.format(user, role))
            print('{} has no role: {}'.format(user, role))
            print('==========================')
    except:
        await ctx.send('There is no such user :no_entry_sign:')
        print('There is no such user')
        print('==========================')

@bot.command(pass_context=True)
async def roleall(ctx, userrole):                                                                                       # checking the role of all users
                                                                                                                        # Example: !roleall role
    x = ctx.message.guild.members
    for ctx.message.id in x:
        user = ctx.message.id


        role = discord.utils.find(lambda r: r.name == userrole, ctx.message.guild.roles)
        if role in user.roles:
            await ctx.send("{} has role: {} :white_check_mark:".format(user, role))
            print("{} has role: {}".format(user, role))
            print('==========================')

        elif role == None:
            await ctx.send("There is no such role: {} :no_entry:".format(userrole))
            print("There is no such role: {}".format(userrole))
            print('==========================')
            break

        # else:                                                                                                         # Use this if you want to see people without a specified role
        #     await ctx.send('{} has no role: {} :no_entry_sign:'.format(user, role))
        #     print('{} has no role: {}'.format(user, role))
        #     print('==========================')




@commands.has_permissions(administrator=True)
@bot.command(pass_context = True)
async def send(ctx, userrole, *,content):                                                                               # sends direct messages to all users of the group with the specified role.
                                                                                                                        # Example: !send role Text
                                                                                                                        # Use a roles only with 1 word or it will NOT work.
    x = ctx.message.guild.members

    for ctx.message.id in x:

        user = ctx.message.id
        role = discord.utils.find(lambda r: r.name == userrole, ctx.message.guild.roles)
        if role in user.roles:
            try:
                await ctx.message.id.send(content)
                await ctx.send("Message delivered : {} :white_check_mark: ".format(user))
                print("Message delivered : {}".format(user))
                print('==========================')

            except:
                await ctx.send("ERROR! Can't send the message : {} :no_entry: ".format(user))
                print("ERROR! Can't send the message : {}".format(user))
                print('==========================')


        elif role == None:
            await ctx.send("There is no such role: {} :no_entry:".format(userrole))
            print("There is no such role: {}".format(userrole))
            print('==========================')
            break

        else:
            await ctx.send("{} has no role {} :no_entry_sign: ".format(user, role))
            print("{} has no role {} :no_entry_sign: ".format(user, role))
            print('==========================')

bot.run(TOKEN)
