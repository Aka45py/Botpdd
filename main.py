import os
import time
import threading
import discord
from discord.ext import commands, tasks
from flask import Flask

# -------------------------------
# 🚀 Flask (Render-friendly)
# -------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "<h2>✅ Le bot PDD est en ligne</h2>", 200

@app.route('/status')
def status():
    return "OK", 200   # ⚠️ JAMAIS 503 sur Render

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    print(f"[LOG] Lancement Flask sur le port {port}")
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# -------------------------------
# ⚙️ Discord Bot
# -------------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

Reglement_id = 1031818811265011712
Application_pdd = 1438894898534154260

WELCOME_CHANNEL_ID = 1004871766201614416
WELCOME_COOLDOWN = 15

last_welcome_time = 0
welcome_queue = []
welcome_lock = False

# -------------------------------
# 📜 Événements Discord
# -------------------------------
@bot.event
async def on_ready():
    print(f"[LOG] Bot connecté en tant que {bot.user}")

    try:
        
    except Exception as e:
        print(f"[LOG] Nom du bot non modifié : {e}")

    if not send_welcome_messages.is_running():
        send_welcome_messages.start()

@bot.event
async def on_disconnect():
    print("[LOG] Discord déconnecté (temporaire)")

@bot.event
async def on_resumed():
    print("[LOG] Discord reconnecté 🎉")

@bot.event
async def on_member_join(member):
    print(f"[LOG] Nouveau membre : {member} ({member.id})")

    if member.id not in [m.id for m in welcome_queue]:
        welcome_queue.append(member)
        print(f"[LOG] File d’attente : {len(welcome_queue)}")

# -------------------------------
# 🔁 Bienvenue
# -------------------------------
@tasks.loop(seconds=5)
async def send_welcome_messages():
    global last_welcome_time
    if not welcome_queue:
        return

    now = time.time()
    if now - last_welcome_time >= WELCOME_COOLDOWN:
        await send_group_message()

async def send_group_message():
    global last_welcome_time, welcome_lock

    if welcome_lock:
        return

    welcome_lock = True

    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        print("[LOG] Canal de bienvenue introuvable")
        welcome_lock = False
        return

    mentions = " ".join(m.mention for m in welcome_queue)

    await channel.send(f"""Bienvenue {mentions} sur le discord des Challenges PDD !
Pour participer à nos Challenges, quelques règles essentielles :
Nous t'invitons à lire les **règlements** <#{Reglement_id}> (règlements distincts des courses et des records)
Ton **pseudo Discord PDD doit être identique au nom de ton bateau** ⛵️ (nom de bateau – initiales Team / prénom)
Pour chaque course, l'inscription se fera sur une **application web** développée en interne <#{Application_pdd}>
Un **Pavillon à hisser (Pays + Département)** 🏳️ sera précisé pour chaque course
Des courses OFF hors challenge PDD sont également proposées
Au plaisir de te voir sur les flots avec nous 🌊""")

    print("[LOG] Message de bienvenue envoyé")

    welcome_queue.clear()
    last_welcome_time = time.time()
    welcome_lock = False

# -------------------------------
# 🚀 Lancement
# -------------------------------
def run_discord():
    token = os.environ.get("TOKEN_BOT")
    if not token:
        raise RuntimeError("TOKEN_BOT manquant")
    bot.run(token)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_discord()
