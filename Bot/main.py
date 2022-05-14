import discord
from discord.ext import commands
import random
import time
import json
import requests
from credits import *
import datetime
import Shifr

bot = commands.Bot(command_prefix=settings['prefix'])

bot_start_time = time.time()  # start


def write_to_log(log):
    wall = open('log.txt', 'a')
    wall.write(str(log + '\n'))
    wall.close()


def write_stats():
    current_datetime = datetime.datetime.now()
    wall = open('stats.txt', 'a')
    wall.write(str(f'|Day {current_datetime.day} {str(current_datetime.hour)} : {str(current_datetime.minute)} : {str(current_datetime.second)}|\n  Starting...\n\n'))
    wall.close()


class MyClient(discord.Client):
    async def on_ready(self):
        print('Зашол как {0}!'.format(self.user))

    async def on_message(self, message):
        print('Сообщение от {0.author}: {0.content}'.format(message))


@bot.command()  # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def hello(ctx):  # Создаём функцию и передаём аргумент ctx.
    start_time = time.time()  # start
    author = ctx.message.author  # Объявляем переменную author и записываем туда информацию об авторе.
    await ctx.send(f'Привет! Команды: {bot_prefix}CMD_cammands')  # Выводим сообщение с упоминанием автора, обращаясь к переменной author.
    end_time = time.time()  # end
    print("Время hello: ", end_time - start_time, "s")  # q
    write_to_log(f"{ctx.message.author}:hello")


# список слов, из которого будем брать загадываемое
words = ['ПРИКОЛ', 'МЕМБРАНА', 'КОДЛЭНД', 'МАШИНА', 'БЕРЁЗА', 'ЖИЗНЬ', 'СЕРДЦЕ', 'ШУТКА']
members = []  # Список игроков
lives = 0  # кол-во жизней
running = 'none'
current_player = 0  # номер текущего игрока
word = []  # Слово для отгадывания будет храниться в виде списка
display_word = []  # Слово, которое нужно будет отображать в чате (будет заполнено ------)
original_word = ''  # Загаданное слово в виде строки

