# Import libraries for Telegram bot
import telebot
from telebot import types
import os

# Telegram bot token from BotFather
TOKEN = "8719751151:AAE5mZpZnLKKRe_2lFhWodQN6D2BjQCgN3s"
bot = telebot.TeleBot(TOKEN)

try: bot.stop_polling()
except: pass
    
# Dictionary for storing player data
players = {}

# Class with a suspect in the game
class Suspect:
    def _init_(self, name, role, info, q1, q2, q3, second_round, is_guilty, final_truth):
        self.name, self.role, self.info = name, role, info
        self.q1, self.q2, self.q3 = q1, q2, q3
        self.second_round, self.is_guilty, self.final_truth = second_round, is_guilty, final_truth

   
# 2. DATABASE (FULL ORIGINAL SCENARIO)
suspects = {
    "kanat": Suspect("Kanat", "Technician", 
        "⚙️ A gloomy man in a work jumpsuit, smelling of machine oil.",
        "I am Kanat, the technician. I arrived at the start of the working day at 7:00 AM, FaceID can confirm that I arrived on time.",
        "I haven't seen anything and I haven't heard anything because I wasn't there. FaceID shows I arrived, but I was busy.",
        "I was in the utility room since 7:00 AM. I saw nothing and heard nothing. No one saw me and no one can confirm it.",
        "🕵️ Detective: Your FaceID is confirmed, but no one saw you. And this professional timer in the console... only you could do it.\n\n🛠️ Kanat: I was in the basement! Kids don't go there!", 
        True,
        "Kanat confessed: He had a major conflict with the school administration. Knowing how important this show was for the school, he decided to ruin everything out of spite."),

    "aruzhan": Suspect("Aruzhan", "Actress", 
        "🎭 A beautiful girl in a theatrical costume, looking very pale and frightened.",
        "I'm Aruzhan, the lead actress. I arrived at 8:00 AM and immediately went backstage to rehearse.",
        "I heard it when it was already happening! I saw the figure of the one who was scaring the students.",
        "I was on stage, rehearsing my role under the spotlights.",
        "🕵️ Detective: Your FaceID was not confirmed for 8:00. Why did you lie?\n\n💧 Aruzhan: I was afraid of Aidana! I thought I wouldn't be allowed to play anymore!", 
        False, "Aruzhan was actually an hour late and lied to avoid trouble with the teacher."),

    "azhar": Suspect("Azhar", "Makeup Artist", 
        "💄 A girl with brushes, fixing her makeup.",
        "I arrived at 8:00 AM, FaceID can prove it. I went straight to the dressing room.",
        "I found a note immediately! I decided not to touch it because it scared me.",
        "I was in the dressing room, preparing tools for the actors.",
        "🕵️ Detective: FaceID is confirmed. What exactly were you doing?\n\n🎨 Azhar: I was organizing my makeup kits and preparing the costumes!", 
        False, "Azhar was not lying. She just found the note ."),
    
    "balnur": Suspect("Balnur", "New Girl", 
        "🎒 A girl in a school uniform with a huge backpack.",
        "I'm Balnur, I'm new here. I arrived at 7:30 AM (FaceID confirmed). Ms. Aidana asked me to come early.",
        "I saw the figure of the person in the mask and also light was flashing.",
        "I arrived just seconds before. I saw everything and I was the first to pick up the mask.",
        "🕵️ Detective: Why did you decide to take the mask in your hands?\n\n🏃‍♀️ Balnur: I decided to run after him and found the mask on the road!", 
        False, "Balnur was confused and found the mask while trying to catch the stranger."),

    "aidana": Suspect("Aidana", "Teacher", 
        "👩‍🏫 A strict woman in glasses, holding a gradebook.",
        "I am Aidana, the teacher in charge. I arrived at 7:50 AM.",
        "I didn't notice anything unusual before that. The school was quiet.",
        "I went straight to the assembly hall at 8:00 AM and saw what happened myself!",
        "🕵️ Detective: Why did you lie that you were there and controlled everything?\n\n☕️ Aidana: I didn't want the Principal to think I left the students unsupervised while I was in the staff room!", 
        False, "Aidana was embarrassed that she was drinking tea in the staff room during the incident.")
}

# 3. GAME LOGIC
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    players[user_id] = {"clues": [], "interrogated": [], "round2": []}
    
