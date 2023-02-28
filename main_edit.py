import asyncio
import json
import os
from time import time
from datetime import datetime, timedelta
from telethon import TelegramClient, events, types, functions
from telethon.tl.functions.messages import ImportChatInviteRequest


class TgClientsBot:
    # можно реализовать в виде класса доступ к аккаунтам, когда какой и тп
    pass


class Sessions:
    @staticmethod
    async def generate_time_for_sessions(none) -> None:
        """
        Генерирует json'ы с временем последнего использования для сессий
        """
        session_names = [f.replace('.session', '') for f in os.listdir('sessions') if f.endswith('.session')]
        for session_name in session_names:
            with open(f'sessions/{session_name}_time.json', 'w') as f:
                time_info = {"session_name": session_name, "used_at": time()}
                json.dump(time_info, f)

    @staticmethod
    def last_used_session(none) -> dict:
        """
        Первый аргумент: имя самой отлежавшейся сессии
        Второй аргумент: список сессий с названием сессии и последним её использованием
        """
        session_names = [f.replace('.session', '') for f in os.listdir('sessions') if f.endswith('.session')]
        sessions_data = []
        for session_name in session_names:
            with open(f'sessions/{session_name}_time.json') as f:
                sessions_data.append(json.load(f))
        with open('shit.json', 'w') as f:
            json.dump(sessions_data, f)
        last_used_session = {}
        min = sessions_data[0]['used_at']
        for i in sessions_data:
            if i['used_at'] <= min:
                min = i['used_at']
                last_used_session = i['session_name']
        with open(f'sessions/{last_used_session}_time.json', 'w') as f:
            time_info = {"session_name": last_used_session, "used_at": time()}
            json.dump(time_info, f)

        with open(f'sessions/{last_used_session}.json') as f:
            session_data = json.load(f)

        data = {
            'api_id': session_data['app_id'],
            'api_hash': session_data['app_hash'],
            'session_name': session_data['phone']
        }
        return data

    def get_client(self) -> TelegramClient:
        pass


