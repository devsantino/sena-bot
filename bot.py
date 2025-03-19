import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
from datetime import datetime, timedelta
import os
from collections import defaultdict

# إعدادات البوت
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.guilds = True
intents.messages = True
intents.members = True  # تفعيل لرؤية الأعضاء
intents.message_content = True  # تفعيل لرؤية محتوى الرسائل

bot = commands.Bot(command_prefix='!', intents=intents)

# إعدادات الأدوار والإشعارات
OWNER_ID = 760949680355278848  # استبدل هذا بمعرفك الشخصي
ALLOWED_ROLES = [1248376968643088485, 1236265862952915046]  # استبدل هذه بالأيدي الخاصة برولات الإدارة
notifications_channel_id = None  # سيتم تعيينه عبر أمر معين

WARNING_ROLES = {
    1: 1351706303894130759,  # رول التحذير الأول
    2: 1351706353567010898,  # رول التحذير الثاني
    3: 1351706386362273923   # رول التحذير الثالث
}

# إعدادات نظام مكافحة السبام
MESSAGE_LIMIT = 5  # الحد الأقصى لعدد الرسائل المسموح بها
TIME_WINDOW = 10  # الفترة الزمنية بالثواني
spam_tracker = defaultdict(list)  # لتتبع الرسائل المرسلة من قبل الأعضاء

# وظيفة للتحقق من الصلاحيات
async def has_allowed_role(interaction):
    return any(role.id in ALLOWED_ROLES for role in interaction.user.roles)

# حدث عند اتصال البوت
@bot.event
async def on_ready():
    print(f'✅ {bot.user} متصل بنجاح!')
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} أمر سلاش تم تسجيله بنجاح!")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تسجيل الأوامر: {e}")

# ---------------------------------- أوامر السلاش ----------------------------------
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
    await send_notification(
        f"🚨 **تم طرد عضو**\n"
        f"👤 العضو: {member.mention}\n"
        f"👤 تم الطرد بواسطة: {interaction.user.mention}\n"
        f"📝 السبب: {reason}"
    )

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
    await send_notification(
        f"🚨 **تم حظر عضو**\n"
        f"👤 العضو: {member.mention}\n"
        f"👤 تم الحظر بواسطة: {interaction.user.mention}\n"
        f"📝 السبب: {reason}"
    )

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
            await send_notification(
                f"⚠️ **تم تحذير عضو**\n"
                f"👤 العضو: {member.mention}\n"
                f"👤 تم التحذير بواسطة: {interaction.user.mention}\n"
                f"📝 السبب: {reason}"
            )
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
            await send_notification(
                f"✅ **تمت إزالة تحذير من عضو**\n"
                f"👤 العضو: {member.mention}\n"
                f"👤 تمت الإزالة بواسطة: {interaction.user.mention}"
            )
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
    await send_notification(
        f"🗣️ **تم استخدام أمر SAY**\n"
        f"👤 المستخدم: {interaction.user.mention}\n"
        f"📝 الرسالة: {message}"
    )

@bot.tree.command(name="setnotifications", description="تحديد روم الإشعارات التلقائية")
async def set_notifications(interaction: discord.Interaction, channel: discord.TextChannel):
    global notifications_channel_id
    if not await has_allowed_role(interaction):
        await interaction.response.send_message("❌ ليس لديك الصلاحية لاستخدام هذا الأمر.", ephemeral=True)
        return

    notifications_channel_id = channel.id
    await interaction.response.send_message(f"✅ تم تعيين روم الإشعارات إلى {channel.mention}")

