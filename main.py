# Import libraries for Telegram bot
import telebot
from telebot import types
import os

# Telegram bot token from BotFather
TOKEN = "8719751151:AAFOeY77gn_Fu006sgdM4TSc30oUWTztdRk"
bot = telebot.TeleBot(TOKEN)

# Dictionary for storing player data
players = {}

# Class with a suspect in the game
class Suspect:
    def __init__(self, name, role, alibi, info, second_round, is_guilty, final_truth):
        self.name = name
        self.role = role
        self.alibi = alibi
        self.info = info
        self.second_round = second_round
        self.is_guilty = is_guilty
        self.final_truth = final_truth

   
# Dictionary containing all suspects
suspects = {
    "kanat": Suspect("Канат", "Техник", "Был в подсобке один, чинил проводку. Никого не видел.", 
                     "🛠️ Хмурый мужчина в рабочем комбинезоне, от него пахнет машинным маслом.", 
                     "🕵️ Детектив: Канат, в подсобке вас никто не видел, а в пульте найден таймер. Только вы могли его поставить.\n🛠️ Канат: Отстаньте, я просто работал в подвале!", True, 
                     "Канат сознался: он ненавидит шумные праздники и хотел сорвать спектакль, чтобы уволиться по собственному желанию. Он единственный, кто знал, как настроить таймер в старом пульте."),
    "aruzhan": Suspect("Аружан", "Актриса", "Я была на сцене всё утро, повторяла роль под софитами.", 
                       "🎭 Красивая девушка в театральном костюме, выглядит очень бледной и испуганной.", 
                       "🕵️ Детектив: Аружан, Ажар говорит, что сцена была пуста, когда она заглядывала. Где вы были?\n🎭 Аружан: Может я просто отошла воды попить? Да, точно, я была в коридоре!", False, 
                       "Аружан на самом деле проспала и пришла в школу на час позже, но боялась признаться в этом учителю Айдане, чтобы её не выгнали из спектакля."),
    "balnur": Suspect("Балнур", "Новенькая", "Я искала кабинет химии на 3 этаже, честно!", 
                      "🎒 Девочка в школьной форме с огромным рюкзаком, постоянно смотрит в карту школы.", 
                      "🕵️ Детектив: Балнур, другие говорят, что химии сегодня нет в расписании. Зачем вы туда шли?\n🎒 Балнур: Ой, я просто перепутала этажи! Я же новенькая!", False, 
                       "Балнур реально запуталась: в её старой школе химия была на 3 этаже, а в этой — на 1-м. Она не врала, просто ошиблась."),
    "azhar": Suspect("Ажар", "Гример", "Я была в гримёрке, Аружан пришла ко мне сразу.", 
                     "🎨 Веселая девушка, все руки в пятнах от яркого грима и блестках.", 
                     "🕵️ Детектив: Аружан пришла позже. Вы её выгораживаете?\n🎨 Ажар: Ну... я не смотрела на часы!", False, 
                     "Ажар врала про время прихода Аружан только для того, чтобы прикрыть свою лучшую подругу перед учителями."),
    "aidana": Suspect("Айдана", "Учитель", "У меня был урок истории в 9 'Б'.", 
                      "📚 Строгая женщина в очках, держит в руках толстый журнал успеваемости.", 
                      "🕵️ Детектив: Девочки говорят, уроки отменили. Какой урок вы вели?\n📚 Айдана: Это был факультатив!", False, 
                      "Айдана на самом деле сидела в учительской и спокойно пила чай, пока дети были предоставлены сами себе, но статус строгого учителя не позволял ей в этом признаться.")
}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    players[user_id] = {"name": "Детектив", "clues": [], "interrogated": []}
intro = (
        "🕒 *08:00 AM*\n\n"
        "*УТРО ПЕРЕД СПЕКТАКЛЕМ*\n"
        "Этот день начался с настоящего хаоса в актовом зале. Вечером должен был состояться очень важный спектакль, "
        "но кто-то пробрался ночью в школу и устроил саботаж. Директор в ярости! Свет постоянно мигал и выключался, "
        "и были найдены несколько записок с угрожающими посланиями. Многие дети напуганы и утверждают, что видели привидение в маске.\n\n"
        "Руководство школы пригласило вас, чтобы найти виновного до начала спектакля.\n\n"
        "🕵️‍♂️ *Как ваше имя, Детектив?*"
    )
    bot.send_message(user_id, intro, parse_mode="Markdown")
    bot.register_next_step_handler(message, save_name)

def save_name(message):
    user_id = message.chat.id
    players[user_id]["name"] = message.text
    show_main_menu(user_id)

def show_main_menu(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🤝 Опрос подозреваемых", callback_data="round1"))
    
 if len(players[user_id]["interrogated"]) >= 5:
        markup.add(types.InlineKeyboardButton("🔍 Осмотреть локации", callback_data="search"))
    
    if len(players[user_id]["clues"]) >= 3:
        markup.add(types.InlineKeyboardButton("❓ ПЕРЕКРЕСТНЫЙ ДОПРОС", callback_data="round2"))
        markup.add(types.InlineKeyboardButton("⚖️ ВЕРДИКТ", callback_data="verdict"))
bot.send_message(user_id, f"Детектив {players[user_id]['name']}, ваше действие:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.message.chat.id
    if user_id not in players: return

    if call.data == "round1":
        markup = types.InlineKeyboardMarkup()
        for key, s in suspects.items():
            prefix = "✅ " if key in players[user_id]["interrogated"] else "👤 "
            markup.add(types.InlineKeyboardButton(f"{prefix}{s.name}", callback_data=f"talk1_{key}"))
        bot.send_message(user_id, "Кого опросим?", reply_markup=markup)
 elif call.data.startswith("talk1_"):
        s_key = call.data.split("_")[1]
        if s_key not in players[user_id]["interrogated"]:
            players[user_id]["interrogated"].append(s_key)
            if len(players[user_id]["interrogated"]) == 5:
                bot.send_message(user_id, "📢 *Вы опросили всех подозреваемых! Теперь вам доступны локации для осмотра.*", parse_mode="Markdown")
        
        s = suspects[s_key]
        bot.send_message(user_id, f"👤 *{s.name}\n\nОблик:* {s.info}\n*Алиби:* \"{s.alibi}\"", parse_mode="Markdown")
        show_main_menu(user_id)

  elif call.data == "search":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎭 Сцена", callback_data="clue_mask"))
        markup.add(types.InlineKeyboardButton("⚡ Аппаратная", callback_data="clue_timer"))
        markup.add(types.InlineKeyboardButton("💄 Гримерка", callback_data="clue_letter"))
        bot.edit_message_text("Где будем искать улики?", user_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("clue_"):
        item = call.data.split("_")[1]
        clue_names = {"mask": "Маска", "timer": "Таймер", "letter": "Записка"}
        file_name = f"{item}.jpg"
        
