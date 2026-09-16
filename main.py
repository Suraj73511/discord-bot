import os
import json
import asyncio
import random
import io
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from fastapi import FastAPI
import google.generativeai as genai
import discord
from discord.ext import commands
from discord.ui import Button, View

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    # Model name set to gemini-3.6-flash
    ai_model = genai.GenerativeModel('gemini-3.6-flash')

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Void Enterprise Bot Active"}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Memory Storage
server_backups = {}
user_games = {}
server_data_memory = {}

@bot.event
async def on_ready():
    print(f"Void Bot online as {bot.user}")

# 1. ANTI-NUKE GUARD
@bot.event
async def on_member_join(member):
    if member.bot:
        async for entry in member.guild.audit_logs(action=discord.AuditLogAction.BOT_ADD, limit=1):
            if entry.user.id != member.guild.owner_id:
                try:
                    await member.kick(reason="Nuke Guard: Unauthorized Bot Addition")
                    print(f"Nuke Guard Kicked: {member.name}")
                except Exception as e:
                    print(f"Nuke Guard Error: {e}")

# 2. CHAT, AUTOMOD & DIRECT PHOTO ENGINE
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Process Direct Commands (!backup, !panel, !kick, etc.)
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    guild_id = str(message.guild.id) if message.guild else "DM"
    text = message.content.strip().lower()

    # Log Server Messages
    if guild_id not in server_data_memory:
        server_data_memory[guild_id] = []
    server_data_memory[guild_id].append({
        "user_id": message.author.id,
        "username": message.author.name,
        "content": message.content,
        "timestamp": datetime.utcnow().isoformat()
    })
    if len(server_data_memory[guild_id]) > 500:
        server_data_memory[guild_id].pop(0)

    # DIRECT WORKING PHOTO GENERATION (File Attachment)
    if text.startswith("/imagine") or any(w in text for w in ["photo", "image", "pic", "tasveer"]):
        query = text.replace("/imagine", "").replace("photo", "").replace("image", "").replace("pic", "").replace("tasveer", "").strip() or "cyberpunk gaming"
        async with message.channel.typing():
            try:
                img_url = f"https://pollinations.ai/p/{urllib.parse.quote(query)}?width=800&height=800&seed={random.randint(1, 99999)}"
                req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    img_bytes = response.read()
                
                picture = discord.File(io.BytesIO(img_bytes), filename="image.png")
                await message.reply(content=f"🖼️ **Photo Generated:** `{query}`", file=picture)
            except Exception as e:
                await message.reply("❌ Photo generate karne me dikkat aayi, dobara try karo!")
        return

    # Past Record Query
    if any(phrase in text for phrase in ["mere bare me bata", "mera past record", "main kaisa hu", "my record"]):
        user_id = message.author.id
        last_msg = None
        async for msg in message.channel.history(limit=100):
            if msg.author.id == user_id and msg.id != message.id:
                last_msg = msg
                break

        if last_msg:
            msg_count = sum(1 for log in server_data_memory.get(guild_id, []) if log["user_id"] == user_id)
            await last_msg.reply(f"🔥 **Past Record:** Is server par tere ~{msg_count} messages logged hain.")
        else:
            await message.channel.send(f"Bhai {message.author.mention}, tera past record clean hai!")
        return

    # Game Context Logic
    user_id = message.author.id
    games_list = ["pubg", "bgmi", "free fire", "ff", "grand mobile", "gta", "valorant", "cod"]
    mentioned_game = next((g for g in games_list if g in text), None)
    
    if mentioned_game:
        user_games[user_id] = mentioned_game.upper()
    current_game = user_games.get(user_id)

    # AI CHAT - SHORT & STRICT PERSONALITY (NO FALTU BAKWAS)
    try:
        sys_prompt = f"""
        You are Void Bot. Your ONLY creator, developer, and boss is SURAJ.
        
        RULES:
        1. If asked about developer/creator/owner/Suraj, strictly state that SURAJ is your sole developer and boss who coded you. NEVER mention Google or anyone else.
        2. Keep replies VERY SHORT, DIRECT, and POINT-TO-POINT. Do NOT talk unnecessary extra stuff!
        3. Respond in the language used by user (Garhwali, Kumaoni, Sanskrit, Hindi, English).
        4. If user is abusive, reply back with a quick matching roast.
        5. Game context: {current_game if current_game else 'Not specified'}.
        
        User Message: {message.content}
        """
        res = ai_model.generate_content(
            sys_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=150
            )
        )
        await message.channel.send(res.text)
    except Exception as e:
        await message.channel.send(f"Bhai dikkat: {e}")

