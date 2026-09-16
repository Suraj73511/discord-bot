import os
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI
import google.generativeai as genai
import discord
from discord.ext import commands
from discord.ui import Button, View

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    # Model name updated to gemini-3.6-flash
    ai_model = genai.GenerativeModel('gemini-3.6-flash')

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Void Enterprise Ultra Bot Active"}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# In-Memory Storage
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

# 2. AUTOMOD, AI CHAT & PAST RECORD SYSTEM
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Process Direct Commands (!kick, !ban, !panel etc.)
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    guild_id = str(message.guild.id) if message.guild else "DM"
    text = message.content.strip().lower()

    # Log Server Messages (Owner Privacy Record)
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

    # Image Request / Imagine Art
    if text.startswith("/imagine") or any(w in text for w in ["photo", "image", "pic", "tasveer"]):
        query = text.replace("/imagine", "").replace("photo", "").replace("image", "").strip() or "cyberpunk gaming"
        image_url = f"https://source.unsplash.com/featured/?{query},gaming"
        await message.channel.send(f"🖼️ **AI Imagine Art:**\n{image_url}")
        return

    # Past Record & Reply Tag Logic
    if any(phrase in text for phrase in ["mere bare me bata", "mera past record", "main kaisa hu", "my record"]):
        user_id = message.author.id
        last_msg = None
        async for msg in message.channel.history(limit=100):
            if msg.author.id == user_id and msg.id != message.id:
                last_msg = msg
                break

        if last_msg:
            msg_count = sum(1 for log in server_data_memory.get(guild_id, []) if log["user_id"] == user_id)
            await last_msg.reply(f"🔥 **Past Record:** Is server par tere ~{msg_count} messages logged hain. Bada proof ye raha:")
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

    if not current_game and any(kw in text for kw in ["game", "play", "senso", "headshot", "rank"]):
        await message.channel.send("Bhai pehle bata kaunsa game khelta hai? (Free Fire, BGMI, Grand Mobile, GTA etc.) Uske baad tips deta hu!")
        return

    # Gemini 3.6 Flash Multi-Language & Abuse Persona
    try:
        sys_prompt = f"""
        You are Void Bot, a witty Hinglish gamer friend.
        - Respond in the language used by user (Supports Garhwali, Kumaoni, Sanskrit, Hindi, English).
        - Translate accurately if requested.
        - Be friendly by default.
        - IF AND ONLY IF the user uses abuses or toxic language, reply back matching their abusive roast tone.
        - User Game: {current_game if current_game else 'Not specified'}.
        User message: {message.content}
        """
        res = ai_model.generate_content(sys_prompt)
        await message.channel.send(res.text)
    except Exception as e:
        await message.channel.send(f"Bhai dikkat: {e}")

# ================= 3. INSTANT BACKUP & RESTORE =================

@bot.command()
async def backup(ctx):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("🔒 Only Server Owner can backup server structure.")
        return
    
    guild = ctx.guild
    server_backups[str(guild.id)] = {
        "roles": [r.name for r in guild.roles if r.name != "@everyone"],
        "text_channels": [c.name for c.text_channels],
        "voice_channels": [v.name for v.voice_channels]
    }
    await ctx.send("💾 **Nuke Guard Backup Completed!** Server structure saved.")

@bot.command()
async def restore(ctx):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("🔒 Only Server Owner can perform One-Click Restore.")
        return
    
    guild = ctx.guild
    data = server_backups.get(str(guild.id))
    if not data:
        await ctx.send("❌ No backup found. Run `!backup` first.")
        return

    await ctx.send("🔄 **Restoring Server...**")
    for r_name in data["roles"]:
        if not discord.utils.get(guild.roles, name=r_name):
            await guild.create_role(name=r_name)
    for c_name in data["text_channels"]:
        if not discord.utils.get(guild.text_channels, name=c_name):
            await guild.create_text_channel(name=c_name)
    await ctx.send("✅ **One-Click Restore Completed!**")

# ================= 4. SUPPORT TICKET SYSTEM =================

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
@commands.has_permissions(administrator=True)
async def panel(ctx):
    embed = discord.Embed(title="Interactive Support Tickets", description="Click below to open a private ticket.", color=0x3498db)
    await ctx.send(embed=embed, view=TicketView())

# ================= 5. MODERATION & SERVER DATA =================

@bot.command()
async def serverdata(ctx):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("🔒 Only Server Owner can access server log records.")
        return
    records = server_data_memory.get(str(ctx.guild.id), [])
    await ctx.send(f"📊 **Privacy Log:** Total {len(records)} recent messages securely recorded.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    await member.kick(reason=reason)
    await ctx.send(f"🚨 **{member.display_name}** kicked!")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason)
    await ctx.send(f"⛔ **{member.display_name}** banned!")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int = 10):
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration)
    await ctx.send(f"🤫 **{member.display_name}** timed out for {minutes}m.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def createchannel(ctx, name: str, channel_type: str = "text"):
    guild = ctx.guild
    if channel_type.lower() == "voice":
        await guild.create_voice_channel(name)
        await ctx.send(f"🔊 Voice Channel **{name}** created!")
    else:
        await guild.create_text_channel(name)
        await ctx.send(f"💬 Text Channel **#{name}** created!")

@app.on_event("startup")
async def startup_event():
    if BOT_TOKEN:
        asyncio.create_task(bot.start(BOT_TOKEN))
