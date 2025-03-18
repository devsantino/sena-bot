import discord
import os
from discord.ext import commands

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
        await bot.tree.sync()
        print("✅ تم مزامنة أوامر السلاش بنجاح!")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء مزامنة الأوامر: {e}")

@bot.tree.command(name="ping", description="يظهر لك سرعة استجابة البوت")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! 🏓 {round(bot.latency * 1000)}ms", ephemeral=True)

bot.run(os.getenv("YOUR_BOT_TOKEN"))
