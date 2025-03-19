import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.guilds = True
intents.messages = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

OWNER_ID = 760949680355278848  # استبدل هذا بمعرفك الشخصي
ALLOWED_ROLES = [1248376968643088485, 1236265862952915046]  # استبدل هذه بالأيدي الخاصة برولات الإدارة

WARNING_ROLES = {
    1: 1248376968643088485,  # رول التحذير الأول
    2: 1236265862952915046,  # رول التحذير الثاني
    3: 987654321098765432   # رول التحذير الثالث
}

@bot.event
async def on_ready():
    print(f'✅ {bot.user} متصل بنجاح!')
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} أمر سلاش تم تسجيله بنجاح!")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تسجيل الأوامر: {e}")

async def has_allowed_role(interaction):
    return any(role.id in ALLOWED_ROLES for role in interaction.user.roles)

@bot.tree.command(name="ping", description="يظهر لك سرعة استجابة البوت")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! 🏓 {round(bot.latency * 1000)}ms")

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

@bot.tree.command(name="lock", description="قفل القناة الحالية")
async def lock(interaction: discord.Interaction):
    if not await has_allowed_role(interaction):
        await interaction.response.send_message("❌ ليس لديك الصلاحية لاستخدام هذا الأمر.", ephemeral=True)
        return

    await interaction.channel.set_permissions(interaction.guild.default_role,
                                              send_messages=False,
                                              create_public_threads=False,
                                              create_private_threads=False,
                                              embed_links=False,
                                              attach_files=False,
                                              use_application_commands=False)
    await interaction.response.send_message("🔒 تم قفل القناة بنجاح!")

@bot.tree.command(name="unlock", description="فتح القناة الحالية")
async def unlock(interaction: discord.Interaction):
    if not await has_allowed_role(interaction):
        await interaction.response.send_message("❌ ليس لديك الصلاحية لاستخدام هذا الأمر.", ephemeral=True)
        return

    await interaction.channel.set_permissions(interaction.guild.default_role,
                                              send_messages=True,
                                              create_public_threads=True,
                                              create_private_threads=True,
                                              embed_links=True,
                                              attach_files=True,
                                              use_application_commands=True)
    await interaction.response.send_message("🔓 تم فتح القناة بنجاح!")

@bot.tree.command(name="warn", description="تحذير عضو")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد السبب"):
    if not await has_allowed_role(interaction):
        await interaction.response.send_message("❌ ليس لديك الصلاحية لاستخدام هذا الأمر.", ephemeral=True)
        return

    for level, role_id in WARNING_ROLES.items():
        role = discord.utils.get(interaction.guild.roles, id=role_id)
        if role not in member.roles:
            await member.add_roles(role)
            await member.send(f"⚠️ لقد تلقيت تحذيرًا في سيرفر {interaction.guild.name} بسبب: {reason}")
            await interaction.response.send_message(f"⚠️ {member.mention} تم تحذيره بنجاح! السبب: {reason}")
            return

    await interaction.response.send_message(f"❌ {member.mention} لديه بالفعل الحد الأقصى من التحذيرات!", ephemeral=True)

@bot.tree.command(name="unwarn", description="إزالة أحد تحذيرات عضو")
async def unwarn(interaction: discord.Interaction, member: discord.Member):
    if not await has_allowed_role(interaction):
        await interaction.response.send_message("❌ ليس لديك الصلاحية لاستخدام هذا الأمر.", ephemeral=True)
        return

    for level, role_id in reversed(WARNING_ROLES.items()):
        role = discord.utils.get(interaction.guild.roles, id=role_id)
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"✅ تمت إزالة تحذير من {member.mention} بنجاح!")
            return

    await interaction.response.send_message(f"❌ {member.mention} ليس لديه أي تحذيرات لإزالتها!", ephemeral=True)

@bot.tree.command(name="on_duty", description="عرض الإداريين المتاحين")
async def on_duty(interaction: discord.Interaction):
    duty_staff = [member.mention for member in interaction.guild.members if any(role.id in ALLOWED_ROLES for role in member.roles)]
    if duty_staff:
        await interaction.response.send_message(f"🟢 الإداريون المتاحون حالياً:\n{', '.join(duty_staff)}")
    else:
        await interaction.response.send_message("❌ لا يوجد إداريون متاحون حالياً.")

@bot.tree.command(name="say", description="يجعل البوت يكرر رسالة معينة")
async def say(interaction: discord.Interaction, *, message: str):
    await interaction.channel.send(message)
    await interaction.response.send_message("✅ تم إرسال الرسالة بنجاح!", ephemeral=True)


import os
bot.run(os.getenv("TOKEN"))
