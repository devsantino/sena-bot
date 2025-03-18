import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.guilds = True
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

OWNER_ID = 123456789012345678  # استبدل هذا بمعرفك الشخصي

# -------------------- حدث On Ready --------------------
@bot.event
async def on_ready():
    print(f'✅ {bot.user} متصل بنجاح!')
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} أمر سلاش تم تسجيله بنجاح!")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تسجيل الأوامر: {e}")

# -------------------- أمر Ping --------------------
@bot.tree.command(name="ping", description="يظهر لك سرعة استجابة البوت")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! 🏓 {round(bot.latency * 1000)}ms")

@bot.command(name="ping")
async def ping_prefix(ctx):
    await ctx.send(f"Pong! 🏓 {round(bot.latency * 1000)}ms")

# -------------------- أوامر الإدارة --------------------
@bot.tree.command(name="ban", description="حظر عضو")
@commands.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد السبب"):
    if member.id == OWNER_ID:
        await interaction.response.send_message("❌ لا يمكنك حظر صاحب البوت!", ephemeral=True)
        return
    await member.ban(reason=reason)
    await interaction.response.send_message(f"✅ {member.mention} تم حظره بنجاح!")

# -------------------- نظام تيكت متقدم --------------------
class TicketView(discord.ui.View):
    @discord.ui.button(label="افتح تيكت", style=discord.ButtonStyle.green)
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = await interaction.guild.create_text_channel(f"🎫-تيكت-{interaction.user.name}")
        await channel.send(f"📩 تم فتح التيكت بواسطة {interaction.user.mention}")
        await interaction.response.send_message(f"✅ تم فتح تيكت جديد: {channel.mention}", ephemeral=True)

@bot.tree.command(name="ticket", description="افتح تيكت جديد")
async def ticket(interaction: discord.Interaction):
    view = TicketView()
    await interaction.response.send_message("اضغط على الزر أدناه لفتح تيكت جديد.", view=view, ephemeral=True)

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
