from discord.ext import commands
import discord
import asyncio
import pyson
import os, errno
import datetime


config = pyson.Pyson('data.json')
token = config.data.get('config').get('token')

Items = {
    "neidan": 100000,
    "spike": 82000,
    "coin": 100000,
    "goblet": 100000000,
    "skin": 42800,
    "whisker": 100000000,
    "fin": 100000000,
    "horn": 53700,
    "shell": 409200,
    "steel": 100000000,
    "jaw": 52400,
    "tongue": 100000000,
    "amethyst": 100000000,
}

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print('Logged in as: ' + bot.user.name)
    print('Bot ID: ' + bot.user.id)


async def connect():
    print('Logging in...')
    while not bot.is_closed:
        try:
            await bot.start(token)
        except:
            await asyncio.sleep(5)


@bot.command(pass_context=True)
async def ping(ctx):
    now = datetime.datetime.utcnow()
    old_message = now - ctx.message.timestamp
    old_delta = old_message.microseconds
    milsec_old = int(old_delta // 1000)
    test_message = await bot.say(f"Checking delay {milsec_old}")
    new_time = now - test_message.timestamp
    delta = new_time.microseconds
    milsec = int(delta // 1000)
    await bot.edit_message(test_message, new_content=f'{milsec}ms round trip time from my message until response.')


@bot.command(pass_context=True)
async def details(ctx):
    '''details DM's a log of all current period transactions

    Usage:
    !details
    '''
    if not os.path.exists(f'{ctx.message.author.id}.txt'):
        await bot.say(f"I don\'t have any details for '{ctx.message.author.mention}' yet.")
        return

    else:
        with open(f'{ctx.message.author.id}.txt', 'r', encoding='utf8') as data:
            lines = ''
            for line in data:
                if line != '\n':
                    lines += line

            if len(lines) == 0:
                lines = "Nothing to show"
            else:
                lines = ("\n".join(lines.split("\n")))

        embed = discord.Embed(title="Details", colour=discord.Colour(0x278d89), description=f'{lines}')
        await bot.send_message(ctx.message.author, embed=embed)
        await bot.say(f'{ctx.message.author.mention} Sending it now..')


@bot.command(pass_context=True)
async def add(ctx, name: str = None, amount: str=None):
    '''Deposit items

    Usage:
    !add <item_name> <amount>
    eg; !add spike 12
    Item names: Neidan, Spike, Coin, Goblet, Skin, Whisker, Fin, Horn, Shell, Steel, Jaw, Tongue, Amethyst
    '''

    if not name or not amount or not amount.isdigit():
        help_description = bot.formatter.format_help_for(ctx, bot.commands.get('add'))[0]
        embed = discord.Embed(description=f'{help_description}', colour=discord.Colour(0xAE0901))
        await bot.say(embed=embed)
        return

    if amount == 0:
        await bot.say('Trying to be sneaky with adding no items eh?')
        return

    name = name.lower()
    if f"{name[:-1]}" in Items:
        name = name[:-1]

    if name not in Items:
        embed = discord.Embed(description=f"It seems '{name}' isn't an item you can add, valid items are: \nItem names:"
                    f"\nNeidan, Spike, Coin, Goblet, Skins, Whisker, Fin, Horn, Shell, Steel, Jaw, Tongue, Amethyst"
                               , colour=discord.Colour(0xAE0901))
        await bot.say(embed=embed)
        return

    if int(amount) > 10000:
        amount = int(amount)
        await bot.say(f'{amount:,} seems like an unrealistic number..')
        return

    else:
        value = Items.get(name)
        amount = int(amount)
        income = value * amount
        if ctx.message.author.id not in config.data.get('users'):
            new_user = {"donated": {}, "cash": 0}
            config.data['users'][ctx.message.author.id] = new_user
            config.save()
            print(f'{ctx.message.author} has been added with ID: {ctx.message.author.id}')

        user_old_cash = config.data.get('users').get(ctx.message.author.id).get('cash')
        new_cash = user_old_cash + income
        config.data['users'][ctx.message.author.id]['cash'] = int(new_cash)
        config.save()

        if name not in config.data.get('users').get(ctx.message.author.id).get('donated'):
            config.data['users'][ctx.message.author.id]['donated'][name] = amount
            config.save()
        else:
            old_item_amount = config.data.get('users').get(ctx.message.author.id).get('donated').get(name)
            new_item_amount = old_item_amount + amount
            config.data['users'][ctx.message.author.id]['donated'][name] = new_item_amount
            config.save()
        with open(f'{ctx.message.author.id}.txt', 'a+', encoding='utf8') as data:
            now = str(ctx.message.timestamp)
            now = now[:-7]
            data.write(f'{now}: {ctx.message.content}\n')
            data.close()
        await bot.say(f"{ctx.message.author.mention} you have donated '{amount} {name}' for ${income:,}")
        return


@bot.command(pass_context=True)
async def delitem(ctx, name: str = None, amount: str=None):
    '''delete items

    Usage:
    !delitem <item_name> <amount>
    eg; !add spike 12
    Item names: Neidan, Spike, Coin, Goblet, Skin, Whisker, Fin, Horn, Shell, Steel, Jaw, Tongue, Amethyst
    '''

    if not name or not amount or not amount.isdigit():
        help_description = bot.formatter.format_help_for(ctx, bot.commands.get('add'))[0]
        embed = discord.Embed(description=f'{help_description}', colour=discord.Colour(0xAE0901))
        await bot.say(embed=embed)
        return

    name = name.lower()
    if f"{name[:-1]}" in Items:
        name = name[:-1]

    if name not in Items:
        embed = discord.Embed(description=f"It seems '{name}' isn't an item you can add, valid items are: \nItem names:"
                    f"\nNeidan, Spike, Coin, Goblet, Skin, Whisker, Fin, Horn, Shell, Steel, Jaw, Tongue, Amethyst"
                               , colour=discord.Colour(0xAE0901))
        await bot.say(embed=embed)
        return

    else:
        value = Items.get(name)
        amount = int(amount)
        income = value * amount
        if ctx.message.author.id not in config.data.get('users'):
            await bot.say(f'{ctx.message.author.mention}, I don\'t see you in my users..')
            return

        if name not in config.data.get('users').get(ctx.message.author.id).get('donated'):
            await bot.say(f'{ctx.message.author.mention}, I don\'t see {name} in your donations.')
            return

        else:
            old_item_amount = config.data.get('users').get(ctx.message.author.id).get('donated').get(name)
            new_item_amount = old_item_amount - amount
            if new_item_amount < 0:
                await bot.say('You can\'t remove more than you have...')
                return
            user_old_cash = config.data.get('users').get(ctx.message.author.id).get('cash')
            new_cash = user_old_cash - income
            config.data['users'][ctx.message.author.id]['cash'] = int(new_cash)
            config.data['users'][ctx.message.author.id]['donated'][name] = new_item_amount
            config.save()
        with open(f'{ctx.message.author.id}.txt', 'a+', encoding='utf8') as data:
            now = str(ctx.message.timestamp)
            now = now[:-7]
            data.write(f'{now}: {ctx.message.content}\n')
            data.close()
        await bot.say(f"{ctx.message.author.mention} i have removed '{amount} {name}' and ${income:,}.")
        return


@bot.command(pass_context=True, aliases=['myloot'])
async def loot(ctx):
    '''Shows donated loot.

    Usage:
    !loot / !myloot
    '''
    if ctx.message.author.id not in config.data.get('users'):
        await bot.say(f'I don\'t have anything for user: {ctx.message.author.mention}.')
        return
    try:
        donated = config.data.get('users').get(ctx.message.author.id).get('donated')
        cash = config.data.get('users').get(ctx.message.author.id).get('cash')
        embed = discord.Embed(title="Donated", description=f'{ctx.message.author.mention}          '
                                                           f'**Total Deposit: **${cash:,}',
                          colour=discord.Colour(0x0AFA02))
        amountlist = ''
        items = ''
        for item in donated:
            amount = config.data.get('users').get(ctx.message.author.id).get('donated').get(item)
            if item == "hunt":
                amount = f'${amount:,}'
            amountlist += f'{amount}\n'
            items += f'{item}\n'

        embed.add_field(name='Name', value=items)
        embed.add_field(name='Amount', value=amountlist)
        await bot.say(embed=embed)
        return
    except:
        embed = discord.Embed(title="Donated", description=f'{ctx.message.author.mention} Cash{cash}',
                              colour=discord.Colour(0x0AFA02))
        embed.add_field(name='Name', value="None")
        embed.add_field(name='Amount', value='None')
        await bot.say(embed=embed)
        return


@bot.command(pass_context=True)
async def donated(ctx):
    '''Donation value

    Usage:
    !donated
    Shows currency value of all donations
    '''
    if ctx.message.author.id not in config.data.get('users'):
        await bot.say(f'I don\'t have anything for user: {ctx.message.author.mention}.')
        return
    users_cash = config.data.get('users').get(ctx.message.author.id).get('cash')
    await bot.say(f'{ctx.message.author.mention}, you have donated ${users_cash:,}.')
    return


@bot.command(pass_context=True)
async def huntsplit(ctx, name: str=None, amount: str=None):
    '''huntsplit allows users to split hunts between members

    Usage:
    !huntsplit <item> <amount> <@mention> <@mention>
    eg; !huntsplit spike 12 @user @user @user @user
    Item names: Neidan, Spike, Coin, Goblet, Skin, Whisker, Fin, Horn, Shell, Steel, Jaw, Tongue, Amethyst
    '''
    if not amount.isdigit():
        await bot.say('You need an amount to split!')
        return

    if not name:
        await bot.say('Please include an item to split')
        return

    mention_list = []
    for mention in ctx.message.mentions:
        mention_list.append(mention.id)

    if len(mention_list) == 0:
        await bot.say('It seems you forgot to mention who was part of the hunt!')
        return

    name = name.lower()
    if f"{name[:-1]}" in Items:
        name = name[:-1]

    if name not in Items:
        await bot.say(f"I can\'t seem to find '{name}' in the item list")
        return

    else:
        amount = int(amount)
        value = Items.get(name)
        item_cost = int(value) * amount
        cash_to_give = item_cost / len(mention_list)
        cash_to_give = round(cash_to_give)
        for person in mention_list:
            if person not in config.data.get('users'):
                print(f'{person} has been added')
                new_user = {"donated": {}, "cash": 0}
                config.data['users'][person] = new_user
                config.save()

            users_cash = config.data.get('users').get(person).get('cash')
            new_users_cash = users_cash + int(cash_to_give)
            config.data['users'][person]['cash'] = new_users_cash
            get_hunt = "hunt"
            if get_hunt not in config.data.get('users').get(person).get('donated'):
                config.data['users'][person]['donated']['hunt'] = int(cash_to_give)
                config.save()
                with open(f'{person}.txt', 'a+', encoding='utf8') as data:
                    player = await bot.get_user_info(person)
                    now = str(ctx.message.timestamp)
                    now = now[:-7]
                    data.write(f'{now}: !huntsplit {player} {cash_to_give:,}\n')
                    data.close()
            else:
                old_hunt = config.data.get('users').get(person).get('donated').get('hunt')
                new_hunt = old_hunt + cash_to_give
                config.data['users'][person]['donated']['hunt'] = int(new_hunt)
                config.save()
                with open(f'{person}.txt', 'a+', encoding='utf8') as data:
                    player = await bot.get_user_info(person)
                    now = str(ctx.message.timestamp)
                    now = now[:-7]
                    data.write(f'{now}: !huntsplit {player} {cash_to_give:,}\n')
                    data.close()

        with open(f'admin.txt', 'a+', encoding='utf8') as data:
            now = str(ctx.message.timestamp)
            now = now[:-7]
            data.write(f'{now}: {ctx.message.author.name}:{ctx.message.content}\n')
            data.close()
        await bot.say(f'Users donations have been updated by ${cash_to_give:,}.')


@bot.command(pass_context=True)
async def delhunt(ctx, name: str=None, amount: str=None):
    '''delhunt allows admins to remove split hunts between members

    Usage:
    !delhunt <item> <amount> <@mention> <@mention>
    eg; !delhunt spike 8 @user @user @user @user
    Item names: Neidan, Spike, Coin, Goblet, Skin, Whisker, Fin, Horn, Shell, Steel, Jaw, Tongue, Amethyst
    '''
    if ctx.message.author is ctx.message.server.owner or ctx.message.author.id in config.data.get('config'):
        if not amount.isdigit():
            await bot.say('You need an amount to split!')
            return

        if not name:
            await bot.say('Please include an item to split')
            return

        mention_list = []
        for mention in ctx.message.mentions:
            mention_list.append(mention.id)

        if len(mention_list) == 0:
            await bot.say('It seems you forgot to mention who was part of the hunt!')
            return

        name = name.lower()
        if f"{name[:-1]}" in Items:
            name = name[:-1]

        if name not in Items:
            await bot.say(f"I can\'t seem to find '{name}' in the item list")
            return

        else:
            amount = int(amount)
            value = Items.get(name)
            item_cost = int(value) * amount
            cash_to_give = item_cost / len(mention_list)
            cash_to_give = round(cash_to_give)
            error_break = False
            for person in mention_list:
                if person not in config.data.get('users'):     
                    print(f'{person} has been added')
                    new_user = {"donated": {}, "cash": 0}
                    config.data['users'][person] = new_user

                users_cash = config.data.get('users').get(person).get('cash')
                new_users_cash = users_cash - int(cash_to_give)
                if new_users_cash > -1:
                    config.data['users'][person]['cash'] = new_users_cash
                    get_hunt = "hunt"
                    if get_hunt not in config.data.get('users').get(person).get('donated'):
                        config.data['users'][person]['donated']['hunt'] = int(cash_to_give)
                        with open(f'{person}.txt', 'a+', encoding='utf8') as data:
                            player = await bot.get_user_info(person)
                            now = str(ctx.message.timestamp)
                            now = now[:-7]
                            data.write(f'{now}: !delhunt {player} {cash_to_give:,}\n')
                            data.close()

                    else:
                        old_hunt = config.data.get('users').get(person).get('donated').get('hunt')
                        new_hunt = old_hunt - cash_to_give
                        config.data['users'][person]['donated']['hunt'] = int(new_hunt)
                        with open(f'{person}.txt', 'a+', encoding='utf8') as data:
                            player = await bot.get_user_info(person)
                            now = str(ctx.message.timestamp)
                            now = now[:-7]
                            data.write(f'{now}: !delhunt {player} {cash_to_give:,}\n')
                            data.close()

                else:
                    await bot.say(f'It seems you\'d be giving <@{person}> negative money..that doesn\'t seem right..')
                    error_break = True
                    break

            config.save()
            if not error_break:
                with open(f'admin.txt', 'a+', encoding='utf8') as data:
                    now = str(ctx.message.timestamp)
                    now = now[:-7]
                    data.write(f'{now}: {ctx.message.author.name}: {ctx.message.content}\n')
                    data.close()
                await bot.say(f'Users hunt donations have been removed by ${cash_to_give:,}.')
                return
    else:
        await bot.say(f'{ctx.message.author.mention}, you are not authorized for this command.')
        return


@bot.command(pass_context=True)
async def sailors(ctx):
    '''sailors shows all users who have donated this current period

    Usage:
    !sailors
    '''
    if len(config.data.get('users')) == 0:
        await bot.say('No users have donated!')
        return

    await bot.send_typing(ctx.message.channel)
    users = config.data.get('users')
    total = []
    for user in users:
        cash = config.data.get('users').get(user).get('cash')
        total.append(int(cash))
    final_total = 0
    for cash_amount in total:
        final_total = final_total + cash_amount

    leaderboard = sorted(users, key=lambda x: users[x]['cash'], reverse=True)
    leaderboard = list(enumerate(leaderboard))
    embed = discord.Embed(colour=discord.Colour(0x278d89))
    embed.set_thumbnail(url='https://cgg.website/lb.png')
    players_list = ''
    cash_list = ''
    for place, entry in leaderboard[:10]:
        user_donated = users[entry]['cash']
        if user_donated is 0:
            percent = 0
            cash_list += f'${user_donated} ({percent})%\n'
        else:
            percent = (user_donated / final_total) * 100
            cash_list += f'${user_donated:,} ({percent:.2f}%)\n'

        player = await bot.get_user_info(entry)
        players_list += f'**#{place+1}** {player.mention}\n'

    embed.add_field(name='Players', value=players_list)
    embed.add_field(name='Donated', value=cash_list)
    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def reset(ctx):
    '''reset allows admins to reset all donations and files

    Usage:
    !reset
    WARNING: this will remove EVERYTHING
    '''
    if ctx.message.author is ctx.message.server.owner or ctx.message.author.id in config.data.get('config'):
        await bot.send_typing(ctx.message.channel)
        with open(f'admin.txt', 'a+', encoding='utf8') as data:
            now = str(ctx.message.timestamp)
            now = now[:-7]
            data.write(f'{now}: {ctx.message.author.name}: {ctx.message.content}\n')
            data.close()

        if not os.path.exists("backups"):
            try:
                os.makedirs("backups")
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        date = datetime.date.today()
        if not os.path.exists(f"backups/{date}"):
            try:
                os.makedirs(f"backups/{date}")
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        for file in os.listdir("."):
            if file.endswith(".txt"):
                try:
                    move = (os.path.join(f"backups\{date}", file))
                    os.rename(file, move)
                except:
                    move = (os.path.join(f"backups\{date}", file))
                    counter = 0
                    while os.path.exists(move):
                        x = 1
                        y = x + counter
                        file_name = f"{file[:-4]}"
                        new_file_name = f"{file_name}({y}).txt"
                        counter += 1
                        move = (os.path.join(f"backups\{date}", new_file_name))
                    os.rename(file, move)

        user_list = []
        for user in config.data.get('users'):
            user_list.append(user)

        for person in user_list:
            config.data['users'].pop(person, None)
            config.save()

        await bot.say('Reset complete.')

    else:
        await bot.say(f'{ctx.message.author.mention}, you are not authorized for this command.')
        return


@bot.command(pass_context=True)
async def addadmin(ctx, user_id: str=None):
    """<addadmin id> Server Owner can add users must be userID."""
    if not user_id:
        return

    if ctx.message.author == ctx.message.server.owner:
        if not user_id.isdigit():
            await bot.say('That isn\'t a valid ID.')
            return
        get_user = await bot.get_user_info(user_id)
        if get_user not in ctx.message.server.members:
            await bot.say('That user doesn\'t seem to be in this server.')
            return
        else:
            with open(f'admin.txt', 'a+', encoding='utf8') as data:
                now = str(ctx.message.timestamp)
                now = now[:-7]
                data.write(f'{now}:{ctx.message.author.name}: {ctx.message.content}\n')
                data.close()
            if user_id not in config.data.get('config'):
                config.data['config'][user_id] = True
                config.save()
            await bot.say('User added.')

    else:
        await bot.say(f'{ctx.message.author.mention} you are not authorized to use this command.')
        return


@bot.command(pass_context=True)
async def deladmin(ctx, user_id: str=None):
    """<addadmin id> Server Owner can delete users must be userID."""
    if not user_id:
        return

    if ctx.message.author == ctx.message.server.owner:
        if not user_id.isdigit():
            await bot.say('That isn\'t a valid ID.')
            return

        get_user = await bot.get_user_info(user_id)
        if get_user not in ctx.message.server.members:
            await bot.say('That user doesn\'t seem to be in this server.')
            return
        else:
            with open(f'admin.txt', 'a+', encoding='utf8') as data:
                now = str(ctx.message.timestamp)
                now = now[:-7]
                data.write(f'{now}: {ctx.message.author.name}: {ctx.message.content}\n')
                data.close()
            if user_id in config.data.get('config'):
                config.data['config'].pop(user_id, None)
                config.save()
            await bot.say('User removed.')

    else:
        await bot.say(f'{ctx.message.author.mention} you are not authorized to use this command.')
        return


bot.loop.run_until_complete(connect())