class games:
    class visel:
        # Хэндлер команды !start - эта команда позволяет начать новую игру
        @bot.command(name='startg')
        async def startg(ctx):
            global running, members, lives
            # Если игра уже начата (то есть не 'none' - отправляем соответствующее сообщение. Если начата - добавляем автора в список игроков и отправляем в чат сообщение
            if running != 'none':
                await ctx.send('Игра уже началась! Чтобы завершить игру - введите команду !stopg')
            else:
                running = 'joining'
                members.append(ctx.author.name)
                lives = 7
                await ctx.send('Игра началась! Пишите !joing, если хотите присоединиться.')

        # Хэндлер команды !join - эта команда позволяет присоединиться к игре
        @bot.command(name='joing')
        async def joing(ctx):
            global members
            # Если игра не в none - предлагаем начать игру
            if running == 'none':
                await ctx.send('Пока некуда присоединяться. Введите !startg, чтобы начать игру.')
            # Если игра в joining - проверяем, не зарегистрирован ли уже игрок
            elif running == 'joining':
                if ctx.author.name not in members:
                    members.append(ctx.author.name)
                    await ctx.send('Вы в игре!')
                else:
                    await ctx.send('Вы уже в игре!')
            # Если игра в running - присоединиться уже нельзя
            else:
                await ctx.send('Игра уже начата :(')

        # Хэндлер команды !play - эта команда позволяет запустить игру, когда все пользователи присоединились
        @bot.command(name='playg')
        async def playg(ctx):
            global running, word, display_word, original_word, a, words
            a = ""
            original_word = ""
            display_word = []
            word = []
            # Если игра в none - предлагаем начать игру
            if running == 'none':
                await ctx.send('Игра пока не началась. Введите !startg, чтобы начать')
            # Если игра в joining - выбираем слово и начинаем игру
            elif running == 'joining':
                running = 'running'
                a = random.choice(words)  # Выбираем слово из списка (строка)
                original_word = a  # Сохраняем выбранное слово в виде строки
                print(original_word)
                # Формируем список word из выбранной строки, а display_word заполняем прочерками
                for i in a:
                    word.append(i)
                    display_word.append('-')
                # Отправляем сообщение с информацией об игре: кто ходит, как ходить, и загаданное слово.
                await ctx.send('Игра запущена! Загаданное слово: ' + ''.join(display_word) + ' Первым ходит ' + str(members[current_player]) + '. Введите команду !guess и букву.', file=discord.File(fr'C:\Users\alexz\PycharmProjects\Discord\Photos\{0}.png'))
            # Если игра уже running - сообщаем, что игра уже идёт, кто ходит, как ходить и загаданное слово
            else:
                await ctx.send('Игра запущена! Первым ходит ' + str(members[current_player]) + '. Введите команду !guess и букву. \nЗагаданное слово: ' + ''.join(display_word), file=discord.File(fr'C:\Users\alexz\PycharmProjects\Discord\Photos\{0}.png'))

        @bot.command(name='guess')
        async def guess(ctx, letter):
            global display_word, word, current_player, running, lives, original_word, a
            letter = letter.upper()  # Слова хранятся в uppercase, поэтому букву тоже переводим в upper
            if running == 'running':  # Проверяем, если running
                if ctx.author.name in members:  # Проверяем, есть ли игрок в списке
                    if ctx.author.name == members[
                        current_player]:  # Проверяем, совпадает ли игрок, отправивший команду, с текущим игроком
                        if letter in word:  # Если игрок есть в списке и ход у него - проверяем, есть ли его буква в списке word
                            while letter in word:  # До тех пор пока она есть - меняем первое вхождение этой буквы в word на '*', а в display_word - по тому же индексу заменяем прочерк на букву
                                display_word[word.index(letter)] = letter
                                word[word.index(letter)] = '*'
                            await ctx.send('Есть такая буква!')
                        else:  # Если буквы не оказалось в списке - вычитаем жизнь
                            lives -= 1
                            await ctx.send('Такой буквы нет :(')
                        # Увеличиваем номер игрока, а если он больше чем индекс последнего элемента списка - обнуляем, чтобы начать новый круг
                        if current_player == len(members) - 1:
                            current_player = 0
                        else:
                            current_player += 1
                    else:  # Если ход принадлежит другому игроку - сообщаем об этом
                        await ctx.send('Ошибка! Сейчас ходит ' + str(members[current_player]))
                else:  # Если игрока нет в списке игроков - сообщаем об этом
                    await ctx.send('Ошибка! Вы не зарегистрировались :(')
                if word.count('*') == len(
                        word):  # Если каждый элемент списка это '*' - значит слово отгадано. Сообщаем об этом и вызываем init(), обнуляющий все нужные значения
                    await ctx.send('Слово отгадано, игра окончена. Чтобы начать новую - введите !startg.')
                    running = 'none'
                elif lives <= 0:  # Если кончились жизни - игра окончена. Сообщаем об этом и обнуляем все нужные значения с помощью init()
                    await ctx.send('Слово не отгадано, а жизни кончились. Игра окончена. Чтобы начать новую - введите !startg.', file=discord.File(fr'C:\Users\alexz\PycharmProjects\Discord\Photos\{7}.png'))
                    running = 'none'
                else:  # Если слово не отгадано и жизни есть - выводим информацию о загаданном слове и продолжаем игру
                    if str(lives) == "7":
                        ng = 0
                    elif str(lives) == "6":
                        ng = 1
                    elif str(lives) == "5":
                        ng = 2
                    elif str(lives) == "4":
                        ng = 3
                    elif str(lives) == "3":
                        ng = 4
                    elif str(lives) == "2":
                        ng = 5
                    elif str(lives) == "1":
                        ng = 6
                    elif str(lives) == "0":
                        ng = 7
                    await ctx.send('Загаданное слово: ' + ' '.join(display_word) + '. Сейчас ходит ' + members[current_player] + '. Жизней осталось: ' + str(lives),file=discord.File(fr'C:\Users\alexz\PycharmProjects\Discord\Photos\{ng}.png'))
            # Если игра в none - предлагаем начать новую
            elif running == 'none':
                await ctx.send('Игра пока не началась. Введите !startg, чтобы начать')
            # Если игра в joining - сообщаем, что ждем пока все подключатся
            else:
                await ctx.send('Игра пока не запущена, ждем пока все подключатся. Чтобы начать игру - введите !playg')

        @bot.command(name='helpmeg')
        async def helpmeg(ctx):
            send = '''Приветствуем вас! У вас есть возможность сыграть в игру виселица.'''

            sendf = '''Правила довольно просты: 
Набирается команда игроков, которая поочередно дает ответы с вариантами пропущенных букв.\n 
*Каждый неправильный ответ приближает команду к виселице :)*\n\n
Доступны команды:
    !startg - запустить игру 
    !joing - присоединиться к игре 
    !playg - начать раунд'''

            embed = discord.Embed(title=send, color=0xff99)
            embed.set_footer(text=sendf)
            await ctx.send(embed=embed)

        @bot.command(name='stopg')
        async def stopg(ctx):
            global running
            await ctx.send("Игра успешно закончена.\n Введите !startg, чтобы начать новую игру.")
            running = None
    class suefa:
        @bot.command()
        async def suefa(ctx, vibor):
            SUEF = random.randint(1,3)
            SUEFA = vibor
            if vibor.lower() == "камень":
                SUEFA = 1
            elif vibor.lower() == "ножницы":
                SUEFA = 2
            elif vibor.lower() == "бумага":
                SUEFA = 3
            else:
                await ctx.send("Выбрать можно только: Камень; Ножницы; Бумага.")
            if SUEF == SUEFA:
                await ctx.send("Ничья")
            elif SUEFA == 1 and SUEF == 2:
                await ctx.send("Вы выиграли")
            elif SUEFA == 2 and SUEF == 1:
                await ctx.send("Вы проиграли")
            elif SUEFA == 1 and SUEF == 3:
                await ctx.send("Вы проиграли")
            elif SUEFA == 3 and SUEF == 1:
                await ctx.send("Вы выиграли")
            elif SUEFA == 2 and SUEF == 3:
                await ctx.send("Вы выиграли")
            elif SUEFA == 3 and SUEF == 2:
                await ctx.send("Вы проиграли")


