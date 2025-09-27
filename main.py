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
async def on_member_join(member):
    global last_welcome_time
    now = time.time()

    # Message privé (toujours envoyé)
    try:
        await member.send(f"Bienvenue sur le serveur, {member.name} ! 🎉")
    except:
        print("Impossible d’envoyer un DM à ce membre.")

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
    channel_id = 740604309552758785  # <-- ID du salon de bienvenue
    channel = bot.get_channel(channel_id)

    if channel and isinstance(channel, discord.TextChannel):
        mentions = " ".join([member.mention for member in welcome_queue])
        await channel.send(f"""Bienvenue {mentions} sur le serveur discord du Challenge PDD
        Tout d'abord pour pouvoir participer à notre Challenge :
        Nous t'invitons à lire le réglement en entier ici <#{Reglement_id}> pour le reglement des courses ainsi que des records
        De plus il faut que ton pseudo Discord soit identique à ton pseudo VR (avec un préfixe pour les équipes et un slash pour un hypothétique prénom)
        Également tu trouveras une distinction avec les courses Hors catégorie qui sont des courses qui ne comptent pas pour le challenge mais classé tout de même par des membres et si tu veux en faire partir n'hésite pas à contacter Aka45
        En ce qui concerne les courses directement les inscriptions se font par un formulaire diffusé généralement 5-6 jours avant le départ puis la veille du départ un fichier pour sélectionner ses options est diffusé
        Si toute fois tu cherches une information n'hésites pas à regarder dans les messages épinglés ou bien a poser des questions nous ne mangeons que des rations de navigations mais pas de dopants à la sauce VR
        Au plaisir de te voir sur les flots avec nous""")
        welcome_queue.clear()
        last_welcome_time = time.time()
    elif isinstance(channel, discord.ForumChannel):
        print(f"Le canal {channel.name} est un forum. Impossible d'envoyer un message de bienvenue directement.")
    else:
        print(f"Type de canal non supporté ou canal introuvable: {channel}")

# --------- Commandes Discord ---------
@bot.command()
async def programme(ctx):
    await ctx.send(f"""Voilà le programme de la prochaine course {ctx.author.mention} 
**__Les inscriptions sont closes !__**
Pavillon à prendre : **ARGENTINA/CATAMARNA PROVINCE**
Fichier des options : https://framaforms.org/choix-des-options-challenge-pdd-2025-course-ndeg9-la-solitaire-du-figaro-etape-3-1758312895
Date et heure de fermeture de déclaration et départ : 21/09 17h00
Date et heure du 1er classement : 22/09 17h00
Le pavillon est à prendre __avant__ le premier classement
Classeurs de la Course : :frog: | Tamanart99 - PV / Françoise et :whale: | :blue_square: JulienRo64 :peacock: PV4""")

@bot.command()
async def programmeHC(ctx):
    await ctx.send(f"""Pour l'instant aucune course hors catégorie n'est prévue {ctx.author.mention}
Si vous avez des idées n'hésitez pas à contacter le CO afin d'organiser une course et la classer""")

@bot.command()
async def Challenge(ctx):
    await ctx.send("""Le challenge PDD consiste en 12 manches étalées sur toute l'année, avec comme condition pour respecter une égalite des chances entre les participants que les options sont limitées à la prime de départ ou bien en monotype choisi par le CO. """)

# --------- Lancement du bot ---------
token = os.environ['TOKEN_TEST']  # mets ton token dans une variable d’environnement
bot.run(token)
