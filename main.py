import os
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI
import google.generativeai as genai
import discord
from discord.ext import commands

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Void Bot & API Active"}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Void Bot online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # AI Chat with Mention or DM
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if not prompt:
            prompt = "Hello"
            
        try:
            # Desi Gamer Friend Persona Prompt Setup
            sys_prompt = f"Act as a witty, casual gamer friend speaking Hinglish. Answer this: {prompt}"
            res = ai_model.generate_content(sys_prompt)
            await message.channel.send(res.text)
        except Exception as e:
            await message.channel.send(f"Bhai koi dikkat aayi: {e}")
        return

    await bot.process_commands(message)

# Moderation Commands
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"🔥 {member.mention} ko kick kar diya gaya. Reason: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"⛔ {member.mention} ko ban kar diya gaya. Reason: {reason}")

@app.on_event("startup")
async def startup_event():
    if BOT_TOKEN:
        asyncio.create_task(bot.start(BOT_TOKEN))