@bot.command()
async def start(ctx):
    start_time = time.time()  # start

    await ctx.send(f"Привет, я бот созданный Александром!\n Команды: {bot_prefix}CMD_help")

    end_time = time.time()  # end
    print("Время start: ", end_time - start_time, "s")  # q
    write_to_log(f"{ctx.message.author}:start")


@bot.command()
async def fox(ctx):
    start_time = time.time()  # start
    response = requests.get('https://some-random-api.ml/img/fox')  # Get-запрос
    json_data = json.loads(response.text)  # Извлекаем JSON

    embed = discord.Embed(color=0xff9900, title='Рандомная лиса')  # Создание Embed'a
    embed.set_image(url=json_data['link'])  # Устанавливаем картинку Embed'a
    await ctx.send(embed=embed)  # Отправляем Embed
    end_time = time.time()  # end
    print("Время fox: ", end_time - start_time, "s")  # q
    write_to_log(f"{ctx.message.author}:fox")


@bot.command()
async def cat(ctx):
    start_time = time.time()  # start
    response = requests.get('https://some-random-api.ml/img/cat')  # Get-запрос
    json_data = json.loads(response.text)  # Извлекаем JSON

    embed = discord.Embed(color=0xff9900, title='Рандомный кот')  # Создание Embed'a
    embed.set_image(url=json_data['link'])  # Устанавливаем картинку Embed'a
    await ctx.send(embed=embed)  # Отправляем Embed
    end_time = time.time()  # end
    print("Время cat: ", end_time - start_time, "s")  # q
    write_to_log(f"{ctx.message.author}:cat")


@bot.command()
async def dog(ctx):
    start_time = time.time()  # start
    response = requests.get('https://some-random-api.ml/img/dog')  # Get-запрос
    json_data = json.loads(response.text)  # Извлекаем JSON

    embed = discord.Embed(color=0xff9900, title='Рандомная собака')  # Создание Embed'a
    embed.set_image(url=json_data['link'])  # Устанавливаем картинку Embed'a
    await ctx.send(embed=embed)  # Отправляем Embed
    end_time = time.time()  # end
    print("Время dog: ", end_time - start_time, "s")  # q
    write_to_log(f"{ctx.message.author}:dog")


@bot.command()
async def panda(ctx):
    start_time = time.time()  # start
    response = requests.get('https://some-random-api.ml/img/panda')  # Get-запрос
    json_data = json.loads(response.text)  # Извлекаем JSON

    embed = discord.Embed(color=0xff9900, title='Рандомная панда')  # Создание Embed'a
    embed.set_image(url=json_data['link'])  # Устанавливаем картинку Embed'a
    await ctx.send(embed=embed)  # Отправляем Embed
    end_time = time.time()  # end
    print("Время panda: ", end_time - start_time, "s")  # q
    write_to_log(f"{ctx.message.author}:panda")


@bot.command()
async def bird(ctx):
    start_time = time.time()  # start
    response = requests.get('https://some-random-api.ml/img/bird')  # Get-запрос
    json_data = json.loads(response.text)  # Извлекаем JSON

    embed = discord.Embed(color=0xff9900, title='Рандомный попугай')  # Создание Embed'a
    embed.set_image(url=json_data['link'])  # Устанавливаем картинку Embed'a
    await ctx.send(embed=embed)  # Отправляем Embed
    end_time = time.time()  # end
    print("Время bird: ", end_time - start_time, "s")  # q
    write_to_log(f"{ctx.message.author}:bird")