intro = (
        "🎭 **THE MORNING BEFORE THE PERFORMANCE**\n\n"
        "This day began with a real chaos in the assembly hall. A very important performance was supposed to take place in the evening, "
        "but someone sneaked into the school at night and sabotaged it. The director is furious! "
        "The lights were constantly flashing on and off and several notes with threatening messages were found. "
        "Many children are scared and claim to have seen a ghost in a mask. "
        "The school management invited you to find the culprit before the performance begins. "
        "You have until the evening, five suspects and three locations.\n\n"
        "👤 **What is your name, Detective?**"
    )
    bot.send_message(user_id, intro, parse_mode="Markdown")
    bot.register_next_step_handler(message, lambda m: save_name(m))

def save_name(message):
    user_id = message.chat.id
    players[user_id]["name"] = message.text
    show_main_menu(user_id)

def show_main_menu(user_id):
    markup = types.InlineKeyboardMarkup()
    p = players[user_id]
    if len(p["interrogated"]) < 5:
        markup.add(types.InlineKeyboardButton("👤 Step 1: Interviews", callback_data="round1"))
    elif len(p["clues"]) < 3:
        markup.add(types.InlineKeyboardButton("🔍 Step 2: Search Clues", callback_data="search"))
    elif len(p["round2"]) < 5:
        markup.add(types.InlineKeyboardButton("❓ Step 3: Second Interrogation", callback_data="round2"))
    else:
        markup.add(types.InlineKeyboardButton("⚖️ Step 4: Final Verdict", callback_data="verdict"))
    bot.send_message(user_id, f"Detective {p.get('name', 'Detective')}, current phase:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.message.chat.id
    if user_id not in players: return

    if call.data == "round1":
        markup = types.InlineKeyboardMarkup()
        for k, s in suspects.items():
            btn_text = f"✅ {s.name}" if k in players[user_id]["interrogated"] else f"👤 {s.name}"
            markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"sel_{k}"))
        bot.send_message(user_id, "Who will you interview?", reply_markup=markup)
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
       # Умный поиск пути (ищет в папке проекта)
        base_dir = os.path.join(os.getcwd(), "Downloads", "detective_bot")
        full_path = os.path.join(base_dir, file_name)
        if not os.path.exists(full_path):
             full_path = os.path.join(os.getcwd(), file_name)
        
        if clue_names[item] not in players[user_id]["clues"]:
            players[user_id]["clues"].append(clue_names[item]) 

            if os.path.exists(full_path):
                with open(full_path, 'rb') as photo:
                    bot.send_photo(user_id, photo, caption=f"✅ Найдена улика: *{clue_names[item]}*", parse_mode="Markdown")
            else:
                bot.send_message(user_id, f"✅ Найдена улика: *{clue_names[item]}*\n(Картинка не найдена в папке)")
        
        show_main_menu(user_id)
 elif call.data == "round2":
        markup = types.InlineKeyboardMarkup()
        for key, s in suspects.items():
            markup.add(types.InlineKeyboardButton(f"Допросить {s.name}", callback_data=f"talk2_{key}"))
        bot.send_message(user_id, "Второй раунд. Поймайте их на лжи!", reply_markup=markup)

    elif call.data.startswith("talk2_"):
        s_key = call.data.split("_")[1]
        s = suspects[s_key]
        bot.send_message(user_id, s.second_round, parse_mode="Markdown")
        show_main_menu(user_id)


    elif call.data == "verdict":
        markup = types.InlineKeyboardMarkup()
        for key, s in suspects.items():
            markup.add(types.InlineKeyboardButton(f"Обвинить: {s.name}", callback_data=f"final_{key}"))
        bot.send_message(user_id, "Кто виновен?", reply_markup=markup)

    elif call.data.startswith("final_"):
        s_key = call.data.split("_")[1]
        s = suspects[s_key]
        if s.is_guilty:
            # Выводим победу и ВСЕ признания
            response = f"✅ *ПОБЕДА! Это {s.name}!*\n\n{s.final_truth}\n\n"
            response += "*А вот почему врали остальные:*\n"
            for k, other in suspects.items():
                if k != s_key:
                    response += f"🔹 *{other.name}*: {other.final_truth}\n"
            bot.send_message(user_id, response, parse_mode="Markdown")
        else:
            bot.send_message(user_id, f"❌ *ОШИБКА!* {s.name} не виноват(а). Пока вы спорили, преступник скрылся!")
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    bot.send_message(message.chat.id, "⚠️ Используйте кнопки меню!")

print("Бот запущен!")
bot.polling(none_stop=True)
