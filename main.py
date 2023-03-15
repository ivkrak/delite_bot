import asyncio
import json
import os
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from time import time
from loguru import logger
from telethon import TelegramClient, events, types, functions, errors
from telethon.tl.functions.channels import GetFullChannelRequest

logger.add(
    'errors.log',
    format='{time} {level} {message}',
    level='DEBUG'
)
logger.info('Бот запущен')


class Sessions:
    @logger.catch
    @staticmethod
    async def generate_time_for_sessions(none) -> None:
        """
        Генерирует json (time.json) с временем последнего использования для сессий
        """
        if not os.path.isfile('sessions/time.json'):
            open('sessions/time.json', 'w').close()
        session_names = [f.replace('.session', '') for f in os.listdir(
            'sessions') if f.endswith('.session')]
        sessions_time = {str(session_name): time() for session_name in session_names}
        with open('sessions/time.json', 'w') as f:
            json.dump(sessions_time, f)

    FILENAME = "sessions/time.json"
    LOCKER = Lock()

    @logger.catch
    @staticmethod
    def prepare_group(group: str) -> tuple[bool, str]:
        """Clean entity from url

        Args:
            group (str): chat url

        Returns:
            tuple[bool, str]: private or public link, clean link
        """
        group = group.replace("/+", "/joinchat/")
        isPrivate = 'joinchat/' in group
        preaperGroupVal = group.replace('https://', '').replace("http://", "").replace(
            't.me/', '').replace('joinchat/', '').replace('@', '').replace('/', '')
        return isPrivate, preaperGroupVal

    @logger.catch
    @staticmethod
    async def join_to_chat(link: str, account: TelegramClient):
        """ raise  (NextRecepient,  NextAccount)"""
        private, cleanGroup = Sessions.prepare_group(link)
        chatEntity = None
        try:
            if not private:
                chatEntity = await account(functions.channels.JoinChannelRequest(cleanGroup))
            else:
                chatEntity = await account(functions.messages.ImportChatInviteRequest(cleanGroup))
        except errors.UserAlreadyParticipantError:
            chatEntity = await account(functions.messages.CheckChatInviteRequest(hash=cleanGroup))

        except (errors.UserDeactivatedBanError):
            return None
        except errors.ChannelsTooMuchError as e:
            return None
        except (errors.ChatIdInvalidError):
            return None
        except errors.ChannelPrivateError:
            return None
        except (errors.InviteHashEmptyError, errors.InviteHashExpiredError, errors.InviteHashInvalidError):
            return None
        except (errors.FloodWaitError, errors.PeerFloodError, errors.FloodError) as err:
            return None

        except (errors.UsernameInvalidError, ValueError):
            return None
        except (errors.UserDeactivatedError, errors.AuthKeyDuplicatedError, errors.UserDeactivatedBanError) as err:
            return None
        except Exception as e:
            return None

        resultEntity = None
        if isinstance(chatEntity, types.ChatInviteAlready):
            resultEntity = chatEntity.chat

        elif isinstance(chatEntity, types.Updates) or (
                isinstance(chatEntity, types.messages.ChatFull) and not isinstance(chatEntity,
                                                                                   types.ChatInviteAlready)):
            resultEntity = chatEntity.chats[0]

        return resultEntity

    @logger.catch
    @staticmethod
    def get_telegram_client() -> TelegramClient:
        data = Sessions.last_used_session()
        return TelegramClient(session=data['session_name'],
                              api_id=data['api_id'],
                              api_hash=data['api_hash'])

    @logger.catch
    @staticmethod
    async def connect_account(self) -> TelegramClient:
        data = Sessions.last_used_session()
        if data is None:
            admins_list = [351162658, 1822295368]  # мой ID,  ID аккаунта Вани
            for user_id in admins_list:
                await self.bot_client.send_message(user_id, 'Аккаунты закончились')
        phone = f"sessions//{data['session_name']}"
        client = TelegramClient(session=phone,
                                api_id=data['api_id'],
                                api_hash=data['api_hash'])
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            Sessions.delete_account_from_list(data['session_name'])
            return await Sessions.connect_account(self)
        return client

    @logger.catch
    @staticmethod
    def delete_account_from_list(phone):
        Sessions.LOCKER.acquire()
        try:
            with open(Sessions.FILENAME, "r") as f:
                data = json.load(f)
            if data.get(phone) is not None:
                del data[phone]
            with open(Sessions.FILENAME, "w") as f:
                json.dump(data, f)
            try:
                os.remove(f"sessions//{phone}.json")
                os.remove(f"sessions//{phone}.session")
            except Exception as e:
                logger.error(e)
        finally:
            Sessions.LOCKER.release()

    @logger.catch
    @staticmethod
    def get_account_alive(timespan):
        dt_object = datetime.fromtimestamp(timespan)
        return datetime.now() - dt_object

    @logger.catch
    @staticmethod
    def last_used_session() -> dict:
        Sessions.LOCKER.acquire()
        session_names = [f.name.replace('.session', '')
                         for f in Path('sessions').glob("*.session")]
        if len(session_names) == 0:
            return None
        sessions_data = {}
        if not os.path.exists(Sessions.FILENAME):
            for x in session_names:
                sessions_data[x] = int(time())
            with open(Sessions.FILENAME, "w") as f:
                json.dump(sessions_data, f)
        else:
            with open(Sessions.FILENAME, "r") as f:
                sessions_data = json.load(f)
        try:
            min_phone = list(sessions_data.keys())[0]
            min_value = sessions_data[min_phone]
            for x, y in sessions_data.items():
                if min_value > y:
                    min_phone = x
                    min_value = y

            sessions_data[min_phone] = int(time())
            with open(Sessions.FILENAME, "w") as f:
                json.dump(sessions_data, f)

            with open(f'sessions/{min_phone}.json') as f:
                session_json = json.load(f)

            data = {
                'api_id': session_json['app_id'],
                'api_hash': session_json['app_hash'],
                'session_name': session_json['phone']
            }
            return data
        except Exception as e:
            logger.exception(e)
        finally:
            Sessions.LOCKER.release()


