import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import random

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
duty_list = []

# إدارة - أوامر مثل البان والكيك والمزيد
@bot.tree.command(name="ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "غير محدد"):
    if member.id == bot.owner_id:
        await interaction.response.send_message("❌ لا يمكن طرد صاحب البوت.")
    else:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"✅ تم حظر {member.mention} بنجاح. السبب: {reason}")

@bot.tree.command(name="kick")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "غير محدد"):
    if member.id == bot.owner_id:
        await interaction.response.send_message("❌ لا يمكن طرد صاحب البوت.")
    else:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"✅ تم طرد {member.mention} بنجاح. السبب: {reason}")

@bot.tree.command(name="mute")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "غير محدد"):
    await member.edit(timeout_until=discord.utils.utcnow() + timedelta(minutes=duration))
    await interaction.response.send_message(f"✅ تم إسكات {member.mention} لمدة {duration} دقيقة. السبب: {reason}")

@bot.tree.command(name="warn")
@app_commands.checks.has_permissions(kick_members=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "غير محدد"):
    await interaction.response.send_message(f"⚠️ {member.mention} تم تحذيره. السبب: {reason}")

@bot.tree.command(name="purge")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"✅ تم حذف {amount} رسالة بنجاح.", ephemeral=True)

# نظام التيكت المتقدم
@bot.tree.command(name="ticket")
@app_commands.checks.has_permissions(manage_channels=True)
async def ticket(interaction: discord.Interaction):
    embed = discord.Embed(title="🎫 اختر نوع التيكت", description="اختر أحد الخيارات التالية:")
    embed.add_field(name="1️⃣ طلب خدمة", value="لفتح تيكت لطلب خدمة جديدة.", inline=False)
    embed.add_field(name="2️⃣ تجديد خدمة", value="لفتح تيكت لتجديد الخدمة.", inline=False)
    embed.add_field(name="3️⃣ تساؤل", value="لفتح تيكت لطرح سؤال.", inline=False)

    view = TicketSelectView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class TicketSelectView(discord.ui.View):
    @discord.ui.button(label="طلب خدمة", style=discord.ButtonStyle.primary)
    async def service_request(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "طلب خدمة")

    @discord.ui.button(label="تجديد خدمة", style=discord.ButtonStyle.success)
    async def service_renew(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "تجديد خدمة")

    @discord.ui.button(label="تساؤل", style=discord.ButtonStyle.secondary)
    async def inquiry(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "تساؤل")

async def create_ticket(interaction, ticket_type):
    category = discord.utils.get(interaction.guild.categories, name="Tickets")
    if not category:
        category = await interaction.guild.create_category("Tickets")

    channel = await interaction.guild.create_text_channel(f"{ticket_type}-{interaction.user.name}", category=category)
    await channel.send(f"**{interaction.user.mention}** فتح تيكت ({ticket_type}). انتظر أحد الإداريين.")
    await interaction.response.send_message(f"تم فتح تيكت بنجاح: {channel.mention}", ephemeral=True)

# نظام القيفواي الاحترافي
@bot.tree.command(name="giveaway")
@app_commands.checks.has_permissions(administrator=True)
async def giveaway(interaction: discord.Interaction, duration: int, prize: str, winners: int = 1):
    embed = discord.Embed(title="🎉 جائزة جديدة!", description=f"🏆 الجائزة: **{prize}**\n⌛ مدة السحب: {duration} دقيقة\n👥 عدد الفائزين: {winners}")
    message = await interaction.channel.send(embed=embed)
    await message.add_reaction("🎉")

    await asyncio.sleep(duration * 60)

    updated_msg = await interaction.channel.fetch_message(message.id)
    users = [user async for user in updated_msg.reactions[0].users() if not user.bot]

    if users:
        winners_list = random.sample(users, min(winners, len(users)))
        winner_mentions = ', '.join(winner.mention for winner in winners_list)
        await interaction.channel.send(f"🎊 الفائزون هم: {winner_mentions}! مبروك! 🎉")
    else:
        await interaction.channel.send("❌ لا يوجد مشاركين في السحب.")

# نظام إشعارات تلقائي
@bot.tree.command(name="notify")
@app_commands.checks.has_permissions(administrator=True)
async def notify(interaction: discord.Interaction, message: str):
    for channel in interaction.guild.text_channels:
        await channel.send(f"🔔 إشعار: {message}")

# نظام تسجيل الدخول والخروج
@bot.tree.command(name="on_duty")
@app_commands.checks.has_permissions(manage_roles=True)
async def on_duty(interaction: discord.Interaction):
    duty_list.append(interaction.user.id)
    await interaction.response.send_message(f"✅ {interaction.user.mention} الآن في الخدمة.")

@bot.tree.command(name="off_duty")
@app_commands.checks.has_permissions(manage_roles=True)
async def off_duty(interaction: discord.Interaction):
    if interaction.user.id in duty_list:
        duty_list.remove(interaction.user.id)
    await interaction.response.send_message(f"❎ {interaction.user.mention} خرج من الخدمة.")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"تم تسجيل الدخول باسم {bot.user}")

import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')

bot.run(os.getenv('TOKEN'))  # تأكد أن هذا السطر موجود ويستخدم os.getenv
