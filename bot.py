import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.guilds = True
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

OWNER_ID = 760949680355278848
ALLOWED_ROLES = [1248376968643088485, 1236265862952915046]

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
                                               use_application_commands=False,
                                               create_polls=False)
    await interaction.response.send_message("🔒 تم قفل القناة بنجاح!")

@bot.tree.command(name="unlock", description="فتح القناة الحالية")
async def unlock(interaction: discord.Interaction):
    if not await has_allowed_role(interaction):
        await interaction.response.send_message("❌ ليس لديك الصلاحية لاستخدام هذا الأمر.", ephemeral=True)
        return

    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 تم فتح القناة بنجاح!")

@bot.tree.command(name="warn", description="تحذير عضو")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد السبب"):
    if not await has_allowed_role(interaction):
        await interaction.response.send_message("❌ ليس لديك الصلاحية لاستخدام هذا الأمر.", ephemeral=True)
        return

    warning_roles = [role for role in member.roles if role.name.startswith("تحذير")]

    if len(warning_roles) >= 3:
        await interaction.response.send_message(f"⚠️ {member.mention} لديه بالفعل 3 تحذيرات.")
        return

    warn_role = discord.utils.get(interaction.guild.roles, name=f"تحذير {len(warning_roles) + 1}")
    if warn_role:
        await member.add_roles(warn_role)
        await member.send(f"⚠️ لقد تلقيت تحذيرًا في السيرفر {interaction.guild.name} بسبب: {reason}")
        await interaction.response.send_message(f"✅ {member.mention} تم تحذيره بنجاح! السبب: {reason}")
    else:
        await interaction.response.send_message("❌ لم يتم العثور على أدوار التحذير. تأكد من إضافتها في السيرفر.")

@bot.tree.command(name="unwarn", description="إزالة تحذير من عضو")
async def unwarn(interaction: discord.Interaction, member: discord.Member):
    if not await has_allowed_role(interaction):
        await interaction.response.send_message("❌ ليس لديك الصلاحية لاستخدام هذا الأمر.", ephemeral=True)
        return

    warning_roles = [role for role in member.roles if role.name.startswith("تحذير")]
    if warning_roles:
        await member.remove_roles(warning_roles[0])
        await interaction.response.send_message(f"✅ تم إزالة تحذير واحد من {member.mention} بنجاح!")
    else:
        await interaction.response.send_message(f"❌ {member.mention} ليس لديه أي تحذيرات.")

@bot.tree.command(name="say", description="إرسال رسالة عبر البوت")
async def say(interaction: discord.Interaction, message: str):
    if not await has_allowed_role(interaction):
        await interaction.response.send_message("❌ ليس لديك الصلاحية لاستخدام هذا الأمر.", ephemeral=True)
        return

    await interaction.channel.send(message)
    await interaction.response.send_message("✅ تم إرسال الرسالة بنجاح!", ephemeral=True)

@bot.tree.command(name="on_duty", description="عرض قائمة بالإداريين المتاحين")
async def on_duty(interaction: discord.Interaction):
    admins = [member.mention for member in interaction.guild.members if any(role.id in ALLOWED_ROLES for role in member.roles)]
    if admins:
        await interaction.response.send_message(f"👨‍💼 الإداريون المتاحون حاليًا: {', '.join(admins)}")
    else:
        await interaction.response.send_message("❌ لا يوجد إداريون متاحون حاليًا.")

import os
bot.run(os.getenv("TOKEN"))
