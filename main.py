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
        "A gloomy man in a work jumpsuit, smelling of machine oil.",
        "I am Kanat, the technician. I arrived at the start of the working day at 7:10 AM, FaceID can confirm that I arrived on time.",
        "I haven't seen anything and I haven't heard anything because I wasn't there. FaceID shows I arrived, but I was busy.",
        "I was in the utility room since 7:10 AM. I saw nothing and heard nothing. No one saw me and no one can confirm it.",
        "Detective: Your FaceID is confirmed, but no one saw you. And this professional timer in the console... only you could do it.\n\nKanat: I was in the basement! Kids don't go there!",
        True, "Kanat confessed: He had a major conflict with the school administration. Knowing how important this show was for the school, he decided to ruin everything out of spite."),
    
    "aruzhan": Suspect("Aruzhan", "Actress",
        "A beautiful girl in a theatrical costume, looking very pale and frightened.",
        "I'm Aruzhan, the lead actress. I arrived at 7:45 AM and immediately went backstage to rehearse.",
        "I heard it when it was already happening! I saw the figure of the one who was scaring the students.",
        "I was on stage, rehearsing my role under the spotlights.",
        "Detective: Your FaceID was not confirmed for 7:45. Why did you lie?\n\nAruzhan: I was afraid of Aidana! I thought I wouldn't be allowed to play anymore!",
        False, "Aruzhan was actually an hour late and lied to avoid trouble with the teacher."),

    "azhar": Suspect("Azhar", "Makeup Artist",
        "A girl with brushes, fixing her makeup.",
        "I arrived at 7:50 AM, FaceID can prove it. I went straight to the dressing room.",
        "I found a note immediately! I decided not to touch it because it scared me. After that i heard the noise and saw the figure of the one who was scaring the students",
        "I was in the dressing room, preparing tools for the actors.",
        "Detective: FaceID is confirmed. What exactly were you doing in the dressing room?\n\nAzhar: I was organizing my makeup kits and preparing the costumes for actors!",
        False, "Azhar was not lying. She just found the note."),
    
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

    elif call.data.startswith("sel_"):
        k = call.data[4:]
        s = suspects[k]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Introduce yourself and arrival time?", callback_data=f"q1_{k}"))
        markup.add(types.InlineKeyboardButton("Did you hear anything unusual?", callback_data=f"q2_{k}"))
        markup.add(types.InlineKeyboardButton("Where were you at 8:00 AM?", callback_data=f"q3_{k}"))
        markup.add(types.InlineKeyboardButton("🔙 Finish", callback_data="back"))
        bot.edit_message_text(f"Questioning {s.name}...\n{s.info}", user_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith(("q1_", "q2_", "q3_")):
        q, k = call.data[:2], call.data[3:]
        if k not in players[user_id]["interrogated"]: players[user_id]["interrogated"].append(k)
        bot.send_message(user_id, f"🗣️ *{suspects[k].name}:* {getattr(suspects[k], q)}", parse_mode="Markdown")

    elif call.data == "back":
        bot.delete_message(user_id, call.message.message_id)
        show_main_menu(user_id)

    elif call.data == "search":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎭 Stage", callback_data="clue_mask"),
                   types.InlineKeyboardButton("⚡️ Booth", callback_data="clue_timer"),
                   types.InlineKeyboardButton("💄 Room", callback_data="clue_letter"))
        bot.send_message(user_id, "Search location:", reply_markup=markup)

    elif call.data.startswith("clue_"):
        item = call.data[5:]
        clue_names = {"mask": "Mask", "timer": "Timer", "letter": "Note"}
        clue_texts = {
            "mask": "The mask used to scare children. It's very big. Found by Balnur.",
            "timer": "A professional timer. It caused the flickering. Expert work.",
            "letter": "Found by Azhar. Crude handwriting. 'Cancel the play at any cost'."
        }
        
 path = os.path.join(os.path.expanduser("~"), "Downloads", "detective_bot", f"{item}.jpg")
        
        if clue_names[item] not in players[user_id]["clues"]: players[user_id]["clues"].append(clue_names[item])
        
        if os.path.exists(path):
            with open(path, 'rb') as f:
                bot.send_photo(user_id, f, caption=f"✅ Found: {clue_names[item]}\n{clue_texts[item]}")
        else:
            bot.send_message(user_id, f"✅ Found: {clue_names[item]}\n{clue_texts[item]}\n\n⚠️ Image {item}.jpg not found.")
        show_main_menu(user_id)

    elif call.data == "round2":
        markup = types.InlineKeyboardMarkup()
        for k, s in suspects.items():
            btn_text = f"✅ {s.name}" if k in players[user_id]["round2"] else f"👤 {s.name}"
            markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"t2_{k}"))
        bot.send_message(user_id, "Second interrogation:", reply_markup=markup)

    elif call.data.startswith("t2_"):
        k = call.data[3:]
        if k not in players[user_id]["round2"]: players[user_id]["round2"].append(k)
        bot.send_message(user_id, suspects[k].second_round, parse_mode="Markdown")
        show_main_menu(user_id)

    elif call.data == "verdict":
        markup = types.InlineKeyboardMarkup()
        for k, s in suspects.items(): markup.add(types.InlineKeyboardButton(f"Accuse: {s.name}", callback_data=f"fin_{k}"))
        bot.send_message(user_id, "Who is guilty?", reply_markup=markup)

    elif call.data.startswith("fin_"):
        k = call.data[4:]
        s = suspects[k]
        if s.is_guilty:
            res = f"✅ *SOLVED! It was {s.name}!\n\n{s.final_truth}\n\nOthers:*\n"
            for other_k, other_s in suspects.items():
                if other_k != k: res += f"• {other_s.name}: {other_s.final_truth}\n"
            bot.send_message(user_id, res, parse_mode="Markdown")
        else:
            bot.send_message(user_id, "❌ *WRONG!* The culprit managed to escape while you were accusing the innocent! Try again.")

print("Bot started...")
bot.polling(none_stop=True)