@bot.command()
async def coala(ctx):
    start_time = time.time()  # start
    response = requests.get('https://some-random-api.ml/img/coala')  # Get-запрос
    json_data = json.loads(response.text)  # Извлекаем JSON

    embed = discord.Embed(color=0xff9900, title='Рандомная коала')  # Создание Embed'a
    embed.set_image(url=json_data['link'])  # Устанавливаем картинку Embed'a
    await ctx.send(embed=embed)  # Отправляем Embed
    end_time = time.time()  # end
    print("Время coala: ", end_time - start_time, "s")
    write_to_log(f"{ctx.message.author}:coala")


@bot.command()  # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def AZ_help(ctx):  # Создаём функцию и передаём аргумент ctx.
    start_time = time.time()  # start
    author = ctx.message.author  # Объявляем переменную author и записываем туда информацию об авторе.
    await ctx.send(
        f'Привет, {author.mention}! Вот список команд: ')  # Выводим сообщение с упоминанием автора, обращаясь к переменной author.
    await ctx.send(f'{bot_prefix}AZ_help')
    time.sleep(1)
    await ctx.send(f'{bot_prefix}hello')
    time.sleep(1)
    await ctx.send(f'{bot_prefix}CMD_help')
    time.sleep(1)
    await ctx.send(f'{bot_prefix}spam')
    time.sleep(1)
    await ctx.send(f'{bot_prefix}fox')
    time.sleep(1)
    await ctx.send(f'{bot_prefix}cat')
    time.sleep(1)
    await ctx.send(f'{bot_prefix}dog')
    time.sleep(1)
    await ctx.send(f'{bot_prefix}panda')
    time.sleep(1)
    await ctx.send(f'{bot_prefix}bird')
    time.sleep(1)
    await ctx.send(f'{bot_prefix}helpmeg')
    end_time = time.time()  # end
    print("Время AZ_help: ", end_time - start_time, "s")  # q
    write_to_log(f"{ctx.message.author}:AZ_help")


@bot.command()  # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def spam(ctx):  # Создаём функцию и передаём аргумент ctx.
    start_time = time.time()  # start
    author = ctx.message.author  # Объявляем переменную author и записываем туда информацию об авторе.
    await ctx.send(f'Спам через')  # Выводим сообщение с упоминанием автора, обращаясь к переменной author.
    await ctx.send(f'{author.mention} 5...')
    time.sleep(1)
    await ctx.send(f'{author.mention} 4...')
    time.sleep(1)
    await ctx.send(f'{author.mention} 3...')
    time.sleep(1)
    await ctx.send(f'{author.mention} 2...')
    time.sleep(1)
    await ctx.send(f'{author.mention} 1...')
    time.sleep(1)
    for i in range(0, 2):
        await ctx.send(f'@everyone  СПААААМ')
        await ctx.send(f'@everyone  СПААААМ')
        await ctx.send(f'@everyone  СПААААМ')
    end_time = time.time()  # end
    print("Время spam: ", end_time - start_time, "s")  # q
    write_to_log(f"{ctx.message.author}:spam")


@bot.command()  # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def CMD_help(ctx):  # Создаём функцию и передаём аргумент ctx.
    start_time = time.time()  # start
    embed = discord.Embed(color=0xff9900, title=f'''Вот списиок команд:''')
    embed.set_footer(text=f'''
    {bot_prefix}CMD_help - Команды
    {bot_prefix}hello - Приветик от бота
    {bot_prefix}spam - Немного спама.
    {bot_prefix}fox - ЛИСИЧКААА!!
    {bot_prefix}cat - КОТИИК!!
    {bot_prefix}dog - СОБАЧКАА!!
    {bot_prefix}panda - ПАНДАЧКАА!!
    {bot_prefix}bird - ПТИЧКАА!
    {bot_prefix}helpmeg - Виселица
    {bot_prefix}shifr что шифровать - Шифровальщик''')  # Создание Embed'a
    await ctx.send(f'Дароу', embed=embed)  # Отправляем Embed
    end_time = time.time()  # end
    print("Время CMD_help: ", end_time - start_time, "s")  # q
    write_to_log(f"{ctx.message.author}:CMD_help")


