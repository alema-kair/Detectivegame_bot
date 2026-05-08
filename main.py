import telebot
from telebot import types

TOKEN = "8719751151:AAFOeY77gn_Fu006sgdM4TSc30oUWTztdRk"
bot = telebot.TeleBot(TOKEN)

player_clues = {}

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    player_clues[user_id] = []
    
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
            markup.add(types.InlineKeyboardButton("👤 Актер-школьник", callback_data="sus_actor"))
            markup.add(types.InlineKeyboardButton("👤 Подозрительная новенькая", callback_data="sus_newbie"))
            markup.add(types.InlineKeyboardButton("🛠 Техник сцены", callback_data="sus_tech"))
            
            bot.send_message(user_id, "🔍 У вас достаточно улик! Кто по-вашему виноват?", reply_markup=markup)

    # Логика обвинения
    elif call.data == "sus_actor":
        bot.send_message(user_id, "❌ НЕВЕРНО.\nАктер был на сцене во время мигания света. Он не мог установить таймер.")
    
    elif call.data == "sus_newbie":
        bot.send_message(user_id, "❌ НЕВЕРНО.\nНовенькая даже не знает, где находится аппаратная. Маска ей велика.")
    
    elif call.data == "sus_tech":
        bot.send_message(user_id, "✅ ВЕРНО! ЭТО ТЕХНИК!\n\nЛОГИКА:\n1. Только техник мог незаметно поставить Таймер в сложный пульт.\n2. Маска нужна была, чтобы его не узнали, если он столкнется с кем-то в темноте.\n3. В Записке говорилось об отмене — он завидовал славе актеров и хотел провала.")

# ---------- ЗАПУСК ----------
print("Детектив-бот на Inline кнопках запущен!")
bot.polling(none_stop=True)
