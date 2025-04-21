import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import random
import re
from datetime import datetime, timedelta, timezone
import asyncpg

# database init
db = None
pool = None

# discord token from .env
token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise ValueError("token not found in environment variables")



# meowlist
meows = [
    "meow", "mew", "mewo", "meww", "mewww", "mew~", "meww~",
    "mraow", "mrow", "mrrp", "mrp", "mrrrp", "mrrrow", "mraww",
    "nya", "nyan", "nyah", "nyaa", "nyaaa", "nnya", "nnyah",
    "prrt", "prr", "brrt", "brrrp", "brrp", "rrp", "rrrp",
    "chirp", "chirr", "mewl", "mree", "mrree", "mrrreeow",
    "reeow", "reow", "rowr", "rawr", "rawrr", "reee", "eeow",
    "hiss", "hsss", "hssss", "murr", "murrr", "murmur",
    "purr", "purrr", "purrrr", "blp", "blep", "meoww", "brlp",
    "mmrow", "mmrrp", "meeeow", "meeeu", "meuuu", "eow", "owww",
    "UwU", "Jamie"
]


# Features docs
features = """**JARVI COUNTER**
if jarvis is mentioned add 1 to jarvis count
up to and including 3 jarvi can be in one message
if there are more than 3 the message is deleted and the jarvi are not counted
if cameron says jarvis it deletes the message and says "Cameron you're ruinin'it" then deletes that after 3 seconds

also if someone says any sort of cat noise it sends a random cat gif from a selection of 10 or 1/100 chance for secret gif :shushing_face:

**COMMANDS**
/jarviscommand - repeats what you say to it
/jarviscoolcommand - admins only - repeats what you say to it with sans and a picture of Darius I found in my downloads
/setjarvi - admins only - lets you set the number of jarvi
/listfeatures - prints this list
/checkperms - lists the permissions the bot has
/kys - admins only - kill the bot by stopping the script completely 
/listbanned - lists banned words
/addbanned - admins only - allows you to add to banned words list
/removebanned - admins only - allows you to remove words from banned words list
/mewo - lists cat noises

**FILTERING**
if you use a word in the banned words list it gets deleted and you're told that word isn't allowed
if you use a dead name the message gets deleted and the bot sends your message but with the deadname replaced
(unless you say george because cameron is pissy like that)

**UPTIME**
*should* be on at all times"""


# deadnames
DEADNAMES = {"george stanley": "Elle",
             " gs": "E",
             "gsl": "EL",
             "adam": "Ava",
             "<:hahageroe:1083754356203077692>": "Elle",
             }