class Bot:
    __bot_apikey: str = None
    __app_id = 8
    __app_hash = "7245de8e747a0d6fbe11f7cc14fcc0bb"
    __bot_session = "delete_all_people_in_chat_bot"

    __bot_client: TelegramClient = None

    # bot_client property
    # Get TelegramClient instance or set new one
    @property
    def bot_client(self) -> TelegramClient:
        """
        Get the TelegramClient instance.
        Returns:
            TelegramClient instance
        """
        return self.__bot_client

    @bot_client.setter
    def bot_client(self, client: TelegramClient):
        """
        Set a new TelegramClient instance
        Args:
            client (TelegramClient): The new TelegramClient instance
        Raises:
            Exception: If the provided TelegramClient is not connected.
        """
        if not client.is_connected():
            raise Exception("Connect client first")
        self.__bot_client = client

    # bot_apikey property
    @property
    def bot_apikey(self) -> str:
        """
        Get the API Key
        Returns: 
            str: The API Key.
        """
        return self.__bot_apikey

    @bot_apikey.setter
    def bot_apikey(self, data):
        """
        Set an API Key
        Args:
            data (str): The new API Key.
        Raises:
            ValueError: If the API Key length or syntax is invalid.
        """
        if len(data) < 20 or ":" not in data:
            raise ValueError("Check ApiKey")
        self.__bot_apikey = data

    def only_admin_functions(func):
        """
        Decorator used to check if a user is admin of the current chat. 
        If the sender is not admin, a message will be sent in response informing the user
        """

        async def inner(self, event):
            sender = await event.get_sender()
            if not await self.check_user_admin(event.chat, sender.id):
                await event.reply("Эта команда используется только в чатах или канах")
                return
            return await func(self, event)

        return inner

    def only_groups_functions(func):
        """
        Decorator used to check if a command written in private chat. 
        """

        # Do not allow the command to be used in private chat
        def inner(self, event):
            if event.is_private:
                event.reply(
                    "Эта команда используется только в чатах или канах")
                return
            return func(self, event)

        return inner

    def __init__(self, apikey) -> None:
        self.bot_apikey = apikey
        self.commands: dict = {
            "/start": self.start_command,
            "/panel": self.help_command,
            "/checkAdmin@delete_all_people_in_chat_bot": self.check_admin,
            "/kick_all_users@delete_all_people_in_chat_bot": self.kick_all_users,
            "/delete_all_messages@delete_all_people_in_chat_bot": self.delete_all_messages,
            "/delete_banned_users@delete_all_people_in_chat_bot": self.delete_banned_users,
            "/generate_time_from_sessions": Sessions.generate_time_for_sessions
        }

    # execute() function
    # This function creates a TelegramClient object using the parameters stored as class member. 
    # It then registers an event handler for incoming messages and starts a loop that runs until the client disconnects. 
    async def execute(self):

        t = TelegramClient(self.__bot_session, self.__app_id, self.__app_hash)
        self.bot_client = await t.start(bot_token=self.bot_apikey)

        self.bot_client.add_event_handler(
            self.new_message_event, events.NewMessage(outgoing=False, incoming=True))

        await self.bot_client.run_until_disconnected()

    async def start_command(self, event):
        sender = await event.get_sender()
        await event.reply(f'Ваш username: {sender.username}\nВаш юзер id: {sender.id}')

    @only_groups_functions
    async def help_command(self, event):
        # Вступление в чат
        await event.reply(
            '''
            Бот создан для трёх целей:
            * Удаления всех пользователей (кроме администрации) /kick_all_users
            * Удаления всех сообщений в группе /delete_all_messages
            * Удаление только заблокированных пользователей /delete_banned_users
            
            Чтобы узнать, есть ли у вас права администратора, нажмите /checkAdmin
            '''
        )

    @only_groups_functions
    @only_admin_functions
    async def delete_all_messages(self, event):

        data = Sessions.last_used_session(None)
        client = TelegramClient(
            session=f'sessions/{data["session_name"]}.session',
            api_id=data['api_id'],
            api_hash=data['api_hash']
        )

        try:
            chatid = event.message.chat.id
            expire_date = datetime.now() + timedelta(days=3)
            link = await event.exportChatInviteLink(event.message.chat, expire_date, 3)
            link = link.invite_link.strip('https://t.me/+')
            chat = await event.get_chat(chatid)
            chat_title = chat.title
            client.start()
            try:
                await client(ImportChatInviteRequest(link))
            except:
                pass
            me = await client.get_me()
            await client.send_message(chatid, 'Вступил для администрирования группы')
            await event.promote_chat_member(
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
            print(f'{"_"*10}\n{ex}\n{"_"*10}')
        # получите список всех сообщений в группе
        messages = await client.get_messages(
            event.message.chat.id, limit=None)

        async for message_in_chat in messages:
            await client.delete_messages(event.message.chat.title, [message_in_chat])
        await client(functions.channels.LeaveChannelRequest(event.message.chat.id))

    @only_groups_functions
    @only_admin_functions
    async def delete_banned_users(self, event):
        """
            This function checks for users who have been banned and removed their
            permissions in the chat. It loops through all of the participants in 
            the chat and if a deleted user is found, their view messages permission 
            is set to False.
        """
        entity = event.chat
        # Доработать так как лимит на 10к юзеров проверять есть ли еще кого удалять
        async for x in self.bot_client.iter_participants(entity):
            if x.deleted:
                await self.bot_client.edit_permissions(entity, x, view_messages=False)

    @only_groups_functions
    @only_admin_functions
    async def kick_all_users(self, event):
        """Kick all Non-Admin users from the chat"""
        entity = event.chat
        # Доработать так как лимит на 10к юзеров проверять есть ли еще кого удалять
        async for x in self.bot_client.iter_participants(entity):
            if not isinstance(x.participant, types.ChannelParticipantAdmin) and not isinstance(x.participant,
                                                                                               types.ChannelParticipantCreator):
                await self.bot_client.kick_participant(entity, x)

    @only_groups_functions
    async def check_admin(self, event):
        sender = await event.get_sender()
        is_admin = await self.check_user_admin(event.chat, sender.id)
        text = "Ты админ" if is_admin else "Ты не админ("
        await event.reply(text)

    async def check_user_admin(self, entity, user_id) -> bool:
        # Checks if a user is an admin of the specified entity
        async for x in self.bot_client.iter_participants(entity, filter=types.ChannelParticipantsAdmins()):
            if user_id == x.id:
                return True
        return False

    async def new_message_event(self, event):
        if event.message.message[0] == '/' and len(event.message.message) > 1 \
                and self.commands.get(event.message.message) is None:
            await event.reply("Неизвестная команда")
        elif event.message.message[0] == '/':
            await self.commands.get(event.message.message)(event)
        else:
            pass


async def main():
    bot = Bot("6070517790:AAHAGD4IynHjSDP2sdjZwnEApJV4THPK1o0")
    await bot.execute()


if __name__ == '__main__':
    asyncio.run(main())