@bot.command()  # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def DONT_COPY6579589(ctx):  # Создаём функцию и передаём аргумент ctx.
    start_time = time.time()  # start
    author = ctx.message.author  # Объявляем переменную author и записываем туда информацию об авторе.
    await ctx.send(f'Спам через')  # Выводим сообщение с упоминанием автора, обращаясь к переменной author.
    await ctx.send(f'{author.mention} 5...')
    time.sleep(1)
    await ctx.send(f'{author.mention} 4...')
    time.sleep(1)
    await ctx.send(f'{author.mention} 3...')
    time.sleep(1)
    await ctx.send(f'{author.mention} 2...')
    time.sleep(1)
    await ctx.send(f'{author.mention} 1...')
    time.sleep(1)
    time_running = 0
    running = True
    while running:
        run = input("Run")
        if run == "":
            running = False
        if run != "":
            pass
        for i in range(0, 1):
            time_running = start_time - time.time()
            time_running = -time_running
            print("spamming:", time_running)
            await ctx.send(f'@everyone  СПААААМ')
            end_time = time.time()  # end
    print("Время spam: ", end_time - start_time, "s")  # q
    write_to_log(f"{ctx.message.author}:Mega spam")


@bot.command()  # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def rules(ctx):  # Создаём функцию и передаём аргумент ctx.
    start_time = time.time()  # start
    text = f'''

        1. Помогать союзникам(Не обязательно)
        2. Не оскорблять союзников просто так(По делу можно)
        3. Упоминание родителей карается киком из клана и баном на сервере в дискорде
        4. Подчиняться страшим по званию нужно обязательно
        5. Не скипать или стопать чужую музыку (Искл больше 10 минут)
        7. Включайте музыку в канале
        8. Ссылки запрещены
        9. Приятно проводить время
        10. Не включать громкую музыку!
        11.@everyone @AlexZapl НЕ РАЗДАЁТ РОЛИ!!!
        (Возможны изменения)

        '''
    embed = discord.Embed(title="Information", color=0x9208ea)
    embed.set_footer(text=text)
    await ctx.send("https://media.discordapp.net/attachments/760190442858872854/911696733849931786/image0-1-1-2.gif")
    await ctx.send(embed=embed)
    await ctx.send("https://media.discordapp.net/attachments/760190442858872854/911696733849931786/image0-1-1-2.gif")
    await ctx.send("||@everyone|| ||@here||")
    end_time = time.time()  # end
    print("Время rules: ", end_time - start_time, "s")  # q
    write_to_log(f"{ctx.message.author}:rules")


@bot.command()  # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def annouce(ctx, text1="", text2="", text3="", text4="", text5="", text6="", text7="", text8="", text9=""):
    start_time = time.time()  # start
    text = text1 + " " + text2 + " " + text3 + " " + text4 + " " + text5 + " " + text6 + " " + text7 + " " + text8 + " " + text9
    embed = discord.Embed(title="Новость!", color=0x9208ea)
    embed.set_footer(text=text)
    await ctx.send(embed=embed)
    await ctx.send("||@everyone|| ||@here||")
    end_time = time.time()  # end
    print("Время annouce: ", end_time - start_time, "s")  # q
    write_to_log(f"{ctx.message.author}:annouce {text}")


@bot.command()  # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def shifr(ctx, self):  # Создаём функцию и передаём аргумент ctx.
    Rev = Shifr.DC.runRev(self)
    NotRev = Shifr.DC.runNotRev(self)
    NotSh = Shifr.DC.runNotSh(self)
    time.sleep(0.4)
    embed = discord.Embed(title="Шишр готов!", color=0x9208ea)
    embed.set_footer(text=f"{Rev} \n{NotRev} \n{NotSh}")

    await ctx.send(embed=embed)

@bot.command()  # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def MOD_help(ctx):  # Создаём функцию и передаём аргумент ctx.
    start_time = time.time()  # start
    embed = discord.Embed(color=0xff9900, title=f'''Вот списиок команд для модератора.:
    {bot_prefix}rules - Правила.
    {bot_prefix}annouce сообщение - Оповещение серверу.''')  # Создание Embed'a
    await ctx.send(embed=embed)  # Отправляем Embed
    end_time = time.time()  # end
    print("Время MOD_help: ", end_time - start_time, "s")  # q
    write_to_log(f"{ctx.message.author}:MOD_help")
bot_end_time = time.time()  # end
print("Время загрузки: ", bot_end_time - bot_start_time, "s")  # q

write_stats()

bot.run(settings['token'])  # Обращаемся к словарю settings с ключом token, для получения токена
