from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest


async def kick_all_users(link, chatname, session, api_id, api_hash, client):
    # Вступление в чат
    try:
        link = link.strip('https://t.me/+')
        await client.start()
        print('Эта хуйня работает (10 строка)')
        # await client(ImportChatInviteRequest(link))
        print('Эта хуйня работает (12 строка)')
    except:
        print('Эта хуйня не работает (18 строка)')

    # Сбор удаленных юзеров

    # deleted_users = []
    async for dialog in client.iter_dialogs():
        if dialog.title == chatname:
            chat_id = dialog.id
            break
    print(f'{chat_id=}')
    participants = client.iter_participants(await client.get_entity(chat_id))
    print(f'Получили юзеров: {(participants)}')
    async for part in participants:
        userid = part.id
        deleted = part.deleted
        # if deleted:
        #     deleted_users.append(userid)

    # Выход из чата

    # a = await client.delete_dialog(chat_id)
    # await client.disconnect()
    # return (deleted_users)