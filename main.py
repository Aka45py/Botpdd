import os 
import time
import discord
from discord.ext import commands, tasks
from flask import Flask
import threading

# --------- Partie Flask pour keep-alive ---------
app = Flask(__name__)

@app.route('/')
def home():
    return "Le bot est en ligne ✅"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Lancement du serveur Flask dans un thread séparé
threading.Thread(target=run_flask).start()

# --------- Partie Discord Bot ---------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
Reglement_id = 1031818811265011712

# Variables pour le cooldown global
last_welcome_time = 0
WELCOME_COOLDOWN = 15  # secondes
welcome_queue = []  # file d’attente pour les nouveaux arrivants

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")
    send_welcome_messages.start()  # démarrage de la tâche en arrière-plan

@bot.event
async def on_ready():
    await bot.user.edit(username="Bot PDD")  # Change le nom global (attention : limité à 2 changements/heure)
    print(f"Bot connecté en tant que {bot.user}")

@bot.event
async def on_member_join(member):
    print("logo")
    global last_welcome_time
    now = time.time()

    # Message privé (toujours envoyé)
    #try:
    #   await member.send(f"Bienvenue sur le serveur, {member.name} ! 🎉")
    #except:
    #    print("Impossible d’envoyer un DM à ce membre.")

    # Ajoute le membre à la file d’attente (sans doublons)
    if member not in welcome_queue:
        welcome_queue.append(member)

    # Si le cooldown est écoulé, on envoie immédiatement
    if now - last_welcome_time >= WELCOME_COOLDOWN:
        await send_group_message()

# Tâche en arrière-plan pour vider la file d’attente
@tasks.loop(seconds=5)
async def send_welcome_messages():
    global last_welcome_time
    now = time.time()

    if welcome_queue and now - last_welcome_time >= WELCOME_COOLDOWN:
        await send_group_message()

# Fonction pour envoyer un message groupé
async def send_group_message():
    global last_welcome_time
    channel_id = 1004871766201614416  # <-- ID du salon de bienvenue
    channel = bot.get_channel(channel_id)

    if channel and isinstance(channel, discord.TextChannel):
        mentions = " ".join([member.mention for member in welcome_queue])
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
    elif isinstance(channel, discord.ForumChannel):
        print(f"Le canal {channel.name} est un forum. Impossible d'envoyer un message de bienvenue directement.")
    else:
        print(f"Type de canal non supporté ou canal introuvable: {channel}")

# --------- Commandes Discord ---------
#@bot.command()
#async def programme(ctx):
#    await ctx.send(f"""Voilà le programme de la prochaine course {ctx.author.mention} 
#**__Les inscriptions sont closes !__**
#Pavillon à prendre : **ARGENTINA/CATAMARNA PROVINCE**
#Fichier des options : https://framaforms.org/choix-des-options-challenge-pdd-2025-course-ndeg9-la-solitaire-du-figaro-etape-3-1758312895
#Date et heure de fermeture de déclaration et départ : 21/09 17h00
#Date et heure du 1er classement : 22/09 17h00
#Le pavillon est à prendre __avant__ le premier classement
#Classeurs de la Course : :frog: | Tamanart99 - PV / Françoise et :whale: | :blue_square: JulienRo64 :peacock: PV4""")

#@bot.command()
#async def programmeHC(ctx):
#    await ctx.send(f"""Pour l'instant aucune course hors catégorie n'est prévue {ctx.author.mention}
#Si vous avez des idées n'hésitez pas à contacter le CO afin d'organiser une course et la classer""")

#@bot.command()
#async def Challenge(ctx):
#    await ctx.send("""Le challenge PDD consiste en 12 manches étalées sur toute l'année, avec comme condition pour respecter une égalite des chances entre les participants que les options sont limitées à la prime de départ ou bien en monotype choisi par le CO. """)

# --------- Lancement du bot ---------
token = os.environ['TOKEN_BOT']  # mets ton token dans une variable d’environnement
bot.run(token)
