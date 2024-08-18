import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import re

# Ваш Discord токен
TOKEN = 'MTI3NDQyMTIzMTM4MjI5ODY0NQ.GC4ERN.MRvCARNKeJBpcobv2nQhInfpQow1ENqym6rv6E'

# Guild ID
GUILD_ID = 1274376328837075034

# Создаем бота
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Переменная для хранения опросов и их вариантов
polls = {}
warn_count = {}

# Обработчик события, когда бот готов
@bot.event
async def on_ready():
    print(f'Бот {bot.user} успешно запущен и готов к работе!')
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    print("Команды синхронизированы!")

# Создание кастомного embed для команд
def create_custom_embed(title, description, fields=None, thumbnail_url=None, footer_text=None, color=discord.Color.blurple()):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    if fields:
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    if footer_text:
        embed.set_footer(text=footer_text)
    return embed

# Упрощенная команда для создания опроса с эмодзи
@bot.tree.command(name='poll', description='Создать опрос')
@app_commands.describe(question='Вопрос опроса', option1='Вариант 1', option2='Вариант 2', option3='Вариант 3 (необязательно)', option4='Вариант 4 (необязательно)')
async def poll(interaction: discord.Interaction, question: str, option1: str, option2: str, option3: str = None, option4: str = None):
    embed = create_custom_embed(
        title="🗳️ Опрос",
        description=question,
        fields=[
            ("1️⃣ " + option1, ""),
            ("2️⃣ " + option2, ""),
            ("3️⃣ " + option3 if option3 else "Не указан", ""),
            ("4️⃣ " + option4 if option4 else "Не указан", "")
        ],
        color=discord.Color.blue()
    )
    message = await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()

    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
    for i, option in enumerate([option1, option2, option3, option4]):
        if option:
            await message.add_reaction(reactions[i])

# Команда для отображения всех доступных команд
@bot.tree.command(name='help', description='Показать список команд')
async def help_command(interaction: discord.Interaction):
    embed = create_custom_embed(
        title="🛠️ Команды бота",
        description="Вот список доступных команд. Нажмите на команду, чтобы узнать больше.",
        fields=[
            ("/ban", "Заблокировать пользователя"),
            ("/kick", "Исключить пользователя"),
            ("/warn", "Выдать предупреждение пользователю"),
            ("/mute", "Ограничить доступ к сообщениям пользователю"),
            ("/unmute", "Снять ограничения сообщений с пользователя"),
            ("/poll", "Создать новый опрос"),
            ("/members", "Показать список всех участников сервера"),
            ("/status", "Проверить статус бота и сервера")
        ],
        thumbnail_url='https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGs5enQwN2oweTVxbDJ2czFzN25kc3pwcW91cDg0emJ5aHNjZXV6dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9jlOa676KrqOG1jUUt/giphy.gif',
        footer_text="©️ Ваш Бот | Все права защищены"
    )
    await interaction.response.send_message(embed=embed)

# Команда для проверки статуса бота
@bot.tree.command(name='status', description='Показать статус бота и сервера')
async def status(interaction: discord.Interaction):
    embed = create_custom_embed(
        title="📊 Статус бота",
        description="Информация о текущем статусе бота и сервера.",
        fields=[
            ("Сервер", interaction.guild.name),
            ("Пользователь", interaction.user.mention),
            ("Число участников на сервере", str(interaction.guild.member_count))
        ],
        thumbnail_url='https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGs5enQwN2oweTVxbDJ2czFzN25kc3pwcW91cDg0emJ5aHNjZXV6dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9jlOa676KrqOG1jUUt/giphy.gif',
        footer_text="©️ Ваш Бот | Все права защищены",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

# Команда для получения списка всех участников без ботов
@bot.tree.command(name='members', description='Показать список участников сервера')
async def members(interaction: discord.Interaction):
    members = [member.mention for member in interaction.guild.members if not member.bot]
    if len(members) > 1000:
        await interaction.response.send_message("Слишком много участников для отображения.")
        return

    embed = create_custom_embed(
        title="👥 Список участников",
        description="\n".join(members),
        color=discord.Color.purple(),
        thumbnail_url='https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGs5enQwN2oweTVxbDJ2czFzN25kc3pwcW91cDg0emJ5aHNjZXV6dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9jlOa676KrqOG1jUUt/giphy.gif',
        footer_text="©️ Ваш Бот | Все права защищены"
    )
    await interaction.response.send_message(embed=embed)

# Функция для конвертации времени в секунды
def convert_time_to_seconds(time_str: str) -> int:
    time_regex = re.match(r"(\d+)([smhd])", time_str)
    if not time_regex:
        raise ValueError("Неверный формат времени")

    time_value = int(time_regex.group(1))
    time_unit = time_regex.group(2)

    if time_unit == "s":
        return time_value
    elif time_unit == "m":
        return time_value * 60
    elif time_unit == "h":
        return time_value * 3600
    elif time_unit == "d":
        return time_value * 86400
    else:
        raise ValueError("Неверная единица измерения времени")

# Команда для выдачи предупреждения
@bot.tree.command(name='warn', description='Предупредить пользователя')
@app_commands.describe(user='Пользователь для предупреждения', reason='Причина предупреждения')
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str = None):
    if reason is None:
        reason = "Не указана"
    
    if user.id not in warn_count:
        warn_count[user.id] = 0
    warn_count[user.id] += 1
    
    embed = create_custom_embed(
        title="⚠️ Предупреждение",
        description=f"**Участник:** {user.mention}\n**Причина:** {reason}\n**Всего предупреждений:** {warn_count[user.id]}",
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed)

# Команда для мьюта участника с выбором времени
@bot.tree.command(name='mute', description='Ограничить пользователя в доступе к сообщениям')
@app_commands.describe(user='Пользователь для мьюта', duration='Длительность мьюта (например: 1m, 2h, 1d)', reason='Причина мьюта')
async def mute(interaction: discord.Interaction, user: discord.Member, duration: str, reason: str = None):
    if reason is None:
        reason = "Не указана"
    
    try:
        duration_seconds = convert_time_to_seconds(duration)
    except ValueError as e:
        await interaction.response.send_message(str(e))
        return
    
    mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not mute_role:
        mute_role = await interaction.guild.create_role(name="Muted")
        for channel in interaction.guild.channels:
            await channel.set_permissions(mute_role, send_messages=False, speak=False)
    
    await user.add_roles(mute_role, reason=reason)
    
    embed = create_custom_embed(
        title="🔇 Мьют",
        description=f"**Участник:** {user.mention}\n**Причина:** {reason}\n**Длительность:** {duration}",
        color=discord.Color.red()
    )
    embed.set_footer(text="©️ Ваш Бот | Все права защищены")
    await interaction.response.send_message(embed=embed)

    await asyncio.sleep(duration_seconds)
    await user.remove_roles(mute_role, reason="Мьют истек")
    await interaction.followup.send(f"{user.mention} больше не замьючен.")

# Команда для разбанивания пользователя
@bot.tree.command(name='unmute', description='Снять ограничения сообщений с пользователя')
@app_commands.describe(user='Пользователь для разбанивания')
async def unmute(interaction: discord.Interaction, user: discord.Member):
    mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if mute_role in user.roles:
        await user.remove_roles(mute_role, reason="Мьют снят")
        embed = create_custom_embed(
            title="🔊 Размьют",
            description=f"**Участник:** {user.mention}\n**Статус:** Размьючен",
            color=discord.Color.green()
        )
        embed.set_footer(text="©️ Ваш Бот | Все права защищены")
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"{user.mention} не замьючен.")

# Запуск бота
bot.run(TOKEN)
