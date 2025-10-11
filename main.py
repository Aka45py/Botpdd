import os
import time
import threading
import discord
from discord.ext import commands, tasks
from flask import Flask
import aiohttp
import asyncio
import sys
import traceback

# -------------------------------
# 🚀 Flask principal (Render-friendly)
# -------------------------------
app = Flask(__name__)
bot_ready = False  # Indicateur de statut du bot

@app.route('/')
def home():
    return ("<h2>✅ Le bot PDD est en ligne</h2>"
            f"<p>Statut Discord : {'🟢 Connecté' if bot_ready else '🔴 Déconnecté'}</p>"), 200

@app.route('/status')
def status():
    if bot_ready:
        return "✅ Bot Discord connecté"
    else:
        return "❌ Bot Discord déconnecté", 503

# -------------------------------
# ⚙️ Discord Bot
# -------------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

Reglement_id = 1031818811265011712
last_welcome_time = 0
WELCOME_COOLDOWN = 15
welcome_queue = []

# -------------------------------
# 📜 Événements Discord
# -------------------------------
@bot.event
async def on_ready():
    global bot_ready
    bot_ready = True
    print(f"[LOG] Bot connecté en tant que {bot.user}")
    try:
        await bot.user.edit(username="Bot PDD")
    except Exception as e:
        print(f"[LOG] Nom du bot non modifié : {e}")
    send_welcome_messages.start()
    keep_alive.start()

@bot.event
async def on_disconnect():
    global bot_ready
    bot_ready = False
    print("[LOG] Bot déconnecté 😢")

@bot.event
async def on_resumed():
    global bot_ready
    bot_ready = True
    print("[LOG] Bot reconnecté 🎉")

@bot.event
async def on_member_join(member):
    global last_welcome_time
    now = time.time()
    print(f"[LOG] Nouveau membre détecté : {member} (ID: {member.id})")

    if member not in welcome_queue:
        welcome_queue.append(member)
        print(f"[LOG] Ajouté à la file d’attente ({len(welcome_queue)} membres).")

# -------------------------------
# 🔁 Tâches récurrentes
# -------------------------------
@tasks.loop(seconds=5)
async def send_welcome_messages():
    global last_welcome_time
    now = time.time()
    if welcome_queue and now - last_welcome_time >= WELCOME_COOLDOWN:
        await send_group_message()

async def send_group_message():
    global last_welcome_time
    channel_id = 1004871766201614416
    channel = bot.get_channel(channel_id)
    if channel and isinstance(channel, discord.TextChannel):
        mentions = " ".join([m.mention for m in welcome_queue])
        await channel.send(f"""Bienvenue {mentions} sur le discord des Challenges PDD !
Pour participer à nos Challenges, quelques règles essentielles :
Nous t'invitons à lire les **règlements** <#{Reglement_id}> (règlements distincts des courses et des records)
Ton **pseudo Discord PDD doit être identique au nom de ton bateau** ⛵️ (nom de bateau – initiales Team / prénom ) 
Pour chaque course, un **formulaire d’Inscription** 📃 sera diffusé 10 jours avant le départ et clos à H-24
A H-23h jusqu’à l’heure du départ, un 2ème **formulaire Options** 📃 sera édité. Il sera clos au départ de la course. 
Pour permettre les classements, un **Pavillon à hisser (Pays + Département)** 🏳️ sera précisé en même temps. Le changement de pavillon sera clos au 1er classement (H+ 24)
Des courses OFF hors challenge PDD sont également proposées et classées pour le fun avec leurs salons dédiés.
Au plaisir de te voir sur les flots avec nous""")
        welcome_queue.clear()
        last_welcome_time = time.time()
        print("[LOG] Message de bienvenue envoyé.")
    else:
        print("[LOG] Canal de bienvenue introuvable ou invalide.")

@tasks.loop(minutes=5)
async def keep_alive():
    url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME','botpdd.onrender.com')}/status"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                print(f"[LOG] Keep-alive ping → {resp.status}")
    except Exception as e:
        print(f"[LOG] Erreur keep-alive : {e}")

# -------------------------------
# 🛠️ Supervision du bot Discord
# -------------------------------
def start_discord_bot():
    while True:
        try:
            token = os.environ.get("TOKEN_BOT")
            if not token:
                print("[ERREUR] TOKEN_BOT manquant dans Render Environment")
                sys.exit(1)
            print("[LOG] Lancement du bot Discord...")
            bot.run(token)
        except Exception as e:
            print(f"[ERREUR] Bot Discord crashé, redémarrage dans 10 sec : {e}")
            traceback.print_exc()
            time.sleep(10)  # délai avant relance

# -------------------------------
# 🚀 Lancement principal
# -------------------------------
if __name__ == "__main__":
    # Lancer Discord dans un thread daemon (supervisé)
    threading.Thread(target=start_discord_bot, daemon=True).start()

    # Lancer Flask sur le port fourni par Render
    port = int(os.environ.get("PORT", 10000))
    print(f"[LOG] Lancement Flask sur le port {port}")
    app.run(host="0.0.0.0", port=port, use_reloader=False)
