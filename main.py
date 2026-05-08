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

    
    # Кнопки в самом чате (Inline)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔍 Осмотреть сцену", callback_data="stage"))
    markup.add(types.InlineKeyboardButton("💡 Проверить аппаратную", callback_data="control"))
    markup.add(types.InlineKeyboardButton("📝 Осмотреть гримёрку", callback_data="makeup"))
    markup.add(types.InlineKeyboardButton("📂 Мои улики", callback_data="clues"))
    
    bot.send_message(
        message.chat.id, 
        "🎭 ДЕЛО О СОРВАННОМ СПЕКТАКЛЕ\n\nКто-то пытается сорвать премьеру! Исследуйте локации и найдите все улики, прежде чем выдвигать обвинение.",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ---------- ОБРАБОТКА НАЖАТИЙ ----------
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.message.chat.id
    if user_id not in player_clues: player_clues[user_id] = []

    if call.data == "stage":
        if "Маска" not in player_clues[user_id]:
            player_clues[user_id].append("Маска")
            bot.answer_callback_query(call.id, "Вы нашли маску!")
            bot.send_message(user_id, "🎭 За кулисами лежит жуткая маска. Кажется, кто-то пугал в ней актеров.")
        else:
            bot.send_message(user_id, "Там больше ничего интересного.")

    elif call.data == "control":
        if "Таймер" not in player_clues[user_id]:
            player_clues[user_id].append("Таймер")
            bot.answer_callback_query(call.id, "Улика найдена!")
            bot.send_message(user_id, "⏱ В пульте управления светом установлен таймер. Это работа профессионала.")
        else:
            bot.send_message(user_id, "Аппаратура работает в штатном режиме.")

    elif call.data == "makeup":
        if "Записка" not in player_clues[user_id]:
            player_clues[user_id].append("Записка")
            bot.answer_callback_query(call.id, "Вы нашли письмо!")
            bot.send_message(user_id, "📝 В гримёрке записка: 'Спектакль должен быть отменён любой ценой!'")
        else:
            bot.send_message(user_id, "Тут только пустые тюбики от грима.")

    elif call.data == "clues":
        clues_list = player_clues[user_id]
        if len(clues_list) < 3:
            text = "🧐 Маловато улик... Найдите все 3 предмета!\nСейчас у вас: " + ", ".join(clues_list)
            bot.send_message(user_id, text)
        else:
            # Если все улики собраны, даем список подозреваемых
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("👤 Актриса-школьница Аружан ", callback_data="sus_actor"))
            markup.add(types.InlineKeyboardButton("👤 Подозрительная новенькая Балнур", callback_data="sus_newbie"))
            markup.add(types.InlineKeyboardButton("🛠 Техник сцены Канат", callback_data="sus_tech"))
            
            bot.send_message(user_id, "🔍 У вас достаточно улик! Кто по-вашему виноват?", reply_markup=markup)

    # Логика обвинения
    elif call.data == "sus_actor":
        bot.send_message(user_id, "❌ НЕВЕРНО.\nАктриса была на сцене во время мигания света. Она не могла установить таймер.")
    
    elif call.data == "sus_newbie":
        bot.send_message(user_id, "❌ НЕВЕРНО.\nНовенькая даже не знает, где находится аппаратная. Маска ей велика.")
    
    elif call.data == "sus_tech":
        bot.send_message(user_id, "✅ ВЕРНО! ЭТО ТЕХНИК!\n\nЛОГИКА:\n1. Только техник мог незаметно поставить Таймер в сложный пульт.\n2. Маска нужна была, чтобы его не узнали, если он столкнется с кем-то в темноте.\n3. В Записке говорилось об отмене — он завидовал славе актеров и хотел провала.")


print("Детектив-бот на Inline кнопках запущен!")
bot.polling(none_stop=True)
# Возвращаем всех персонажей и их секреты в конце
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
