from aiogram import Bot, Dispatcher, executor, types
from os import system
from datetime import datetime, timedelta
from userbot import kick_deleted

system("title Kick User")
print('Kick User')

API_TOKEN = '6070517790:AAHAGD4IynHjSDP2sdjZwnEApJV4THPK1o0'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
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


@dp.message_handler(lambda message: message.text and 'kick' in message.text.lower())
async def send_welcome(message: types.Message):
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
        deleted_users = await kick_deleted(invite_link, chat_title)
        try:
            print('Получили удаленных юзеров: ' + str(len(deleted_users)))
        except: print(deleted_users)
        if len(deleted_users) == 0:
            await message.answer('Удаленных пользователей в этом чате не найдено')
        else:
            await message.answer(
                'Найдено удаленных пользователей в этом чате: ' + str(len(deleted_users)) + '.\nНачинаю кикать.')
        for id in deleted_users:
            print('Кикаем ID')
            await bot.kick_chat_member(chatid, id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
