import os
import time
import threading
import discord
from discord.ext import commands, tasks
from flask import Flask
import aiohttp

# -------------------------------
# 🚀 Partie Flask (Keep-alive)
# -------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Le bot est en ligne ✅"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# -------------------------------
# ⚙️ Partie Discord
# -------------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Variables globales
Reglement_id = 1031818811265011712
last_welcome_time = 0
WELCOME_COOLDOWN = 15  # secondes
welcome_queue = []

# -------------------------------
# 📜 Événements
# -------------------------------
@bot.event
async def on_ready():
    try:
        await bot.user.edit(username="Bot PDD")  # max 2 changements par heure
    except Exception as e:
        print(f"[LOG] Impossible de changer le nom du bot : {e}")
    print(f"[LOG] Bot connecté en tant que {bot.user}")
    send_welcome_messages.start()
    keep_alive.start()

@bot.event
async def on_member_join(member):
    global last_welcome_time
    now = time.time()

    print(f"[LOG] Nouveau membre détecté : {member.name}#{member.discriminator} (ID: {member.id})")

    # Ajoute le membre à la file d’attente (sans doublons)
    if member not in welcome_queue:
        welcome_queue.append(member)
        print(f"[LOG] {member.name} ajouté à la file d’attente ({len(welcome_queue)} en attente)")

    # Si le cooldown est écoulé, envoie tout de suite
    if now - last_welcome_time >= WELCOME_COOLDOWN:
        await send_group_message()

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
    channel_id = 1004871766201614416  # <-- ID du salon de bienvenue
    channel = bot.get_channel(channel_id)

    if channel and isinstance(channel, discord.TextChannel):
        mentions = " ".join([member.mention for member in welcome_queue])
        await channel.send(f"""Bienvenue {mentions} sur le discord des Challenges PDD !
Pour participer à nos Challenges, quelques règles essentielles :
Nous t'invitons à lire les **règlements** <#{Reglement_id}> (règlements distincts des courses et des records)
Ton **pseudo Discord PDD doit être identique au nom de ton bateau** ⛵️ (nom de bateau – initiales Team / prénom)
Pour chaque course, un **formulaire d’Inscription** 📃 sera diffusé 10 jours avant le départ et clos à H-24
À H-23h jusqu’à l’heure du départ, un 2ème **formulaire Options** 📃 sera édité. Il sera clos au départ de la course.
Pour permettre les classements, un **Pavillon à hisser (Pays + Département)** 🏳️ sera précisé en même temps. Le changement de pavillon sera clos au 1er classement (H+24)
Des courses OFF hors challenge PDD sont également proposées et classées pour le fun avec leurs salons dédiés.
Au plaisir de te voir sur les flots avec nous ! 🌊""")

        print(f"[LOG] Message de bienvenue envoyé à {len(welcome_queue)} membres.")
        welcome_queue.clear()
        last_welcome_time = time.time()
    else:
        print(f"[LOG] Canal de bienvenue introuvable ou invalide : {channel}")

# -------------------------------
# 🛠️ Keep-alive interne
# -------------------------------
@tasks.loop(minutes=5)
async def keep_alive():
    """Ping le site Render pour éviter l'inactivité."""
    url = "https://botpdd.onrender.com"  # 🔧 Remplace par ton URL Render
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                print(f"[LOG] Keep-alive ping → {resp.status}")
    except Exception as e:
        print(f"[LOG] Erreur keep-alive : {e}")

# -------------------------------
# 🚀 Lancement global
# -------------------------------
def run_discord():
    token = os.environ["TOKEN_BOT"]
    bot.run(token)

if __name__ == "__main__":
    # Lancer Flask dans un thread séparé
    threading.Thread(target=run_flask).start()

    # Lancer Discord dans le thread principal
    run_discord()
