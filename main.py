import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import random
import re
from datetime import datetime, timedelta, timezone
import asyncpg


db = None




token = os.getenv("DISCORD_TOKEN")

#Features
features = """**COUNTER**
if jarvis is mentioned add 1 to jarvis_count.txt
up to and including 3 jarvi can be in one message
if there are more than 3 the message is deleted and the jarvi are not counted
if cameron says jarvis it deletes the message and says "Cameron you're ruinin'it" then deletes that after 3 seconds

also if someone says "mraow" it sends a random cat gif from a selection of 10 or 1/100 chance for secret gif :shushing_face:

**COMMANDS**
/jarviscommand - repeats what you say to it
/jarviscoolcommand - admins only - repeats what you say to it with sans and a picture of Darius I found in my downloads
/setjarvi - admins only - lets you set the number of jarvi
/listfeatures - prints this list
/checkperms - lists the permissions the bot has
/kys - admins only - kill the bot and it stops the script completely 
/listbanned - lists banned words
/addbanned - admins only - allows you to add to banned words list
/removebanned - admins only - allows you to remove words from banned words list

**FILTERING**
if you use a word in the banned words list it gets deleted and you're told that word isn't allowed
if you use a dead name the message gets deleted and the bot sends your message but with the deadname replaced

**UPTIME**
*should* turn on at 8am every day adn turn off 15 hours later"""


#meowlist
meows = [
    "meow", "mew", "mewo", "meww", "mewww", "mew~", "meww~",
    "mraow", "mrow", "mrrp", "mrp", "mrrrp", "mrrrow", "mraww",
    "nya", "nyan", "nyah", "nyaa", "nyaaa", "nnya", "nnyah",
    "prrt", "prr", "brrt", "brrrp", "brrp", "rrp", "rrrp",
    "chirp", "chirr", "mewl", "mree", "mrree", "mrrreeow",
    "reeow", "reow", "rowr", "rawr", "rawrr", "reee", "eeow",
    "hiss", "hsss", "hssss", "murr", "murrr", "murmur",
    "purr", "purrr", "purrrr", "blp", "blep", "blep", "brlp",
    "mmrow", "mmrrp", "meeeow", "meeeu", "meuuu", "eow", "owww"
]


#deadnames
DEADNAMES = {"george stanley": "Elle",
             "gs": "E",
             "gsl": "EL",
             "adam": "Ava",
             "<:hahageroe:1083754356203077692>": "Elle"
             }


#cat gif list
def randcat():
    catgifs = {
        1:"https://tenor.com/view/meow-cute-help-gif-12669267",
        2:"https://tenor.com/view/cat-meoooow-meow-trp-trp10-gif-18218658",
        3:"https://tenor.com/view/cat-gif-12756433236776117962",
        4:"https://tenor.com/view/cat-meow-yap-yapping-yapper-gif-743155705889827822",
        5:"https://tenor.com/view/cat-meow-yap-yapping-yapper-gif-743155705889827822",
        6:"https://tenor.com/view/meowsad-catmeme-gif-1923621111806454717",
        7:"https://tenor.com/view/gato-gatinho-explos%C3%A3o-bomba-triste-gif-117092895135057467",
        8:"https://tenor.com/view/gato-gif-8519052141498810062",
        9:"https://tenor.com/view/gato-gif-8519052141498810062",
        10:"https://tenor.com/view/black-sabbath-war-pigs-on-their-knees-the-war-pigs-crawling-cat-meme-gif-832048690152946154"
        }
    if random.randint(1,100) != 100:
        return catgifs[random.randint(1,10)]
    else:
        if random.randint(1,2) == 1:
            return "https://tenor.com/view/get-on-team-fortress2-team-fortress2-gif-23556930"
        else:
            return "https://tenor.com/view/spongebob-backshots-gif-1172518849162068669"
    

#Banned words file
banfile = "banned_words.txt"


deleted_by_bot = set()

async def load_banned_words():
    rows = await db.fetch("SELECT word FROM banned_words;")
    return [row['word'] for row in rows]

async def add_banned_word(word):
    try:
        await db.execute("INSERT INTO banned_words (word) VALUES ($1);", word.lower())
    except asyncpg.UniqueViolationError:
        pass

async def remove_banned_word(word):
    await db.execute("DELETE FROM banned_words WHERE word = $1;", word.lower())





#something to do with slash commands
intents = discord.Intents.default()
intents.message_content = True

#admin perms list me             darius
cool_ids = "764518265778602004 818561900891471943"

#Emojis
sans = "<:sans:1362759699669450892>"
DaddyD = "<:DaddyD:1362761374941315253>"

bot = commands.Bot(command_prefix="!", intents=intents)


#auto turnoff
utc = timezone(timedelta(0))

# get the current time in UTC
start_time = datetime.now(utc)
print("Current time in UTC:", start_time)
end_time = start_time + timedelta(hours=15)
print("Planned turnoff at ", end_time, " or if it reaches 11pm")


count_file = "jarvis_count.txt"

# Prepare Jarvis_Count file
if os.path.exists(count_file):
    with open(count_file, "r") as f:
        jarvis_count = int(f.read())
else:
    jarvis_count = 0