# ---------------------------------- إشعارات الرسائل والأعضاء ----------------------------------
@bot.event
async def on_message_delete(message):
    if notifications_channel_id and not message.author.bot:
        embed = discord.Embed(
            title="🗑️ **تم حذف رسالة**",
            description=f"📝 الرسالة: {message.content}\n"
                        f"👤 العضو: {message.author.mention}\n"
                        f"📌 القناة: {message.channel.mention}",
            color=discord.Color.red()
        )
        await send_notification(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if notifications_channel_id and not before.author.bot and before.content != after.content:
        embed = discord.Embed(
            title="📝 **تم تعديل رسالة**",
            description=f"👤 العضو: {before.author.mention}\n"
                        f"📌 القناة: {before.channel.mention}\n"
                        f"**قبل:** {before.content}\n"
                        f"**بعد:** {after.content}",
            color=discord.Color.blue()
        )
        await send_notification(embed=embed)

@bot.event
async def on_member_remove(member):
    if notifications_channel_id:
        embed = discord.Embed(
            title="🚪 **عضو غادر السيرفر**",
            description=f"👤 العضو: {member.mention}\n"
                        f"🕒 تاريخ الانضمام: {member.joined_at.strftime('%Y-%m-%d %H:%M:%S')}",
            color=discord.Color.orange()
        )
        await send_notification(embed=embed)

# ---------------------------------- نظام مكافحة السبام ----------------------------------
@bot.event
async def on_message(message):
    if message.author.bot:  # تجاهل رسائل البوت
        return

    # تحديث قائمة الرسائل للعضو
    spam_tracker[message.author.id].append(datetime.now())

    # إزالة الرسائل القديمة خارج النافذة الزمنية
    spam_tracker[message.author.id] = [
        msg_time for msg_time in spam_tracker[message.author.id]
        if (datetime.now() - msg_time).seconds <= TIME_WINDOW
    ]

    # التحقق من تجاوز الحد المسموح به
    if len(spam_tracker[message.author.id]) > MESSAGE_LIMIT:
        await send_notification(
            f"🚨 **تم اكتشاف سبام**\n"
            f"👤 العضو: {message.author.mention}\n"
            f"📌 القناة: {message.channel.mention}\n"
            f"📝 عدد الرسائل: {len(spam_tracker[message.author.id])} في {TIME_WINDOW} ثواني"
        )
        # إعادة تعيين القائمة لمنع تكرار الإشعارات
        spam_tracker[message.author.id] = []

# وظيفة لإرسال الإشعارات
async def send_notification(content=None, embed=None):
    if notifications_channel_id:
        channel = bot.get_channel(notifications_channel_id)
        if channel:
            if embed:
                await channel.send(embed=embed)
            elif content:
                await channel.send(content)

# ---------------------------------- فئة القيف أواي ----------------------------------
class GiveawayView(ui.View):
    def __init__(self, duration: int, winners: int, prize: str):
        super().__init__(timeout=None)
        self.duration = duration
        self.winners = winners
        self.prize = prize
        self.participants = []

    @ui.button(label="🎊 Participate", style=discord.ButtonStyle.green)
    async def participate(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user not in self.participants:
            self.participants.append(interaction.user)
            await interaction.response.send_message("✅ You have successfully participated in the giveaway!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ You have already participated in this giveaway!", ephemeral=True)

    @ui.button(label="👥 Participants", style=discord.ButtonStyle.blurple)
    async def show_participants(self, interaction: discord.Interaction, button: ui.Button):
        participants_list = "\n".join([user.mention for user in self.participants])
        await interaction.response.send_message(f"👥 **Participants:**\n{participants_list}", ephemeral=True)

class CancelGiveawayView(ui.View):
    def __init__(self, giveaways: list):
        super().__init__()
        self.giveaways = giveaways
        self.add_item(GiveawayDropdown(giveaways))

class GiveawayDropdown(ui.Select):
    def __init__(self, giveaways: list):
        options = [
            discord.SelectOption(label=f"Giveaway: {giveaway[2]}", value=str(giveaway[0]))
            for giveaway in giveaways
        ]
        super().__init__(placeholder="اختر القيف أواي المراد إلغاؤه", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_id = int(self.values[0])
        for giveaway in self.view.giveaways:
            if giveaway[0] == selected_id:
                self.view.giveaways.remove(giveaway)
                await interaction.response.send_message(f"✅ تم إلغاء القيف أواي: **{giveaway[2]}** بنجاح!", ephemeral=True)
                return

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_giveaways = []

    @app_commands.command(name="giveaway", description="بدء قيف أواي جديد")
    @app_commands.describe(
        duration="مدة القيف أواي (مثال: 5m, 2h, 1d)",
        winners="عدد الفائزين",
        prize="الجائزة"
    )
    async def giveaway(self, interaction: discord.Interaction, duration: str, winners: int, prize: str):
        # تحويل المدة إلى ثواني
        try:
            duration_seconds = self.parse_duration(duration)
        except ValueError as e:
            await interaction.response.send_message(f"❌ {e}", ephemeral=True)
            return

        if duration_seconds <= 0 or winners <= 0:
            await interaction.response.send_message("❌ مدة أو عدد فائزين غير صالح! تأكد من إدخال أرقام صحيحة.", ephemeral=True)
            return

        # إنشاء رسالة القيف أواي
        embed = discord.Embed(
            title="🎉 **GIVEAWAY** 🎉",
            description=f"🎁 **Prize:** {prize}\n⏳ **Duration:** {self.format_duration(duration_seconds)}\n👑 **Winners:** {winners}",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow() + timedelta(seconds=duration_seconds))
        embed.set_footer(text="تفاعل مع الزر أدناه للمشاركة!")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/123456789012345678/987654321098765432/giveaway.png")  # رابط صورة فخمة
        embed.add_field(name="🎊 **How to Participate**", value="اضغط على الزر الأخضر أدناه للمشاركة!", inline=False)
        embed.add_field(name="👥 **Participants**", value="اضغط على الزر الأزرق لعرض المشاركين.", inline=False)

        view = GiveawayView(duration_seconds, winners, prize)
        await interaction.response.send_message(embed=embed, view=view)
        message = await interaction.original_response()

        # إضافة القيف أواي إلى القائمة النشطة
        self.active_giveaways.append((message.id, winners, prize))

        # الانتظار حتى انتهاء المدة
        await asyncio.sleep(duration_seconds)

        # جلب الرسالة مرة أخرى بعد انتهاء المدة
        message = await interaction.channel.fetch_message(message.id)
        reaction = discord.utils.get(message.reactions, emoji="🎊")

        if reaction and reaction.count > 1:  # يتجاهل البوت نفسه
            participants = [user async for user in reaction.users() if not user.bot]
            if len(participants) < winners:
                await interaction.followup.send("❌ عدد المشاركين أقل من عدد الفائزين! القيف أواي أُلغي تلقائيًا.")
                return

            # اختيار الفائزين
            winners_list = random.sample(participants, winners)
            winners_mentions = ', '.join(winner.mention for winner in winners_list)
            await interaction.followup.send(f"🎉 تهانينا! الفائزون هم: {winners_mentions} وفازوا بجائزة: **{prize}**")
        else:
            await interaction.followup.send("❌ لم يتفاعل أحد مع القيف أواي! تم الإلغاء تلقائيًا.")

    def parse_duration(self, duration: str) -> int:
        """
        تحويل المدة من نص (مثل 5m, 2h, 1d) إلى ثواني.
        """
        if duration.endswith("m"):
            return int(duration[:-1]) * 60
        elif duration.endswith("h"):
            return int(duration[:-1]) * 3600
        elif duration.endswith("d"):
            return int(duration[:-1]) * 86400
        else:
            raise ValueError("صيغة المدة غير صالحة! استخدم `5m` للدقائق، `2h` للساعات، أو `1d` للأيام.")

    def format_duration(self, duration: int) -> str:
        """
        تحويل المدة من ثواني إلى تنسيق مقروء (مثل 5 دقائق، 2 ساعات، 1 يوم).
        """
        if duration < 60:
            return f"{duration} ثانية"
        elif duration < 3600:
            return f"{duration // 60} دقيقة"
        elif duration < 86400:
            return f"{duration // 3600} ساعة"
        else:
            return f"{duration // 86400} يوم"

    @app_commands.command(name="cancel_giveaway", description="إلغاء قيف أواي محدد")
    async def cancel_giveaway(self, interaction: discord.Interaction):
        if not self.active_giveaways:
            await interaction.response.send_message("❌ لا يوجد قيف أوايات نشطة حالياً.", ephemeral=True)
            return

        view = CancelGiveawayView(self.active_giveaways.copy())
        await interaction.response.send_message("اختر القيف أواي المراد إلغاؤه:", view=view, ephemeral=True)

# تحميل فئة القيف أواي عند تشغيل البوت
@bot.event
async def on_ready():
    await bot.add_cog(Giveaway(bot))
    print(f'✅ {bot.user} متصل بنجاح!')
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} أمر سلاش تم تسجيله بنجاح!")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تسجيل الأوامر: {e}")

# تشغيل البوت
bot.run(os.getenv("TOKEN"))
