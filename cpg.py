import discord
import json
import random
import requests
import os

client = discord.Client()

@client.event
async def on_raw_reaction_add(payload):
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    guild_id = str(payload.guild_id)
    emoji = str(payload.emoji)

    with open('reaction_map.json') as file:
        reaction_map = json.load(file)

    author = message.author.name

    if guild_id not in reaction_map:
        reaction_map[guild_id] = {}

    if emoji not in reaction_map[guild_id]:
        reaction_map[guild_id][emoji] = {}

    if author in reaction_map[guild_id][emoji]:
        reaction_map[guild_id][emoji][author] += 1
    else:
        reaction_map[guild_id][emoji][author] = 1

    with open('reaction_map.json', 'w') as file:
        json.dump(reaction_map, file, indent=4)

@client.event
async def on_raw_reaction_remove(payload):
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    guild_id = str(payload.guild_id)
    emoji = str(payload.emoji)

    with open('reaction_map.json') as file:
        reaction_map = json.load(file)
    
    author = message.author.name

    if guild_id in reaction_map and emoji in reaction_map[guild_id] and author in reaction_map[guild_id][emoji]:
        if reaction_map[guild_id][emoji][author] > 0:
            reaction_map[guild_id][emoji][author] -= 1
    
    with open('reaction_map.json', 'w') as file:
        json.dump(reaction_map, file, indent=4)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # if message begins with #react keyword
    if message.content.split(' ')[0] == '#react':
        msg = ''
        guild_id = str(message.guild.id)
        with open('reaction_map.json') as file:
            reaction_map = json.load(file)

        target = message.content.split(' ')[-1]

        # if guild id isn't in the map, then no reactions have been tracked for the server
        if guild_id not in reaction_map:
            msg = 'I haven\'t been initialized in this server...'

        # if target is an emoji, then search for the top people for that reaction
        elif target in reaction_map[guild_id]:
            emoji = target
            n = 5  # max number of members to display
            top = sorted(reaction_map[guild_id][emoji], key=reaction_map[guild_id][emoji].get, reverse=True)[:n]
            topX = ''
            for i in range(len(top)):
                topX += '\n    ' + str(i + 1) + '. ' + top[i] + ', with ' + str(reaction_map[guild_id][emoji][top[i]])

            people = ''
            isAre = ''
            if len(top) == 1:
                people = 'person'
                isAre = 'is'
            else:
                people = str(len(top)) + ' people'
                isAre = 'are'

            msg = 'The top ' + people + ' for ' + emoji + ' reactions ' + isAre + ': ' + topX
        
        # if people are tagged in the message, search for the people's top reactions
        # limit to max 3 people per message to avoid super long message spam
        elif len(message.mentions) > 0 and len(message.mentions) < 4:
            msg = ''
            for member in message.mentions:
                member_reacts = {}
                for emoji in reaction_map[guild_id]:
                    if member.name in reaction_map[guild_id][emoji]:
                        if not reaction_map[guild_id][emoji][member.name] == 0:
                            member_reacts[emoji] = reaction_map[guild_id][emoji][member.name]

                if len(member_reacts) == 0:
                    msg += 'I haven\'t seen any reactions to ' + member.display_name + ' yet'
                else:
                    n = 3  # max number of reactions to display
                    num = min(len(member_reacts), n)

                    if num == 1:
                        msg += 'The top reaction for '
                        isAre = 'is'
                    else:
                        msg += 'The top ' + str(num) + ' reactions for '
                        isAre = 'are'

                    msg += member.display_name + ' ' + isAre + ':'

                    top = sorted(member_reacts, key=member_reacts.get, reverse=True)[:n]
                    for i in range(num):
                        msg += '\n    ' + str(i + 1) + '. ' + top[i] + ', with ' + str(member_reacts[top[i]])
                
                msg += '\n'

        else:
            msg = 'Invalid command, or I haven\'t seen that emoji used as a reaction in this server...'

        await message.channel.send(msg)
    

    # gambling machine $$$$$$$$$$$$
    elif message.content == 'h':
        with open('hstats.json') as file:
            hstats = json.load(file)

        guild_id = str(message.guild.id)
        if guild_id not in hstats['gamblecount']:
            hstats['gamblecount'][guild_id] = {}

        # if the member hasn't gambled h's yet, we give 1 for free, so initialize at 0
        if message.author.name not in hstats['gamblecount'][guild_id]:
            hstats['gamblecount'][guild_id][message.author.name] = 0
        else:
            hstats['gamblecount'][guild_id][message.author.name] -= 1

        # if in hs server, if not in h-gambling channel, no chance to return any h's
        if guild_id == "702258603427495956" and str(message.channel.id) != "786810010830897193":
            return

        i = 0
        msg = ''
        while i < 10 and len(msg) == i:
            if random.random() <= 0.50:
                msg += 'h'
            i += 1
        
        # JACKPOTS                   EXPECTED VALUE
        if random.randint(0, 1000) == 1: #0.05
            msg = 'h' * 50
        if random.randint(0, 25000) == 1: #0.004
            msg = 'h' * 100
        if random.randint(0, 500000) == 1: #0.0025
            msg = 'h' * 250
        if random.randint(0, 1000000) == 1: #0.001
            msg = 'h' * 500
        if random.randint(0, 100000000) == 1: #0.00002
            msg = 'h' * 1000
        
        hstats['gamblecount'][guild_id][message.author.name] += len(msg)

        with open('hstats.json', 'w') as file:
            json.dump(hstats, file, indent=4)

        if len(msg) > 0:
            await message.channel.send(msg)
        
    elif message.content == '#hcount':
        with open('hstats.json') as file:
            hstats = json.load(file)
        
        msg = ''
        
        guild_id = str(message.guild.id)

        if guild_id not in hstats['gamblecount']:
            msg = 'h-count has not been initialized for this server'
        elif message.author.name not in hstats['gamblecount'][guild_id]:
            msg = f'{message.author.mention}, you have not gambled any h\'s so far'
        else:
            msg = f'{message.author.mention}, you have {hstats["gamblecount"][guild_id][message.author.name]} h'
            if abs(hstats['gamblecount'][guild_id][message.author.name]) != 1:
                msg += '\'s'
        
        await message.channel.send(msg)
    
    elif message.content == '#hmax':
        with open('hstats.json') as file:
            hstats = json.load(file)
        
        msg = ''
        guild_id = str(message.guild.id)

        if guild_id not in hstats['gamblecount']:
            msg = 'h-count has not been initialized for this server'
        else:
            n = 5  # max number of members to display
            top = sorted(hstats['gamblecount'][guild_id], key=hstats['gamblecount'][guild_id].get, reverse=True)[:n]
            topX = ''
            for i in range(len(top)):
                topX += '\n    ' + str(i + 1) + '. ' + top[i] + ', with ' + str(hstats['gamblecount'][guild_id][top[i]])
            
            msg = f'The h leaderboard: {topX}'
        
        await message.channel.send(msg)
    
    elif message.content.split(' ')[0] == '#hspend':
        valid_amounts = [500, 1000, 2000, 2500, 5000, 10000]
        with open('hstats.json') as file:
            hstats = json.load(file)
        
        msg = ''
        guild_id = str(message.guild.id)

        stramount = message.content.split(' ')[1]
        try:
            amount = int(stramount)
        except ValueError:
            msg = f'{message.author.mention}, the argument after #hspend must be a number corresponding to one of the prize amounts'
        else:
            if amount in valid_amounts:
                if guild_id not in hstats['gamblecount']:
                    msg = 'h-count has not been initialized for this server'
                elif message.author.name not in hstats['gamblecount'][guild_id]:
                    msg = f'{message.author.mention}, you have not gambled any h\'s so far'
                else:
                    if hstats['gamblecount'][guild_id][message.author.name] >= amount:
                        hstats['gamblecount'][guild_id][message.author.name] -= amount
                        msg = f'{message.author.mention}, you have now spent {amount} h\'s - please show this message to an admin to claim your prize!'
                    else:
                        msg = f'{message.author.mention}, you don\'t have {amount} h\'s to spend'
            else:
                msg = 'The amount you spend must be a valid amount, see the h-gambling channel description for info.'
        
        with open('hstats.json', 'w') as file:
            json.dump(hstats, file, indent=4)
        
        await message.channel.send(msg)
    
    elif message.content.split(' ')[0] == '#frogme' or message.content.split(' ')[0] == '#frogtime':
        random_string = str(random.randint(0, 5)) + str(random.randint(1, 4))  # add random number 01-54 for frog choice
        if not os.path.exists('frogs/' + random_string):
            print('generating new frog image')
            url = 'http://www.allaboutfrogs.org/funstuff/random/00'
            url += random_string + '.jpg'
            response = requests.get(url)
            with open('frogs/' + random_string + '.jpg', 'wb') as file:
                file.write(response.content)

        await message.channel.send(file=discord.File('frogs/' + random_string + '.jpg'))
    
    # Half h count on bad words
    badwords = []
    with open('badwords.txt') as file:
        for line in file:
            badwords.append(line.strip())
    if any(word in message.content.split(' ') for word in badwords):
        with open('hstats.json') as file:
            hstats = json.load(file)

        guild_id = str(message.guild.id)
        if guild_id not in hstats['gamblecount']:
            hstats['gamblecount'][guild_id] = {}

        # if the member hasn't gambled h's yet, we just set it at 0
        # otherwise, half their h count
        if message.author.name not in hstats['gamblecount'][guild_id]:
            hstats['gamblecount'][guild_id][message.author.name] = 0
        else:
            hstats['gamblecount'][guild_id][message.author.name] //= 2

        with open('hstats.json', 'w') as file:
            json.dump(hstats, file, indent=4)


token = ''
with open('token.txt') as file:
    token = file.readline()

client.run(token)