class Bot:
    __bot_apikey: str = None
    __app_id = 8
    __app_hash = "7245de8e747a0d6fbe11f7cc14fcc0bb"
    __bot_session = "delete_all_people_in_chat_bot"
    __admins_user_ids__ = [351162658, 1822295368]
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

    @logger.catch
    def only_admin_functions(func):
        """
        Decorator used to check if a user is admin of the current chat. 
        If the sender is not admin, a message will be sent in response informing the user
        """

        @logger.catch
        async def inner(self, event):
            sender = await event.get_sender()
            if not await self.check_user_admin(event.chat, sender.id):
                await event.reply("Эта команда используется только в чатах или канах")
                return
            return await func(self, event)

        return inner

    @logger.catch
    def only_groups_functions(func):
        """
        Decorator used to check if a command written in private chat. 
        """

        # Do not allow the command to be used in private chat
        def inner(self, event):
            if event.is_private:
                return
            return func(self, event)

        return inner

    def __init__(self, apikey) -> None:
        self.bot_apikey = apikey
        self.bot_client_username = ""
        self.commands: dict = {
            "/start": self.start_command,
            "/panel": self.help_command,
            "/checkadmin": self.check_admin,
            "/kick_all_users": self.kick_all_users,
            "/delete_all_messages": self.delete_all_messages,
            "/delete_banned_users": self.delete_banned_users,
            "/generate_time_from_sessions": Sessions.generate_time_for_sessions
        }

    # execute() function
    # This function creates a TelegramClient object using the parameters stored as class member.
    # It then registers an event handler for incoming messages and starts a loop that runs until the client disconnects.
    async def execute(self):

        t = TelegramClient(self.__bot_session, self.__app_id, self.__app_hash)
        self.bot_client = await t.start(bot_token=self.bot_apikey)
        bot_ent = await t.get_me()
        self.bot_client_username = bot_ent.username

        self.bot_client.add_event_handler(
            self.new_message_event, events.NewMessage(outgoing=False, incoming=True))

        await self.bot_client.run_until_disconnected()

    async def start_command(self, event):
        with open('databases/ids.json', 'r') as f:
            data = json.load(f)
        data["chat_id"].append(event.message.chat.id)
        with open('databases/ids.json', 'w') as f:
            json.dump(data, f)
        await event.reply(
            'Чтобы начать использовать бота, добавьте его в группу и выдайте ему все права администратора')


    @logger.catch
    @only_groups_functions
    async def help_command(self, event):
        # Вступление в чат
        await event.reply(
            '''
            Бот создан для трёх целей:
            * Удаления всех пользователей (кроме администрации) /kick_all_users
            * Удаления всех сообщений в группе /delete_all_messages
            * Удаление только заблокированных пользователей /delete_banned_users
            
            Чтобы узнать, есть ли у вас права администратора, нажмите /checkadmin
            '''
        )

    async def get_chat_link(self, chat) -> str:
        if chat.username is not None:
            return chat.username
        else:
            expire_date = datetime.now() + timedelta(days=3)
            link = await self.bot_client(
                functions.messages.ExportChatInviteRequest(chat, True, False, expire_date, 3, "our bot"))
            return link.link

    @logger.catch
    @only_groups_functions
    @only_admin_functions
    async def delete_all_messages(self, event):

        client = await Sessions.connect_account(self)

        try:
            chat = event.chat
            link = await self.get_chat_link(event.chat)

            try:
                result = await Sessions.join_to_chat(link, client)
                if result is None:
                    raise Exception("ALERT")
            except Exception as e:
                logger.exception(e)
            await client.send_message(self.bot_client_username, "/start")
            me = await client.get_me()
            result = await self.bot_client(functions.channels.EditAdminRequest(
                channel=chat.id,
                user_id=me.id,
                admin_rights=types.ChatAdminRights(
                    delete_messages=True
                ),
                rank=""
            ))

        except Exception as e:
            logger.debug(e)
        # получите список всех сообщений в группе
        try:
            while True:
                list_msg = await client.get_messages(chat.id, limit=100)
                if len(list_msg) <= 3:
                    break
                msg_to_delete = [x.id for x in list_msg]
                await client.delete_messages(chat.id, msg_to_delete, revoke=True)
        except Exception as e:
            logger.exception(e)

        try:
            await client(functions.channels.LeaveChannelRequest(chat.id))
        except Exception as e:
            logger.exception(e)

    @logger.catch
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
        not_admin_users = 1
        while not_admin_users > 0:
            async for x in self.bot_client.iter_participants(entity):
                if x.deleted:
                    await self.bot_client.edit_permissions(entity, x, view_messages=False)
            chat_info = await self.bot_client(functions.channels.GetFullChannelRequest(entity))
            admins = chat_info.full_chat.participants_count
            all_users = chat_info.full_chat.admins_count
            not_admin_users = all_users - admins
            await asyncio.sleep(60)

            # logger.debug(f'{admins=}')
            # logger.debug(f'{all_users=}')
            # logger.debug(f'{not_admin_users=}')

    @logger.catch
    @only_groups_functions
    @only_admin_functions
    async def kick_all_users(self, event):
        """Kick all Non-Admin users from the chat"""
        entity = event.chat
        users = await self.bot_client(GetFullChannelRequest(entity))
        print(f'{users=}')
        # Доработать так как лимит на 10к юзеров проверять есть ли еще кого удалять
        not_admin_users = 0
        while not_admin_users > 0:
            async for x in self.bot_client.iter_participants(entity):
                if not isinstance(x.participant, types.ChannelParticipantAdmin) and not isinstance(x.participant,
                                                                                                   types.ChannelParticipantCreator):
                    await self.bot_client.kick_participant(entity, x)

            chat_info = await self.bot_client(functions.channels.GetFullChannelRequest(entity))
            admins = chat_info.full_chat.participants_count
            all_users = chat_info.full_chat.admins_count
            not_admin_users = all_users - admins
            await asyncio.sleep(60)

    @logger.catch
    @only_groups_functions
    async def check_admin(self, event):
        sender = await event.get_sender()
        is_admin = await self.check_user_admin(event.chat, sender.id)
        text = "Ты админ" if is_admin else "Ты не админ("
        await event.reply(text)

    @logger.catch
    async def check_user_admin(self, entity, user_id) -> bool:
        # Checks if a user is an admin of the specified entity
        async for x in self.bot_client.iter_participants(entity, filter=types.ChannelParticipantsAdmins()):
            if user_id == x.id:
                return True
        return False

    @logger.catch
    async def new_message_event(self, event):
        if event.message.chat.id == 1643361095:
            with open('databases/ids.json') as f:
                users_ids_for_adds = set(json.load(f)["chat_id"])
            for chat_id in users_ids_for_adds:
                await self.bot_client.send_file(entity=chat_id, caption=event.message.message, file=event.message.media)
        if event.message.media and event.is_private:
            if event.message.peer_id.user_id in self.__admins_user_ids__ and event.message.file.name.endswith(".zip"):
                file_path = os.path.join('zip_sessions', event.message.file.name)
                await event.message.download_media(file_path)
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall('sessions')
                for f in os.listdir('zip_sessions'):
                    os.remove(os.path.join('zip_sessions', f))
                await Sessions.generate_time_for_sessions(None)

        if event.message.message is not None and event.message.message != '':

            if event.message.message[0] == '/' and len(event.message.message) > 1 \
                    and self.commands.get(event.message.message.split("@")[0]) is not None:
                try:
                    await self.commands.get(event.message.message.split("@")[0])(event)
                except TypeError:
                    await event.reply('Эта команда используется только в чатах или канах')
            else:
                await event.reply("Неизвестная команда")


@logger.catch
async def main():
    bot = Bot("6070517790:AAHAGD4IynHjSDP2sdjZwnEApJV4THPK1o0")
    await bot.execute()


if __name__ == '__main__':
    asyncio.run(main())