# ================= 3. DISCORD MANAGEMENT COMMANDS =================

@bot.command()
async def backup(ctx):
    guild = ctx.guild
    server_backups[str(guild.id)] = {
        "roles": [r.name for r in guild.roles if r.name != "@everyone"],
        "text_channels": [c.name for c.text_channels],
        "voice_channels": [v.name for v.voice_channels]
    }
    await ctx.send("💾 **Backup Completed!** Roles & channels backup successfully saved.")

@bot.command()
async def restore(ctx):
    guild = ctx.guild
    data = server_backups.get(str(guild.id))
    if not data:
        await ctx.send("❌ Pehle `!backup` chalao, koi backup nahi mila!")
        return

    await ctx.send("🔄 **Restoring Server Structure...**")
    for r_name in data["roles"]:
        if not discord.utils.get(guild.roles, name=r_name):
            try:
                await guild.create_role(name=r_name)
            except Exception:
                pass
    for c_name in data["text_channels"]:
        if not discord.utils.get(guild.text_channels, name=c_name):
            try:
                await guild.create_text_channel(name=c_name)
            except Exception:
                pass
    await ctx.send("✅ **Server Restoration Completed!**")

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Create Ticket", style=discord.ButtonStyle.primary, custom_id="create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ticket_chan = await guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        await interaction.response.send_message(f"✅ Ticket created: {ticket_chan.mention}", ephemeral=True)
        await ticket_chan.send(f"👋 Welcome {interaction.user.mention}! Support team will assist you shortly.")

@bot.command()
async def panel(ctx):
    embed = discord.Embed(title="Interactive Support Tickets", description="Click below to open a private ticket.", color=0x3498db)
    await ctx.send(embed=embed, view=TicketView())

@bot.command()
async def giveaway(ctx, duration: int = 10, *, prize: str = "VIP Role"):
    embed = discord.Embed(title="🎉 GIVEAWAY 🎉", description=f"Prize: **{prize}**\nTime: {duration} seconds!\nReact with 🎉 to enter!", color=0xe74c3c)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")
    await asyncio.sleep(duration)
    
    new_msg = await ctx.channel.fetch_message(msg.id)
    users = [u for u in await new_msg.reactions[0].users().flatten() if not u.bot]
    if users:
        winner = random.choice(users)
        await ctx.send(f"🎊 Congratulations {winner.mention}, you won **{prize}**!")
    else:
        await ctx.send("Nobody entered the giveaway.")

@bot.command()
async def serverdata(ctx):
    records = server_data_memory.get(str(ctx.guild.id), [])
    await ctx.send(f"📊 **Privacy Log:** Total {len(records)} recent messages recorded.")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    try:
        await member.kick(reason=reason)
        await ctx.send(f"🚨 **{member.display_name}** kicked!")
    except Exception as e:
        await ctx.send(f"❌ Kick error: {e}")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    try:
        await member.ban(reason=reason)
        await ctx.send(f"⛔ **{member.display_name}** banned!")
    except Exception as e:
        await ctx.send(f"❌ Ban error: {e}")

@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int = 10):
    try:
        duration = timedelta(minutes=minutes)
        await member.timeout(duration)
        await ctx.send(f"🤫 **{member.display_name}** timed out for {minutes}m.")
    except Exception as e:
        await ctx.send(f"❌ Timeout error: {e}")

@bot.command()
async def createchannel(ctx, name: str, channel_type: str = "text"):
    guild = ctx.guild
    try:
        if channel_type.lower() == "voice":
            await guild.create_voice_channel(name)
            await ctx.send(f"🔊 Voice Channel **{name}** created!")
        else:
            await guild.create_text_channel(name)
            await ctx.send(f"💬 Text Channel **#{name}** created!")
    except Exception as e:
        await ctx.send(f"❌ Channel error: {e}")

@app.on_event("startup")
async def startup_event():
    if BOT_TOKEN:
        asyncio.create_task(bot.start(BOT_TOKEN))

