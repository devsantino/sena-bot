import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.guilds = True
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

OWNER_ID = 760949680355278848  # استبدل هذا بمعرفك الشخصي
ALLOWED_ROLES = [1248376968643088485 , 1236265862952915046]  # استبدل هذه بمعرفات الرتب المسموح لها باستخدام أوامر الإدارة

@bot.event
async def on_ready():
    print(f'✅ {bot.user} متصل بنجاح!')
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} أمر سلاش تم تسجيله بنجاح!")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تسجيل الأوامر: {e}")

@bot.tree.command(name="ping", description="يظهر لك سرعة استجابة البوت")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! 🏓 {round(bot.latency * 1000)}ms")

async def has_allowed_role(interaction):
    return any(role.id in ALLOWED_ROLES for role in interaction.user.roles)

@bot.tree.command(name="kick", description="طرد عضو")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد السبب"):
    if not await has_allowed_role(interaction):
        await interaction.response.send_message("❌ ليس لديك الصلاحية لاستخدام هذا الأمر.", ephemeral=True)
        return

    if member.id == OWNER_ID:
        await interaction.response.send_message("❌ لا يمكنك طرد صاحب البوت!", ephemeral=True)
        return

    await member.kick(reason=reason)
    await interaction.response.send_message(f"✅ {member.mention} تم طرده بنجاح!")

@bot.tree.command(name="ban", description="حظر عضو")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد السبب"):
    if not await has_allowed_role(interaction):
        await interaction.response.send_message("❌ ليس لديك الصلاحية لاستخدام هذا الأمر.", ephemeral=True)
        return

    if member.id == OWNER_ID:
        await interaction.response.send_message("❌ لا يمكنك حظر صاحب البوت!", ephemeral=True)
        return

    await member.ban(reason=reason)
    await interaction.response.send_message(f"✅ {member.mention} تم حظره بنجاح!")

import os
bot.run(os.getenv("TOKEN"))
