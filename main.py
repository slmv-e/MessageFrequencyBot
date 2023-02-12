from vkbottle.bot import Bot, Message
from vkbottle import API
from vkbottle.dispatch.rules import ABCRule
from vkbottle_types.objects import UsersUserFull
from datetime import datetime
from threading import Thread
from asyncio import run
from data import UsersInfo, User
from sheets_worker import Sheets
from json_handler import read_from_json, dump_to_json
from environs import Env

env = Env()
env.read_env(".env")
token = env.str("TOKEN")
bot = Bot(token=token)
api = API(token=token)
users_info = UsersInfo(users=[])


class AdminRule(ABCRule[Message]):
    def __init__(self, rule: bool):
        self.rule = rule

    async def check(self, event: Message) -> bool:
        return True if not self.rule else True if (await event.get_user()).id in read_from_json().admin_ids else False


class ChatRule(ABCRule[Message]):
    def __init__(self, rule: bool):
        self.rule = rule

    async def check(self, event: Message) -> bool:
        return True if not self.rule else True if event.peer_id in read_from_json().chat_ids else False


bot.labeler.custom_rules["admin_rule"] = AdminRule
bot.labeler.custom_rules["chat_rule"] = ChatRule


@bot.on.message(command=("add_this_chat", 0), admin_rule=True)
async def add_this_chat(message: Message):
    chat_id = message.peer_id
    chat_list = read_from_json().chat_ids
    if chat_id not in chat_list:
        chat_list.append(chat_id)
        dump_to_json(key="CHAT_IDS", value=chat_list)
        await message.answer("Этот чат успешно добавлен")
    else:
        await message.answer("Этот чат уже есть в списке")


@bot.on.message(chat_rule=True)
async def message_story(message: Message):
    user: UsersUserFull = await message.get_user()
    user_id = user.id
    user_full_name = f"{user.last_name} {user.first_name}"
    if user_id not in map(lambda usr: usr.id, users_info.users):
        users_info.users.append(User(
            full_name=user_full_name,
            id=user_id,
            last_time=int(datetime.now().timestamp()),
            messages_difference=[]
        ))
    else:
        user: User = list(filter(lambda usr: usr.id == user_id, users_info.users))[0]
        if (message_difference := datetime.now().timestamp() - user.last_time) < 30 * 60 and all(
            not_allowed_words not in message.text.lower()
            for not_allowed_words in ["приступил", "закончил", "начал", "окончил", "завершил"]
        ):
            user.messages_difference.append(int(message_difference))
        user.last_time = int(datetime.now().timestamp())


def main():
    sheets_app = Sheets(users_info=users_info)

    bot_process = Thread(target=run, args=(bot.run_polling(), ))
    sheets_process = Thread(target=sheets_app.start)

    sheets_process.start()
    bot_process.start()

    sheets_process.join()
    bot_process.join()


if __name__ == "__main__":
    main()
