from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import link
import logging
import random
import config
import json


logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)



def get_sessions():
    with open(config.path, 'r') as file:
        json_data = json.loads(file.read())
    return json_data


def get_session(telegram_id: int) -> dict:
    with open(config.path, 'r') as file:
        json_data = json.loads(file.read())
    if str(telegram_id) not in json_data.keys():
        return None
    return json_data.get(str(telegram_id))


def write_session(telegram_id: int, username: str, status: int, user_id: int, id_code: int, users: int=0):
    sessions = get_sessions()
    sessions[str(telegram_id)] = {
        "username": username,
        "status": str(status),
        "user_id": str(user_id),
        "id_code": str(id_code),
        "users": str(users),
        'users_list': []
    }

    with open(config.path, 'w') as file:
        file.write(json.dumps(sessions, indent=4))


@dp.message_handler(commands=['top'])
async def top(message: types.Message):
    data = get_sessions()
    sorted_data = dict(sorted(data.items(), key=lambda x: int(x[1]['users'])))
    msg = ""
    num = 0
    for i in sorted_data:
        if num == 10:
            break
        msg += f"{num+1}. `{sorted_data[i]['username']}` - {sorted_data[i]['users']}\n"
        num += 1
    await bot.send_message(message.chat.id, msg[:-1], parse_mode='Markdown')


@dp.message_handler(commands=['wallet'])
async def wallet(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="Чтобы присоединиться к программе, введите свой кошелек. USDT\n\n💳 Пожалуйста, введите кошелек *USDT*:", parse_mode='Markdown')
    sessions = get_sessions()
    sessions[str(message.chat.id)]['status'] = '-1'
    with open(config.path, 'w+') as f:
        f.write(json.dumps(sessions, indent=4))

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    session = get_session(message.chat.id)
    start_param = message.get_args()

    if start_param:
        sessions = get_sessions()
        for i in sessions:
            if sessions[i]['id_code'] == start_param and i != str(message.chat.id) and str(message.chat.id) not in sessions[i]['users_list']:
                users = int(sessions[i]['users'])
                sessions[i]['users'] = str(users+1)
                sessions[i]['users_list'].append(str(message.chat.id))

                with open(config.path, 'w') as file:
                    file.write(json.dumps(sessions, indent=4))
                break
    if session:
        if session['status'] == '1':
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(text="Подтвердить ✅", callback_data="accept")
            )

            await bot.send_photo(chat_id=message.chat.id, photo=open('img/1.jpg', 'rb'), caption=f"🚀 Чтобы принять участие в розыгрыше $5000 USDT от Crypto drop - присоединяйтесь к официальному чату\n\n{link('🚀 Официальный канал Crypto drop', 'https://t.me/ccryptodrop18')}\n{link('🚀 Официальный чат Crypto dropr', 'https://t.me/cryptodropchat1')}\n\nЗатем нажмите на кнопку `Подтвердить`, чтобы принять участие в розыгрыше 👇", parse_mode='Markdown', reply_markup=markup)
            return
        if session['status'] == '2':
            text = f"""*Поздравляю!*

Вы участвуете в розыгрыше 50 призовых мест на сумму $5000 USDT от Crypto drop!

Первые 50 призов в размере 50 долларов в USDT гарантированно получат 50 лучших участников по количеству приглашенных друзей

Оставшиеся 50 мест будут разыграны случайным образом с помощью генератора случайных чисел в прямом эфире 12 августа 🚀

🥳 Подписка на чат и канал дает вам 1 билет на участие в розыгрыше.

Ваш идентификационный номер: *{session['id_code']}*

Увеличьте свои шансы на победу, приглашая друзей или выполняя задания! 👇"""
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(text="🚀 Увеличить шансы", callback_data="upp")
            )
            await bot.send_photo(chat_id=message.chat.id, photo=open('img/1.jpg', 'rb'), caption=text, parse_mode='Markdown', reply_markup=markup)
            return
        if session['status'] == '3':
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(text="Обновить 🔄", callback_data="update")
            )
            await bot.send_photo(chat_id=message.chat.id, photo=open('img/1.jpg', 'rb'), caption=f"Ваша личная реферальная ссылка: https://t.me/cryptodrawusdtBot?start={session['id_code']}\nПриглашенных пользователей: {session['users']}", parse_mode='Markdown', reply_markup=markup)
            return
    id_code = random.randint(10000, 99999)
    write_session(message.chat.id, message.from_user.username, 0, message.from_user.id, id_code)
    await bot.send_message(chat_id=message.chat.id, text="Чтобы присоединиться к программе, введите свой кошелек. USDT\n\n💳 Пожалуйста, введите кошелек *USDT*:", parse_mode='Markdown')


@dp.callback_query_handler(lambda call: call.data == 'accept')
async def answer(call: types.CallbackQuery, *args):
    user_id = get_session(call.message.chat.id)['user_id']
    user_channel_status_1 = await bot.get_chat_member(chat_id='-1001544129871', user_id=int(user_id))
    user_channel_status_2 = await bot.get_chat_member(chat_id='-1001911655784', user_id=int(user_id))

    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if user_channel_status_1["status"] != 'left' and user_channel_status_2["status"] != 'left':
        await bot.answer_callback_query(call.id, text='✅ Вы успешно подписались на каналы, теперь вы можете участовать в розыгрышах!', show_alert=True)
        sessions = get_sessions()
        sessions[str(call.message.chat.id)]['status'] = '2'
        with open(config.path, 'w+') as f:
            f.write(json.dumps(sessions, indent=4))
    else:
        await bot.answer_callback_query(call.id, text='🚫 Вы не подписались! Пожалуйста подпишитесь и попробуйте снова.', show_alert=True)
    await send_welcome(call.message)

@dp.callback_query_handler(lambda call: call.data == 'update')
async def answer(call: types.CallbackQuery, *args):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await send_welcome(call.message)

@dp.callback_query_handler(lambda call: call.data == 'upp')
async def answer(call: types.CallbackQuery, *args):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    sessions = get_sessions()
    sessions[str(call.message.chat.id)]['status'] = '3'
    with open(config.path, 'w+') as f:
        f.write(json.dumps(sessions, indent=4))
    await send_welcome(call.message)

@dp.message_handler()
async def echo(message: types.Message):
    session = get_session(message.chat.id)
    if session['status'] == '0' or session['status'] == '-1':
        sessions = get_sessions()
        sessions[str(message.chat.id)]['status'] = '1'
        with open(config.path, 'w+') as f:
            f.write(json.dumps(sessions, indent=4))
        await send_welcome(message)
        return

    await bot.send_message(message.chat.id, "Кажется, что-то пошло не так.. (^-^*)")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)