# generate random cat
def randcat():
    catgifs = {
        1: "https://tenor.com/view/meow-cute-help-gif-12669267",
        2: "https://tenor.com/view/cat-meoooow-meow-trp-trp10-gif-18218658",
        3: "https://tenor.com/view/cat-gif-12756433236776117962",
        4: "https://tenor.com/view/cat-meow-yap-yapping-yapper-gif-743155705889827822",
        5: "https://tenor.com/view/cat-you-play-like-a-cat-play-like-a-cat-mrrp-mrp-gif-9789205383530168734",
        6: "https://tenor.com/view/meowsad-catmeme-gif-1923621111806454717",
        7: "https://tenor.com/view/gato-gatinho-explos%C3%A3o-bomba-triste-gif-117092895135057467",
        8: "https://tenor.com/view/gato-gif-8519052141498810062",
        9: "https://tenor.com/view/kitty-kittyjump-excited-kitty-meow-meowhyuck-gif-11696392138403281635",
        10: "https://tenor.com/view/black-sabbath-war-pigs-on-their-knees-the-war-pigs-crawling-cat-meme-gif-832048690152946154",
        11: "https://cdn.discordapp.com/attachments/1017831546633334916/1363530849630425108/Screenshot_20250416-125042.png?ex=68065e8f&is=68050d0f&hm=0e907944bb912980e39ce912c320f60afa0c7c4b7fbd2d31ebe706e328c92705&",
        12: "https://tenor.com/view/neuro-sama-evil-neuro-bounce-vedal987-neuro-gif-11513855482341596679",
        13: "https://tenor.com/view/floppa-spy-tf2-valve-team-fortress-gif-19751193",
        14: "https://tenor.com/view/cat-cat-meme-cat-hug-cat-kiss-kiss-gif-7995560765945148820",
        15: "https://tenor.com/en-GB/view/filian-embed-fail-gif-27021762", #supposed to be embed fail
        16: "https://tenor.com/view/neuro-sama-neuro-sama-neuro-sama-vtuber-neuro-neuro-vtuber-gif-16392526205380439187",
        17: "https://tenor.com/view/neuro-neuro-sama-cat-overlord-neuro-sama-gif-9439092095145078224",
        18: "https://tenor.com/view/cat-internecion-cube-kirie-gif-20069182",
        19: "https://tenor.com/view/meme-cat-kitten-gif-17926206283727080180"
    }
    raregifs = {
        1: "https://tenor.com/view/neuro-sama-ai-vtuber-suspicious-dubious-gif-10363453030530375437",
        2: "https://tenor.com/view/get-on-team-fortress2-team-fortress2-gif-23556930",
        3: "https://tenor.com/view/spongebob-backshots-gif-1172518849162068669",
        4: "https://tenor.com/view/furry-anti-furry-furrys-when-the-springlocks-start-activating-gif-3295430340879895358",
        5: "https://tenor.com/view/hatsune-miku-meme-gif-8373983160467407608",
        6: "https://tenor.com/view/dark-urge-shadowheart-baldur's-gate-3-hop-on-baldur's-gate-3-kiss-gif-3266055874247923337",
        7: "https://tenor.com/view/sans-undertale-gif-11943201415334364081",
        8: "https://tenor.com/view/mcdonalds-flexing-gainz-showing-muscles-i'm-loving-it-gif-8562390891048052730",
        9: "https://tenor.com/view/pom-pom-purin-hi-omc-gif-16553892039548589920",
        10: "https://tenor.com/view/arcadum-maid-cosplay-pose-sexy-gif-22612502",
        11: "https://tenor.com/view/shy-among-us-sussy-baka-yellow-uwu-face-gif-27368757",
        12: "https://tenor.com/view/gopher-darius-screaming-excited-screaming-gif-9632076301582127705",
        13: "https://tenor.com/view/fnaf-five-nights-at-freddy's-gif-4059222196466761933",
        14: "https://tenor.com/view/circus-baby-cursed-fnaf-gif-18818734",
        15: "(I was under orders, I had no choice) https://tenor.com/view/furry-hopon-gif-25273193",
        16: "https://tenor.com/view/neurosama-explosion-vedal-gif-10953604243590119044",
        17: "Me when rare gif: https://tenor.com/view/yippee-creature-meme-party-yay-gif-4844138631754730183",
        18: "https://tenor.com/view/gaslight-gatekeep-girlboss-gaslight-gatekeep-girlboss-freddy-fazbear-gif-25108236",
        19: "https://tenor.com/view/anime-waifu-dance-gif-25689550",
        20: "Keep meowing :D https://tenor.com/view/niffty-niffty-hazbin-hazbin-hotel-jump-stim-gif-568824074923902625",
        21: "Me as I keep adding these: https://tenor.com/view/ghostedvpn-hacker-cat-bongo-cat-keyboard-cat-hacker-gif-4373606555250453292",
        22: "https://tenor.com/view/i-am-only-one-man's-girl-his-name-is-jesus-christ-belong-to-jesus-jesus-christ-not-until-mariage-gif-16757286860798336335",
        23: "https://tenor.com/view/matpat-game-theory-jumpscare-gif-17715187260881724719",
        24: "https://tenor.com/view/inscryption-stoat-total-misplay-card-gif-24910264",
        25: "https://tenor.com/view/pipe-bomb-miku-pipe-bomb-miku-silly-miku-silly-miku-pipe-bomb-gif-14794310888550215845",
        26: "https://tenor.com/view/anomalous-activities-gif-24758355",
        27: "https://tenor.com/view/jesus-ballin-mars-bars-gif-19910027",
        28: "(Jk keep meowing) https://tenor.com/view/glory-wings-of-fire-wof-rainwing-skywing-gif-3751720425011732308",
        29: "HelpMySoulIsStuckInTheBot",
        30: "https://www.youtube.com/@victoriabrides7860",
        31: "https://tenor.com/view/murder-drones-khan-doorman-khan-murder-drones-doors-i-love-doors-gif-6067845957534950832",
        32: "https://tenor.com/view/spinning-spin-rotate-rotating-twirl-gif-27369778",
        33: "https://tenor.com/view/barotrauma-gif-24233534",
        34: "https://tenor.com/view/lethal-company-gaming-gamer-dance-jig-jiggy-gif-16548737736878595145",
        35: "https://tenor.com/view/war-gif-991293921595200744"
    }


    if random.randint(1, 100) >= 90:
        return raregifs[random.randint(1, len(raregifs))]

    else:
        return catgifs[random.randint(1, len(catgifs))]



