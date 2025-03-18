import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import os

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.guilds = True
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
OWNER_ID = 760949680355278848  # استبدل هذا بمعرفك الشخصي

# -------------------- حدث On Ready --------------------
@bot.event
async def on_ready():
    print(f'✅ {bot.user} متصل بنجاح!')
    try:
        await bot.tree.sync()
        print("✅ تمت مزامنة أوامر السلاش بنجاح!")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تسجيل الأوامر: {e}")

# -------------------- أمر Ping --------------------
@bot.tree.command(name="ping", description="يظهر لك سرعة استجابة البوت")
@bot.command(name="ping")
async def ping(ctx_or_interaction):
    latency = round(bot.latency * 1000)
    if isinstance(ctx_or_interaction, discord.Interaction):
        await ctx_or_interaction.response.send_message(f"Pong! 🏓 {latency}ms")
    else:
        await ctx_or_interaction.send(f"Pong! 🏓 {latency}ms")

# -------------------- أوامر الإدارة --------------------
@bot.tree.command(name="ban", description="حظر عضو")
@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx_or_interaction, member: discord.Member, *, reason: str = "لم يتم تحديد السبب"):
    if member.id == OWNER_ID:
        await ctx_or_interaction.send("❌ لا يمكنك حظر صاحب البوت!")
        return
    await member.ban(reason=reason)
    await ctx_or_interaction.send(f"✅ {member.mention} تم حظره بنجاح!")

@bot.tree.command(name="kick", description="طرد عضو")
@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx_or_interaction, member: discord.Member, *, reason: str = "لم يتم تحديد السبب"):
    if member.id == OWNER_ID:
        await ctx_or_interaction.send("❌ لا يمكنك طرد صاحب البوت!")
        return
    await member.kick(reason=reason)
    await ctx_or_interaction.send(f"✅ {member.mention} تم طرده بنجاح!")

# -------------------- نظام تيكت عبر زر --------------------
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="افتح تيكت", style=discord.ButtonStyle.green)
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = await interaction.guild.create_text_channel(f"🎫-تيكت-{interaction.user.name}")
        await channel.send(f"📩 تم فتح التيكت بواسطة {interaction.user.mention}")
        await interaction.response.send_message(f"✅ تم فتح تيكت جديد: {channel.mention}", ephemeral=True)

@bot.tree.command(name="ticket", description="عرض زر لإنشاء تيكت")
@bot.command(name="ticket")
async def ticket(ctx_or_interaction):
    view = TicketView()
    if isinstance(ctx_or_interaction, discord.Interaction):
        await ctx_or_interaction.response.send_message("اضغط على الزر أدناه لفتح تيكت جديد.", view=view)
    else:
        await ctx_or_interaction.send("اضغط على الزر أدناه لفتح تيكت جديد.", view=view)

# -------------------- تشغيل البوت --------------------

import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')

bot.run(os.getenv('TOKEN'))  # تأكد أن هذا السطر موجود ويستخدم os.getenv
