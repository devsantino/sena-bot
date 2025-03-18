import discord
from discord import app_commands
from discord.ext import commands
import asyncio

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
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} أمر سلاش تم تسجيله بنجاح!")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تسجيل الأوامر: {e}")

# -------------------- أمر Ping --------------------
@bot.tree.command(name="ping", description="يظهر لك سرعة استجابة البوت")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! 🏓 {round(bot.latency * 1000)}ms")

# -------------------- أوامر الإدارة --------------------
@bot.tree.command(name="ban", description="حظر عضو")
@commands.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد السبب"):
    if member.id == OWNER_ID:
        await interaction.response.send_message("❌ لا يمكنك حظر صاحب البوت!", ephemeral=True)
        return
    await member.ban(reason=reason)
    await interaction.response.send_message(f"✅ {member.mention} تم حظره بنجاح!")

@bot.tree.command(name="kick", description="طرد عضو")
@commands.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد السبب"):
    if member.id == OWNER_ID:
        await interaction.response.send_message("❌ لا يمكنك طرد صاحب البوت!", ephemeral=True)
        return
    await member.kick(reason=reason)
    await interaction.response.send_message(f"✅ {member.mention} تم طرده بنجاح!")

# -------------------- نظام تيكت متقدم --------------------
@bot.tree.command(name="ticket", description="افتح تيكت جديد")
async def ticket(interaction: discord.Interaction, نوع_الطلب: str):
    channel = await interaction.guild.create_text_channel(f"🎫-{نوع_الطلب}-{interaction.user.name}")
    await channel.send(f"📩 تم فتح التيكت بواسطة {interaction.user.mention}")
    await interaction.response.send_message(f"✅ تم فتح تيكت جديد: {channel.mention}", ephemeral=True)

# -------------------- نظام 'on duty' --------------------
on_duty_admins = []

@bot.tree.command(name="on_duty", description="حدد نفسك كإداري في الخدمة")
async def on_duty(interaction: discord.Interaction):
    if interaction.user.id not in on_duty_admins:
        on_duty_admins.append(interaction.user.id)
        await interaction.response.send_message(f"✅ {interaction.user.mention} الآن في الخدمة!", ephemeral=True)
    else:
        await interaction.response.send_message("❗ أنت بالفعل في الخدمة.", ephemeral=True)

@bot.tree.command(name="off_duty", description="قم بإلغاء حالتك كإداري في الخدمة")
async def off_duty(interaction: discord.Interaction):
    if interaction.user.id in on_duty_admins:
        on_duty_admins.remove(interaction.user.id)
        await interaction.response.send_message(f"❌ {interaction.user.mention} خرج من الخدمة!", ephemeral=True)
    else:
        await interaction.response.send_message("❗ أنت لست في الخدمة.", ephemeral=True)

# -------------------- نظام إشعارات تلقائي --------------------
@bot.tree.command(name="announce", description="إرسال إعلان إلى قناة محددة")
@commands.has_permissions(administrator=True)
async def announce(interaction: discord.Interaction, channel: discord.TextChannel, *, message: str):
    await channel.send(f"📢 **إعلان:** {message}")
    await interaction.response.send_message("✅ تم إرسال الإعلان بنجاح!", ephemeral=True)

# -------------------- نظام قيفواي احترافي --------------------
@bot.tree.command(name="giveaway", description="إنشاء قيفواي جديد")
@commands.has_permissions(administrator=True)
async def giveaway(interaction: discord.Interaction, channel: discord.TextChannel, duration: int, prize: str):
    embed = discord.Embed(title="🎉 قيفواي 🎉", description=f"الجائزة: {prize}\n⏳ ينتهي خلال {duration} دقيقة!", color=0x00ff00)
    msg = await channel.send(embed=embed)
    await msg.add_reaction("🎉")
    await interaction.response.send_message(f"✅ تم بدء القيفواي في {channel.mention}!", ephemeral=True)

    await asyncio.sleep(duration * 60)
    msg = await channel.fetch_message(msg.id)
    users = [user async for user in msg.reactions[0].users() if not user.bot]
    if users:
        winner = random.choice(users)
        await channel.send(f"🎉 تهانينا! الفائز هو {winner.mention} 🎉")
    else:
        await channel.send("❗ لم يشارك أحد في القيفواي!")

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