@bot.event
async def on_ready():
    bot.loop.create_task(bedtime_check())
    current_time = datetime.now(timezone.utc)
    desired_start_time = current_time.replace(hour=9, minute=0, second=0, microsecond=0)
    if current_time < desired_start_time:
        print("too early me eepy")
        await client.close()
    else:
        print(f"Logged in as {bot.user}")


    global db
    db = await asyncpg.connect(os.getenv("DATABASE_URL"))
    
    # make sure table exists
    await db.execute("""
        CREATE TABLE IF NOT EXISTS jarvis_data (
            id SERIAL PRIMARY KEY,
            count INTEGER
        );
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS deleted_messages (
        id SERIAL PRIMARY KEY,
        author TEXT,
        content TEXT,
        channel TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS banned_words (
        id SERIAL PRIMARY KEY,
        word TEXT UNIQUE
        );
    """)



    

    


    #something to do with slash commands
    await bot.tree.sync()


@bot.event
async def on_message_delete(message):
    if message.id in deleted_by_bot:
        deleted_by_bot.remove(message.id)
        return

    author = str(message.author)
    content = message.content
    channel = str(message.channel)

    # Optional: Skip logging empty messages (e.g., just an embed)
    if not content.strip():
        return

    # Save to DB
    await db.execute(
        "INSERT INTO deleted_messages (author, content, channel) VALUES ($1, $2, $3);",
        author, content, channel
    )

    print(f"{author} deleted '{content}' in '#{channel}'")



#auto shutoff after 15 hours
@bot.event
async def shutdown_after_hours(hours):
    await asyncio.sleep(hours * 3600)  # 15 hours in seconds
    print("Shutting down bot.")
    await bot.close()

@bot.event
async def bedtime_check():
    await bot.wait_until_ready()
    while not bot.is_closed():
        current_time = datetime.now(timezone.utc)

        # Shut down at exactly midnight UTC
        if current_time.hour == 0 and current_time.minute == 0:
            print("me eepy goodnight")
            await bot.close()
            return

        await asyncio.sleep(60)  # check once every minute



@bot.event
async def on_message(message):



    
    global jarvis_count
    banned_words = load_banned_words()

    #not deleting features
    if message.author == bot.user and features in message.content:
        return

    #if jarvis is mentioned
    if "jarvis" in message.content.lower():
    if str(message.author.id) != "1034087251199656047":
        jarvi_mentioned = message.content.lower().count("jarvis")
        
        if jarvi_mentioned <= 3:
            # Increase count in database
            await db.execute("UPDATE jarvis_data SET count = count + $1 WHERE id = 1;", jarvi_mentioned)
            new_count = await db.fetchval("SELECT count FROM jarvis_data WHERE id = 1;")
            
            await message.channel.send(f"x{new_count}")
        else:
            print(f"{message.author.display_name} said '{message.content}', deleted")
            deleted_by_bot.add(message.id)
            await message.delete()
    else:
        print(f"{message.author.display_name} said '{message.content}', jarvi removed")
        deleted_by_bot.add(message.id)
        await message.delete()

        msg = await message.channel.send(f"""Cameron you're ruinin'it
        {message.author.mention}: {message.content.replace("jarvis", "")}""")
        await asyncio.sleep(3)
        await msg.delete()


    
    #no shitting
    if message.author.bot and any(word in message.content.lower() for word in banned_words):
         return


    if any(word in message.content.lower() for word in banned_words):
        print(f"{message.author.display_name} said '{message.content}', deleted")
        deleted_by_bot.add(message.id)
        await message.delete()
        await message.channel.send(f"{message.author.mention} That word isn't allowed")
        return

    
    #no deadnaming
    if message.author.bot:
        return
    
        
    content = message.content
    edited = content

    for deadname, corrected in DEADNAMES.items():
        if deadname.lower() in content.lower():
            edited = edited.replace(deadname, corrected)

    if edited != content:
        print(f"{message.author.display_name} used deadname: '{message.content}', replaced and resent")
        deleted_by_bot.add(message.id)
        await message.delete()
        await message.channel.send(f"{message.author.mention}: {edited}")

        


    

        


    
            

    
    #mraow
    if any(word in message.content.lower() for word in meows):
        await message.channel.send(randcat())
        if message.content.lower() in meows:
            print(f"{message.author.display_name} said '{message.content}', deleted")
            await message.delete()

    await bot.process_commands(message)


#Commands
@bot.tree.command(name="jarviscommand", description="Repeat your message")
async def JarvisCommand(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)


@bot.tree.command(name="setjarvi", description="set the count of jarvi")
async def SetJarvi(interaction: discord.Interaction, message: int):
    if str(interaction.user.id) in str(cool_ids):
        await db.execute("UPDATE jarvis_data SET count = $1 WHERE id = 1;", message)
        await interaction.response.send_message(f"Jarvis count set to {message}")
    else:
        await interaction.response.send_message("you don't have permission for that 😤")



@bot.tree.command(name="jarviscoolcommand", description="cool command")
async def JarvisCoolCommand(interaction: discord.Interaction, message: str):
    message += sans + DaddyD
    if str(interaction.user.id) in str(cool_ids):
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
    await interaction.response.send_message(features)


@bot.tree.command(name="kys", description="stop the script from running")
async def kys(interaction: discord.Interaction):
    if str(interaction.user.id) in str(cool_ids):
        await interaction.response.send_message(r"\:(")
        await bot.close()
    else:
        await interaction.response.send_message("frick off broski")


@bot.tree.command(name="addbanned", description="add a word to the banned word list")
async def addbanned(interaction: discord.Interaction, word: str):
    if str(interaction.user.id) in str(cool_ids):
        await add_banned_word(word)
        await interaction.response.send_message(f"added {word} to the banned words")
    else:
        await interaction.response.send_message("no perms")

@bot.tree.command(name="removebanned", description="remove a word from the banned word list")
async def removebanned(interaction: discord.Interaction, word: str):
    if str(interaction.user.id) in str(cool_ids):
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





bot.run(token)
