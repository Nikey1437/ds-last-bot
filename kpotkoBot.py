import requests
from bs4 import BeautifulSoup
import json
import discord
import asyncio
import time
import config
import datetime
from discord import utils
import socket


socket.getaddrinfo('localhost', 8080)


intents = discord.Intents.all()
client = discord.Client(intents=intents)


#LAST START


def prepareHistory(user_id):
    link = ('https://playmafia.pro/cabinet/get?userId=' + user_id + '&days=0&offset=0&limit=3')  # Делаем реквест на плейку
    responce = requests.get(link).text
    soup = BeautifulSoup(responce, 'lxml')
    block_split = (str(soup).rpartition('['))
    block_split = (block_split[1] + block_split[2])
    block_split = (str(block_split).rpartition(']'))
    result = str(block_split[0] + block_split[1])
    return(json.loads(result))


def prepareGame(game_id):
    link = ('https://playmafia.pro/game-statistics/' + str(game_id)) #делаем реквест на плейку
    try:
        responce = requests.get(link).text
    except socket.gaierror:
        print('[except]ALARM! EXEPTION!')
        asyncio.sleep(600) #ждем 60 сек
        print("[ok]Я проснувся, попробуем еще раз!")
        prepareGame(game_id)
    else:
        soup = BeautifulSoup(responce, 'lxml')
        block = soup.find('div', id='app').find('main', class_='content') #берем нужный нам блок
        block_split = (str(block).split('\n')) #Сплитим блок на строки, чтобы выбрать нужную нам строку
        full_stats = block_split[1]
        game_stats = (full_stats.split('game-data'))
        game_stats = game_stats[1]
        game_stats = game_stats[2: -2]
        return(json.loads(game_stats))


