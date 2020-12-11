import discord
import json
import random

client = discord.Client()

@client.event
async def on_raw_reaction_add(payload):
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    guild_id = str(payload.guild_id)
    emoji = str(payload.emoji)

    with open('reaction_map.json') as file:
        reaction_map = json.load(file)

    author = message.author.display_name

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
    
    author = message.author.display_name

    if guild_id in reaction_map and emoji in reaction_map[guild_id] and author in reaction_map[guild_id][emoji]:
        reaction_map[guild_id][emoji][author] -= 1
    
    with open('reaction_map.json', 'w') as file:
        json.dump(reaction_map, file, indent=4)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.split(' ')[0] == '#react':
        msg = ''
        guild_id = str(message.guild.id)
        with open('reaction_map.json') as file:
            reaction_map = json.load(file)

        emoji = message.content.split(' ')[-1]

        if guild_id not in reaction_map:
            msg = 'I haven\'t been initialized in this server...'

        elif emoji in reaction_map[guild_id]:
            top = sorted(reaction_map[guild_id][emoji], key=reaction_map[guild_id][emoji].get, reverse=True)[:5]
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

        else:
            msg = 'I don\'t recognize that command, or I haven\'t seen that emoji used as a reaction in this server...'

        await message.channel.send(msg)

    elif message.content == 'h':
        msg = ''
        if random.randint(0, 1):
            msg = 'h'

        i = 0
        while i < 10 and len(msg) == i + 1:
            if random.randint(0, 1):
                msg += 'h'
            
            i += 1

        if len(msg) > 0:
            await message.channel.send(msg)


token = ''
with open('token.txt') as file:
    token = file.readline()

client.run(token)
