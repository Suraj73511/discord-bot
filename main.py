import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

class VoidBotClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):
        # Sync slash commands globally
        await self.tree.sync()
        print("Void Bot Slash Commands Synced Successfully!")

bot = VoidBotClient()

@bot.event
async def on_ready():
    print(f"🔥 Void Bot Online as: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="/help | Developed by Suraj"))

# ================= 1. CUSTOM DASHBOARD / HELP COMMAND =================

@bot.tree.command(name="help", description="Void Bot System Commands & Controls")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚡ VOID ENTERPRISE SYSTEM",
        description="Next-gen High-Performance Discord Bot, Developed by **Suraj**.",
        color=0x5865F2
    )
    embed.add_field(name="🛡️ Security & Automod", value="`/backup` • `/restore` • `/antinuke`", inline=False)
    embed.add_field(name="🛠️ Moderation", value="`/kick` • `/ban` • `/timeout` • `/clear`", inline=False)
    embed.add_field(name="📩 Support System", value="`/panel` (Setup Ticket Panel)", inline=False)
    embed.set_footer(text="Void Bot Engine • 100% Uptime")
    
    await interaction.response.send_message(embed=embed)

# ================= 2. PROFESSIONAL SUPPORT TICKET PANEL =================

class VoidTicketLaunch(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Open Support Ticket", style=discord.ButtonStyle.blurple, custom_id="void_ticket")
    async def ticket_btn(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ticket_chan = await guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        
        embed = discord.Embed(
            title="🎫 Void Support Ticket Opened",
            description=f"Welcome {interaction.user.mention}! Support team will assist you shortly.",
            color=0x2ecc71
        )
        await ticket_chan.send(embed=embed)
        await interaction.response.send_message(f"✅ Ticket created: {ticket_chan.mention}", ephemeral=True)

@bot.tree.command(name="panel", description="Deploy Void Support Ticket Panel")
@app_commands.checks.has_permissions(administrator=True)
async def ticket_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌐 VOID ENTERPRISE SUPPORT",
        description="Click the button below to open a private ticket with our management team.",
        color=0x3498db
    )
    await interaction.response.send_message(embed=embed, view=VoidTicketLaunch())

# ================= 3. MODERATION COMMANDS (SLASH) =================

@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.checks.has_permissions(kick_members=True)
async def kick_user(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"🚨 **{member.display_name}** was kicked by Void Security. | Reason: {reason}")

@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.checks.has_permissions(ban_members=True)
async def ban_user(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"⛔ **{member.display_name}** was banned by Void Security. | Reason: {reason}")

@bot.tree.command(name="clear", description="Clear messages from a channel")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear_messages(interaction: discord.Interaction, amount: int = 5):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Cleared {amount} messages!", ephemeral=True)

if __name__ == "__main__":
    if BOT_TOKEN:
        bot.run(BOT_TOKEN)