async def ensure_db_connection():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))


async def load_banned_words():
    await ensure_db_connection()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT word FROM banned_words;")
    return [row["word"] for row in rows]


async def add_banned_word(word):
    await ensure_db_connection()
    async with pool.acquire() as conn:
        try:
            await conn.execute("INSERT INTO banned_words (word) VALUES ($1);", word.lower())
        except asyncpg.UniqueViolationError:
            pass


async def remove_banned_word(word):
    await ensure_db_connection()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM banned_words WHERE word = $1;", word.lower())


# something to do with slash commands
intents = discord.Intents.default()
intents.message_content = True

# admin perms list
cool_ids = ["764518265778602004", "818561900891471943"]

# Emojis
sans = "<:sans:1362759699669450892>"
DaddyD = "<:DaddyD:1362761374941315253>"


# non slash commands
bot = commands.Bot(command_prefix="!", intents=intents)


jarvis_count = 0


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # database setup
    await ensure_db_connection()

    async with pool.acquire() as conn:
        # make sure table exists
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS jarvis_data (
                id SERIAL PRIMARY KEY,
                count INTEGER
            );
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS banned_words (
            id SERIAL PRIMARY KEY,
            word TEXT UNIQUE
            );
        """)

        # make sure there's a row with id = 1
        existing = await conn.fetchval("SELECT count FROM jarvis_data WHERE id = 1;")
        if existing is None:
            await conn.execute("INSERT INTO jarvis_data (id, count) VALUES (1, 0);")

    # something to do with slash commands
    await bot.tree.sync()


@bot.event
async def on_message(message):
    lower_message = message.content.lower()

    global jarvis_count
    banned_words = await load_banned_words()

    # not deleting features
    if message.author == bot.user and features in message.content:
        return

    # if jarvis is mentioned
    if "jarvis" in lower_message:
        if str(message.author.id) != "1034087251199656047":
            jarvi_mentioned = lower_message.count("jarvis")
        
            if jarvi_mentioned <= 3:
                # Increase count in database
                async with pool.acquire() as conn:
                    await conn.execute("UPDATE jarvis_data SET count = count + $1 WHERE id = 1;", jarvi_mentioned)
                    new_count = await conn.fetchval("SELECT count FROM jarvis_data WHERE id = 1;")
                
                await message.channel.send(f"x{new_count}")
            else:
                print(f"{message.author.display_name} said '{message.content}', deleted")
                
                await message.delete()
        else:
            print(f"{message.author.display_name} said '{message.content}', jarvi removed")
            
            await message.delete()

            msg = await message.channel.send(f"""Cameron you're ruinin'it
            {message.author.mention}: {message.content.replace("jarvis", "")}""")
            await asyncio.sleep(3)
            await msg.delete()

    #! no badwords
    if not message.author.bot and any(word in lower_message for word in banned_words):
        print(f"{message.author.display_name} said '{message.content}', deleted")
        
        await message.author.send(f"{message.author.mention} That word isn't allowed and can be extremely triggering for people. please avoid using it in future.")
        return

    #! no deadnaming
    content = message.content
    edited = content
    name = None 

    for deadname, corrected in DEADNAMES.items():
        name = corrected
        edited = re.sub(re.escape(deadname), corrected, edited, flags=re.IGNORECASE)

    if edited != content:
        print(f"{message.author.display_name} used deadname: '{message.content}', replaced and resent")
        
        await message.author.send("please refrain from using that name, **{name}** is preferred)

    # mraow
    if any(word in lower_message for word in meows) and not message.author.bot:
        msg = randcat()
        bot_msg = await message.channel.send(msg)
        if msg == "(At Elle's request. I was under orders, I had no choice) https://tenor.com/view/furry-hopon-gif-25273193":
            await asyncio.sleep(3)
            await bot_msg.edit(content="https://tenor.com/view/furry-hopon-gif-25273193")
        if msg == "https://tenor.com/en-GB/view/filian-embed-fail-gif-27021762":
            await asyncio.sleep(5)
            await bot_msg.edit(content="Wait, no... https://tenor.com/en-GB/view/filian-embed-fail-gif-27021762")
            await asyncio.sleep(5)
            await bot_msg.edit(content="https://tenor.com/view/filian-gif-18304054096777899760")
        if msg == "HelpMySoulIsStuckInTheBot":
            await asyncio.sleep(3)
            await message.channel.send("ItsDarkInHere")

    # make sure it still processes commands
    await bot.process_commands(message)


# Commands
@bot.tree.command(name="jarviscommand", description="Repeat your message")
async def JarvisCommand(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)


@bot.tree.command(name="setjarvi", description="set the count of jarvi")
async def SetJarvi(interaction: discord.Interaction, message: int):
    if str(interaction.user.id) in cool_ids:
        async with pool.acquire() as conn:
            await conn.execute("UPDATE jarvis_data SET count = $1 WHERE id = 1;", message)
        await interaction.response.send_message(f"Jarvis count set to {message}")
    else:
        await interaction.response.send_message("you don't have permission for that")


@bot.tree.command(name="jarviscoolcommand", description="cool command")
async def JarvisCoolCommand(interaction: discord.Interaction, message: str):
    message += sans + DaddyD
    if str(interaction.user.id) in cool_ids:
        await interaction.response.send_message(message)


@bot.tree.command(name="checkperms", description="Check the bot's permissions in this channel")
async def checkperms(interaction: discord.Interaction):
    channel = interaction.channel
    guild = interaction.guild
    bot_member = guild.me

    perms = channel.permissions_for(bot_member)
    await interaction.response.send_message(f"Bot permissions in this channel:\n```{perms}```")


@bot.tree.command(name="listfeatures", description="view feature list")
async def listfeatures(interaction: discord.Interaction):
    await interaction.response.send_message(features, ephemeral=true)


@bot.tree.command(name="kys", description="stop the script from running")
async def kys(interaction: discord.Interaction):
    if str(interaction.user.id) in cool_ids:
        await interaction.response.send_message(r"\:(")
        await bot.close()
    else:
        await interaction.response.send_message("frick off broski")


@bot.tree.command(name="addbanned", description="add a word to the banned word list")
async def addbanned(interaction: discord.Interaction, word: str):
    if str(interaction.user.id) in cool_ids:
        await add_banned_word(word)
        await interaction.response.send_message(f"added {word} to the banned words")
    else:
        await interaction.response.send_message("no perms")


@bot.tree.command(name="removebanned", description="remove a word from the banned word list")
async def removebanned(interaction: discord.Interaction, word: str):
    if str(interaction.user.id) in cool_ids:
        await remove_banned_word(word)
        await interaction.response.send_message(f"removed {word} from banned words")
    else:
        await interaction.response.send_message("no perms")


@bot.tree.command(name="listbanned", description="list banned words")
async def listbanned(interaction: discord.Interaction):
    banned_words = await load_banned_words()
    if not banned_words:
        await interaction.response.send_message("there are no banned words")
    else:
        await interaction.response.send_message(f"Banned words: {', '.join(banned_words)}")

@bot.tree.command(name="mewo", description="list cat noises")
async def mewo(interaction: discord.Interaction):
    await interaction.response.send_message(meows, ephemeral=True)

bot.run(token)
