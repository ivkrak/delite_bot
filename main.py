from datetime import datetime, timedelta
from telethon import TelegramClient, functions
from aiogram import Bot, Dispatcher, executor, types
from telethon.tl.functions.messages import ImportChatInviteRequest
import os
from userbot import kick_all_users
from sessions_info import last_used_session, generate_time_for_sessions

print('Бот запущен')

API_TOKEN = '6070517790:AAHAGD4IynHjSDP2sdjZwnEApJV4THPK1o0'

admins_list = [{
    'username': 'ivkrak',
    'user_id': 351162658,
    'ADMIN_username': None,
    'ADMIN_user_id': 1822295368
    }]

session = 'sessions/17825148867.session'
api_id = 8
api_hash = '7245de8e747a0d6fbe11f7cc14fcc0bb'

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
        link = link.invite_link.strip('https://t.me/+')
        chat = await bot.get_chat(chatid)
        chat_title = chat.title
        await client.start()
        try:
            await client(ImportChatInviteRequest(link))
        except:
            await message.answer('Бот готов для администрирования группы')
        me = await client.get_me()
        await client.send_message(chatid, 'Вступил для администрирования группы')
        await bot.promote_chat_member(
            chat_id=chatid,
            user_id=me.id,
            can_manage_chat=True,
            can_delete_messages=True,
            can_pin_messages=True,
            can_change_info=True,
            can_post_messages=True,
            can_edit_messages=True,
            can_restrict_members=True,
            can_promote_members=True
        )
    except Exception as ex:
        await message.answer(ex)

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
    else:
        await message.answer('Ты не админ')


@dp.message_handler(commands=['kick_all_users'])  # не работает
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
        chat = await bot.get_chat(chatid)
        chat_title = chat.title
        await kick_all_users(invite_link, chat_title, session, api_id, api_hash, client)


@dp.message_handler(commands=['delete_all_messages'])  # Готово
async def delete_messages(message: types.Message):
    # получите список всех сообщений в группе
    messages = await client.get_messages(message.chat.title, limit=None)

    # удалите все сообщения в группе
    for message_in_chat in messages:
        # Пробует удалить при помощи бота, при появлении ошибки, удаляет при помощи телетон акка
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=message_in_chat.id)
        except:
            await client.delete_messages(message.chat.title, [message_in_chat])
    await client(functions.channels.LeaveChannelRequest(message.chat.id))


@dp.message_handler(commands=['delete_banned_users'])
async def checkAdmin(message: types.Message):
    pass


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
