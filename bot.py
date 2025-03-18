import discord
from discord.ext import commands
from discord import app_commands
import os

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.guilds = True
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

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

@bot.tree.command(name="kick", description="طرد عضو من السيرفر")
@app_commands.describe(member="العضو الذي تريد طرده", reason="السبب")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد سبب"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ ليس لديك صلاحيات كافية لطرد الأعضاء.", ephemeral=True)
        return
    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"✅ تم طرد {member.mention} بنجاح. السبب: {reason}")
    except Exception as e:
        await interaction.response.send_message(f"❌ حدث خطأ: {e}", ephemeral=True)

@bot.tree.command(name="ban", description="حظر عضو من السيرفر")
@app_commands.describe(member="العضو الذي تريد حظره", reason="السبب")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد سبب"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ ليس لديك صلاحيات كافية لحظر الأعضاء.", ephemeral=True)
        return
    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"✅ تم حظر {member.mention} بنجاح. السبب: {reason}")
    except Exception as e:
        await interaction.response.send_message(f"❌ حدث خطأ: {e}", ephemeral=True)

bot.run(os.getenv("TOKEN"))
