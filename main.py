from aiogram import Bot, Dispatcher, executor, types
from os import system
from datetime import datetime, timedelta

from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest

from userbot import kick_all_users

# system("title Kick User")
print('Бот запущен')

API_TOKEN = '6070517790:AAHAGD4IynHjSDP2sdjZwnEApJV4THPK1o0'

session = '79267450398'
api_id = '2040'
api_hash = 'b18441a1ff607e10a989891a5462e627'


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
client = TelegramClient(session, api_id, api_hash)

@dp.message_handler(commands=['start'])  # ДОРАБОТАТЬ!!!
async def welcome(message: types.Message):
    await message.answer(f'Ваш username: {message.from_user.username}\nВаш юзер id: {message.from_user.id}')
    print(f'username: {message.from_user.username}\nuser_id: {message.from_user.id}')


@dp.message_handler(commands=['help'])  # Работает
async def help(message: types.Message):
    # Вступление в чат
    try:
        chatid = message.chat.id
        expire_date = datetime.now() + timedelta(days=3)
        link = await bot.create_chat_invite_link(chatid, expire_date, 3)
        invite_link = link.invite_link
        print(f'{link=}')
        chat = await bot.get_chat(chatid)
        chat_title = chat.title
        await client.start()
        await client.send_message(chatid, 'Вступил для администрирования группы')
    except: await message.answer('')

    await message.answer(
        '''
        Бот создан для трёх целей:
        * Удаления всех пользователей (кроме администрации) /kick_all_users
        * Удаления всех сообщений в группе /delete_all_messages
        * Удаление только заблокированных пользователей /delete_banned_users
        
        Чтобы узнать, есть ли у вас права администратора, нажмите /checkAdmin
        '''
    )


@dp.message_handler(commands=['checkAdmin'])  # Работает
async def checkAdmin(message: types.Message):
    is_admin = False
    userid = str(message.from_user.id)
    chatid = message.chat.id
    admins = await bot.get_chat_administrators(chatid)
    for user in admins:
        if userid == str(user['user']['id']):
            is_admin = True
            break
    if is_admin:  # юзер админ

        await message.answer('Ты админ')
        print(message.chat.title)


@dp.message_handler(commands=['kick_all_users'])
async def delete_users(message: types.Message):
    print('Команда /kick_all_users прошла')

    is_admin = False
    userid = str(message.from_user.id)
    chatid = message.chat.id
    admins = await bot.get_chat_administrators(chatid)
    for user in admins:
        if userid == str(user['user']['id']):
            is_admin = True
            break
    if is_admin:  # юзер админ
        await message.answer('Начинаю работу...')
        expire_date = datetime.now() + timedelta(days=3)
        link = await bot.create_chat_invite_link(chatid, expire_date, 3)
        invite_link = link.invite_link
        print(f'{link=}')
        chat = await bot.get_chat(chatid)
        chat_title = chat.title
        await kick_all_users(invite_link, chat_title, session, api_id, api_hash)


@dp.message_handler(commands=['delete_all_messages'])  # Работает
async def delete_messages(message: types.Message):
    # получите список всех сообщений в группе
    messages = await client.get_messages(message.chat.title, limit=None)

    # удалите все сообщения в группе
    for message_in_chat in messages:
        await client.delete_messages(message.chat.title, [message_in_chat])


@dp.message_handler(commands=['delete_banned_users'])
async def checkAdmin(message: types.Message):
    pass


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