def getInfo(user_id, game_number):
    history = prepareHistory(user_id) #подготавливаем историю игр у чакры
    current_game = (int(game_number)-1) #просто делаем -1, для удобства понимания пользователей и начала работы массива с 1го элемента
    last_game = history[current_game] #Цепляем из истории игр нужную нам игру
    last_game_info = prepareGame(last_game.get('id')) #Подготавливаем из нужной игры стату
    role = last_game.get('role').get('title') #Узнаем роль стримера
    result = last_game.get('result').get('title') #Узнаем результат стримера

    mafia = list()
    for line in (last_game_info['players']): #Раскидываем всех игроков по ролям
        if line.get('role').get('title') == 'Шериф':
            sher = "{player_id}({player_name})".format(player_id=str(line.get('tablePosition')), player_name=str(line.get('username')))
        elif line.get('role').get('title') == 'Мафия':
            mafia.append("{player_id}({player_name})".format(player_id=str(line.get('tablePosition')), player_name=str(line.get('username'))))
        elif line.get('role').get('title') == 'Дон':
            don = "{player_id}({player_name})".format(player_id=str(line.get('tablePosition')), player_name=str(line.get('username')))
            mafia.append("{player_id}({player_name})".format(player_id=str(line.get('tablePosition')), player_name=str(line.get('username'))))


    end_time = last_game.get('date_ends')
    end_time = end_time.split(" ")
    now = datetime.datetime.now()
    date = end_time[0].split("-")
    time = end_time[1].split(":")

    then = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]))
    delta = now - then
    hours = (delta.seconds // 3600)
    sec_to_min = (delta.seconds % 3600)
    minuts = (sec_to_min // 60)
    if (delta.days == 0):
        if (hours == 0):
            info="Игра закончилась {minuts} {minuts_name} назад. \nРезультаты игры:\nРоль стримера: {role}; \nРезультат: {result}! \nМафия: {mafia[0]}, {mafia[1]}, {mafia[2]}; \nДон: {don}; \nШериф: {sher}".format(game_number=game_number ,role=role, result=result, mafia=mafia, don=don, sher=sher, hours=hours, minuts=minuts, minuts_name=name_of_min(minuts) )
        elif (hours > 0):
            info="Игра закончилась {hours} {hours_name} {minuts} {minuts_name} назад. \nРезультаты игры:\nРоль стримера: {role}; \nРезультат: {result}! \nМафия: {mafia[0]}, {mafia[1]}, {mafia[2]}; \nДон: {don}; \nШериф: {sher}".format(game_number=game_number ,role=role, result=result, mafia=mafia, don=don, sher=sher, hours=hours, minuts=minuts, minuts_name=name_of_min(minuts), hours_name=name_of_hour(hours) )
    elif (delta.days > 0):
        info = "Игра закончилась {days} {days_name} {hours} {hours_name} {minuts} {minuts_name} назад. \nРезультаты игры:\nРоль стримера: {role}; \nРезультат: {result}! \nМафия: {mafia[0]}, {mafia[1]}, {mafia[2]}; \nДон: {don}; \nШериф: {sher}".format(
            game_number=game_number, role=role, result=result, mafia=mafia, don=don, sher=sher, hours=hours,
            minuts=minuts, minuts_name=name_of_min(minuts), hours_name=name_of_hour(hours), days=delta.days, days_name=name_of_day(delta.days))
    return info


async def mess_editor(message_idy):
    while True:
        try:
            await message_edit(message_idy)
            await asyncio.sleep(660)
        except ConnectionError:
            print("[except] Да бляяяяя")
            await asyncio.sleep(1200)  # ждем 60 сек
            await message_edit(message_idy)

#SUPPORT FUNCTIONS


@client.event
async def on_message(mess):
    if mess.author == client.user:
        if mess.content.startswith('!start'):
            await mess.delete()
            await mess_editor(
                config.MESSAGE_LAST_INFO_ID)  # После лога сообщение с !ласт автоматически обновляется, message_id в самом верху(сообщение бота в тест серве)
    else:
        if mess.content.startswith('!ласт123'):
            print("Уже не я написал")

            await mess.channel.send(str(getInfo(config.user_id,1)))


async def message_edit(message_idy):
        result = time.localtime(time.time())
        time_str=("Последнее обновление было {day}.{month}.{year} в {hours}:{min} по МСК".format(day=str(result.tm_mday),
                                                                                             month=str(result.tm_mon),
                                                                                             year=str(result.tm_year),
                                                                                             hours=str(result.tm_hour),
                                                                                             min=str(result.tm_min)))
        new_content = str( getInfo(config.user_id, 1))+"\n \n"+str(getInfo(config.user_id, 2))+"\n \n"+str(getInfo(config.user_id, 3)+"\n \n" + time_str) #делаем сообщение из 3 последних игр
        print("[ok]new last content is loaded")
        channel = client.get_channel(config.CHANNEL_LAST_INFO_ID)
        message = await channel.fetch_message(message_idy)
        print("[ok]channel and message are found")
        await message.edit(content=new_content)
        print("[ok]message about last edited with new content")
        print("[ok]time now:"+time.ctime(time.time()))
        print("------------------------------------------")



def name_of_day(day):
    if (int(day)%10==1):
        return("день")
    elif (int(day) % 10 == 2) or (int(day) % 10 == 3) or (int(day) % 10 == 4) :
        return("дня")
    else:
        return("дней")


def name_of_min(min):
    if (int(min) in range(11,20)):
        return("минут")
    elif (int(min)%10 == 1):
        return("минуту")
    elif (int(min) % 10 == 2) or (int(min) % 10 == 3) or (int(min) % 10 == 4) :
        return("минуты")
    else:
        return("минут")


def name_of_hour(hours):
    if (int(hours) == 1) or (int(hours) == 21):
        return("час")
    elif (5 > int(hours) > 1) or (25 > int(hours) > 21):
        return("часа")
    else:
        return("часов")
#LAST END


#ROLE GIVER START


@client.event
async def on_raw_reaction_add(payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if (int(payload.message_id) == config.MESSAGE_ROLE_ID):
        try:
            member = payload.member
            reactedEmojiId = payload.emoji.id
            role = utils.get(message.guild.roles, id=config.ROLES[reactedEmojiId])  # объект выбранной роли (если есть)
            await member.add_roles(role)
            print('[ROLE ok] User {0.display_name} has been granted with role {1.name}'.format(member, role))
        except Exception as e:
            print(repr(e))


@client.event
async def on_raw_reaction_remove(payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if (int(payload.message_id) == config.MESSAGE_ROLE_ID):
        try:
            guild = message.guild
            member = guild.get_member(payload.user_id)
            reactedEmojiId = payload.emoji.id
            role = utils.get(message.guild.roles, id=config.ROLES[reactedEmojiId])
            await member.remove_roles(role)
            print('[ok] User {0.display_name} has been removed with role {1.name}'.format(member, role))
        except Exception as e:
            print(repr(e))


#ROLE GIVER END


@client.event
async def on_ready():
    print("------------------------------------------")
    print('[ok]Logged on as {0}!'.format(client.user))
    channel_admin = client.get_channel(config.channel_admin_id)
    await channel_admin.send("!start")


client.run(config.TOKEN)


