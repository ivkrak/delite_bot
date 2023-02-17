from telethon import TelegramClient, sync, functions
import time
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, DeleteChatUserRequest


async def kick_all_users(link, chatname, session, api_id, api_hash):
    # Вступление в чат
    try:
        link = link.split('https://t.me/')[1]
        link = link.replace('+', '')
        client = TelegramClient(
            session=session,
            api_id=api_id,
            api_hash=api_hash
        )
        await client.start()
        return await client(ImportChatInviteRequest(link))
    except:
        pass

    # Сбор удаленных юзеров

    deleted_users = []
    async for dialog in client.iter_dialogs():
        if dialog.title == chatname:
            chat_id = dialog.id
            break
    participants = await client.get_participants(client.get_entity(chat_id))
    print('Получили юзеров: ' + str(len(participants)))
    for part in participants:
        userid = part.id
        deleted = part.deleted
        if deleted:
            deleted_users.append(userid)

    # Выход из чата

    a = await client.delete_dialog(chat_id)
    await client.disconnect()
    # return (deleted_users)


async def delete_all_messages(link, chatname, session, api_id, api_hash):
    """

    :param link:
    :param chatname:
    :param session:
    :param api_id:
    :param api_hash:
    :return:
    """

    # Вступление в чат
    try:
        link = link.split('https://t.me/')[1]
        link = link.replace('+', '')
        client = TelegramClient(
            session=session,
            api_id=api_id,
            api_hash=api_hash
        )
        await client.start()
        return await client(ImportChatInviteRequest(link))
    except:
        pass
