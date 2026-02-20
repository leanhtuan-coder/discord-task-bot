"""
Discord Bot for Research Project Task Management
Guided AI Use in Learning Data Structures and Algorithms

Author: Research Team - FPT University Hanoi
Version: 1.0.0 (MVP)
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import os
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

# Import configuration
try:
    from config import (
        BOT_TOKEN,
        DAILY_TASKS_CHANNEL_ID,
        PROGRESS_UPDATE_CHANNEL_ID,
        ANNOUNCEMENTS_CHANNEL_ID,
        USER_IDS,
        ROLE_IDS,
        TIMEZONE,
        USE_GOOGLE_SHEETS,
        GOOGLE_SHEET_ID,
        GOOGLE_SHEET_WORKSHEET,
    )
except ImportError:
    print("Error: config.py not found. Please create config.py with required settings.")
    print("See README.md for configuration instructions.")
    exit(1)

# Import Google Sheets sync if enabled
if USE_GOOGLE_SHEETS:
    try:
        from sheets_sync import load_tasks_from_sheets, mark_task_done_in_sheets
        print("Google Sheets integration enabled.")
    except ImportError:
        print("Error: Google Sheets integration requires 'gspread' and 'google-auth'")
        print("Run: pip install gspread google-auth")
        exit(1)



# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Timezone
tz = ZoneInfo(TIMEZONE)

# Track whether last load came from Sheets or JSON fallback
_last_sheets_error: str = ""
_using_sheets: bool = False


def load_tasks():
    """Load tasks from JSON file or Google Sheets."""
    global _last_sheets_error, _using_sheets
    if USE_GOOGLE_SHEETS:
        try:
            result = load_tasks_from_sheets(GOOGLE_SHEET_ID, GOOGLE_SHEET_WORKSHEET, tz)
            _last_sheets_error = ""
            _using_sheets = True
            return result
        except Exception as e:
            _last_sheets_error = str(e)
            _using_sheets = False
            print(f"Error loading from Google Sheets: {e}")
            print("Falling back to tasks.json")

    _using_sheets = False

    # Load from JSON file
    tasks_file = os.path.join(os.path.dirname(__file__), "tasks.json")
    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: tasks.json not found. Creating empty task list.")
        return {"tasks": []}
    except json.JSONDecodeError:
        print("Error: tasks.json is not valid JSON.")
        return {"tasks": []}


def save_tasks(data):
    """Save tasks to JSON file (only used when not using Google Sheets)."""
    if USE_GOOGLE_SHEETS:
        # Don't save to JSON when using Google Sheets
        return
    
    tasks_file = os.path.join(os.path.dirname(__file__), "tasks.json")
    with open(tasks_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)



def get_today_str():
    """Get today's date as string in DD/MM format."""
    return datetime.now(tz).strftime("%d/%m")


def get_tasks_for_date(date_str):
    """Get all tasks for a specific date."""
    data = load_tasks()
    return [t for t in data["tasks"] if t.get("date") == date_str and not t.get("done", False)]


def get_tasks_for_user(user_name):
    """Get all pending tasks for a specific user."""
    data = load_tasks()
    return [t for t in data["tasks"] if t.get("owner") == user_name and not t.get("done", False)]


def parse_date_str(date_str):
    """Parse date string DD/MM to date object for current year."""
    try:
        day, month = date_str.split('/')
        year = datetime.now(tz).year
        return date(year, int(month), int(day))
    except:
        return None


def get_week_tasks():
    """Get all tasks for the current week (Mon-Sun)."""
    data = load_tasks()
    today = datetime.now(tz).date()
    
    # Get Monday of current week
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    
    week_tasks = []
    for task in data["tasks"]:
        task_date = parse_date_str(task.get("date", ""))
        if task_date and monday <= task_date <= sunday:
            week_tasks.append(task)
    
    return week_tasks, monday, sunday


def get_overdue_tasks():
    """Get all tasks that are overdue (past date and not done)."""
    data = load_tasks()
    today = datetime.now(tz).date()
    
    overdue = []
    for task in data["tasks"]:
        if task.get("done", False):
            continue
        task_date = parse_date_str(task.get("date", ""))
        if task_date and task_date < today:
            overdue.append(task)
    
    return overdue


def get_upcoming_tasks(days=3):
    """Get tasks for the next N days."""
    data = load_tasks()
    today = datetime.now(tz).date()
    end_date = today + timedelta(days=days)
    
    upcoming = []
    for task in data["tasks"]:
        if task.get("done", False):
            continue
        task_date = parse_date_str(task.get("date", ""))
        if task_date and today <= task_date <= end_date:
            upcoming.append(task)
    
    return upcoming


def get_deadline_soon_tasks():
    """Get tasks with deadline today or tomorrow that are not done."""
    data = load_tasks()
    today = datetime.now(tz).date()
    tomorrow = today + timedelta(days=1)
    
    deadline_soon = []
    for task in data["tasks"]:
        if task.get("done", False):
            continue
        task_date = parse_date_str(task.get("date", ""))
        if task_date and task_date in [today, tomorrow]:
            deadline_soon.append(task)
    
    return deadline_soon


def format_daily_tasks_message(tasks_today):
    """Format the daily tasks message."""
    if not tasks_today:
        return "Hôm nay không có task nào được lên lịch."
    
    today_str = get_today_str()
    lines = [f"**Daily Tasks – {today_str}**\n"]
    
    # Group tasks by owner
    tasks_by_owner = {}
    for task in tasks_today:
        owner = task.get("owner", "Unassigned")
        if owner not in tasks_by_owner:
            tasks_by_owner[owner] = []
        tasks_by_owner[owner].append(task)
    
    for owner, owner_tasks in tasks_by_owner.items():
        user_id = USER_IDS.get(owner)
        role = get_role_for_owner(owner)
        
        if user_id:
            lines.append(f"<@{user_id}> ({role})")
        else:
            lines.append(f"**{owner}** ({role})")
        
        for task in owner_tasks:
            task_id = task.get("id", "")
            description = task.get("description", "")
            priority = task.get("priority", "")
            priority_icon = "🔴" if "MUST" in priority else "🟡" if "NICE" in priority else "⚪"
            lines.append(f"  {priority_icon} `{task_id}` {description}")
        
        lines.append("")
    
    lines.append(f"Vui lòng cập nhật tiến độ trong <#{PROGRESS_UPDATE_CHANNEL_ID}> trước 22:00.")
    
    return "\n".join(lines)


def get_role_for_owner(owner):
    """Get the role name for an owner."""
    role_mapping = {
        "Tuấn": "@Research Lead",
        "Thắng": "@Methodology",
        "Ngọc": "@Data & Tools",
        "Tú": "@Logistics",
    }
    return role_mapping.get(owner, "")


# Events
@bot.event
async def on_ready():
    """Called when bot is ready."""
    print(f"Bot is online: {bot.user}")
    print(f"Connected to {len(bot.guilds)} server(s)")
    
    # Sync slash commands to each guild (faster than global sync)
    try:
        for guild in bot.guilds:
            tree.copy_global_to(guild=guild)
            synced = await tree.sync(guild=guild)
            print(f"Synced {len(synced)} slash command(s) to {guild.name}")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    # Start scheduled tasks
    if not daily_morning_reminder.is_running():
        daily_morning_reminder.start()
    if not daily_evening_reminder.is_running():
        daily_evening_reminder.start()
    if not deadline_reminder.is_running():
        deadline_reminder.start()
    
    print("Scheduled tasks started.")
    print(f"Timezone: {TIMEZONE}")


# Scheduled Tasks
@tasks.loop(minutes=1)
async def daily_morning_reminder():
    """Send daily task reminder at 09:00."""
    now = datetime.now(tz)
    if now.hour == 9 and now.minute == 0:
        channel = bot.get_channel(DAILY_TASKS_CHANNEL_ID)
        if channel:
            today_str = get_today_str()
            tasks_today = get_tasks_for_date(today_str)
            message = format_daily_tasks_message(tasks_today)
            
            embed = discord.Embed(
                title="Daily Tasks",
                description=message,
                color=discord.Color.blue(),
                timestamp=now
            )
            embed.set_footer(text="Research Project Task Management")
            
            await channel.send(embed=embed)
            print(f"Sent daily morning reminder at {now}")


@tasks.loop(minutes=1)
async def daily_evening_reminder():
    """Send end-of-day progress reminder at 22:00."""
    now = datetime.now(tz)
    if now.hour == 22 and now.minute == 0:
        channel = bot.get_channel(DAILY_TASKS_CHANNEL_ID)
        if channel:
            # Get today's tasks that are NOT done
            today_str = get_today_str()
            tasks_today = get_tasks_for_date(today_str)
            pending_tasks = [t for t in tasks_today if not t.get("done", False)]
            
            # Group pending tasks by user
            pending_by_user = {}
            for task in pending_tasks:
                owner = task.get("owner", "Unassigned")
                if owner not in pending_by_user:
                    pending_by_user[owner] = []
                pending_by_user[owner].append(task)
            
            description_lines = ["Nhắc nhở cập nhật tiến độ cuối ngày.\n"]
            
            if pending_by_user:
                description_lines.append("**📋 Các bạn sau chưa hoàn thành tasks hôm nay:**\n")
                for owner, user_tasks in pending_by_user.items():
                    user_id = USER_IDS.get(owner)
                    mention = f"<@{user_id}>" if user_id else f"**{owner}**"
                    description_lines.append(f"{mention}: {len(user_tasks)} task(s) pending")
                description_lines.append("")
            
            description_lines.append(
                f"Vui lòng cập nhật trạng thái công việc trong <#{PROGRESS_UPDATE_CHANNEL_ID}>.\n\n"
                "Nếu có blockers hoặc cần hỗ trợ, hãy thông báo để team có thể điều chỉnh kế hoạch."
            )
            
            embed = discord.Embed(
                title="End-of-Day Reminder",
                description="\n".join(description_lines),
                color=discord.Color.orange(),
                timestamp=now
            )
            embed.set_footer(text="Research Project Task Management")
            
            await channel.send(embed=embed)
            print(f"Sent daily evening reminder at {now}")


# Slash Commands
@tree.command(name="today", description="Xem tất cả tasks của team hôm nay")
async def today_command(interaction: discord.Interaction):
    """Show today's tasks for the entire team."""
    today_str = get_today_str()
    tasks_today = get_tasks_for_date(today_str)
    
    if not tasks_today:
        await interaction.response.send_message(
            f"Không có task nào được lên lịch cho ngày {today_str}.",
            ephemeral=True
        )
        return
    
    message = format_daily_tasks_message(tasks_today)
    
    embed = discord.Embed(
        title=f"Tasks hôm nay ({today_str})",
        description=message,
        color=discord.Color.blue()
    )
    
    await interaction.response.send_message(embed=embed)


@tree.command(name="mytasks", description="Xem tasks của bạn")
async def mytasks_command(interaction: discord.Interaction):
    """Show tasks for the current user."""
    # Map Discord user to team member
    user_name = None
    for name, uid in USER_IDS.items():
        if uid == interaction.user.id:
            user_name = name
            break
    
    if not user_name:
        await interaction.response.send_message(
            "Không tìm thấy bạn trong danh sách team. Vui lòng liên hệ Research Lead.",
            ephemeral=True
        )
        return
    
    tasks = get_tasks_for_user(user_name)
    
    if not tasks:
        await interaction.response.send_message(
            f"Bạn không có task pending nào, {user_name}.",
            ephemeral=True
        )
        return
    
    lines = [f"**Tasks của {user_name}:**\n"]
    for task in tasks:
        task_id = task.get("id", "")
        description = task.get("description", "")
        task_date = task.get("date", "")
        priority = task.get("priority", "")
        priority_icon = "🔴" if "MUST" in priority else "🟡" if "NICE" in priority else "⚪"
        lines.append(f"{priority_icon} `{task_id}` [{task_date}] {description}")
    
    embed = discord.Embed(
        title="My Tasks",
        description="\n".join(lines),
        color=discord.Color.green()
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="done", description="Đánh dấu task đã hoàn thành")
@app_commands.describe(task_id="ID hoặc tên task")
async def done_command(interaction: discord.Interaction, task_id: str):
    """Mark a task as done."""
    data = load_tasks()
    
    task_found = None
    for task in data["tasks"]:
        # Match by ID or by description
        if task.get("id") == task_id.upper() or task.get("description", "").lower() == task_id.lower():
            task["done"] = True
            task["completed_at"] = datetime.now(tz).isoformat()
            task["completed_by"] = str(interaction.user.id)
            task_found = task
            break
    
    if not task_found:
        await interaction.response.send_message(
            f"Không tìm thấy task: `{task_id}`",
            ephemeral=True
        )
        return
    
    # Save to appropriate backend
    if USE_GOOGLE_SHEETS:
        try:
            # Use the task's stored worksheet name (each task tracks which sheet it came from)
            task_worksheet = task_found.get("worksheet", GOOGLE_SHEET_WORKSHEET.split(',')[0].strip())
            mark_task_done_in_sheets(
                GOOGLE_SHEET_ID,
                task_found.get("description"),
                str(interaction.user.id),
                task_worksheet,
                tz
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Lỗi khi cập nhật Google Sheets: {e}",
                ephemeral=True
            )
            return
    else:
        save_tasks(data)
    
    embed = discord.Embed(
        title="Task Completed",
        description=f"Task `{task_found.get('description')}` đã được đánh dấu hoàn thành.",
        color=discord.Color.green()
    )
    
    await interaction.response.send_message(embed=embed)


@tree.command(name="addtask", description="Thêm task mới (Research Lead only)")
@app_commands.describe(
    task_id="ID của task (ví dụ: T001)",
    date="Ngày (DD/MM)",
    owner="Người chịu trách nhiệm",
    description="Mô tả task",
    priority="Độ ưu tiên (MUST/NICE)"
)
async def addtask_command(
    interaction: discord.Interaction,
    task_id: str,
    date: str,
    owner: str,
    description: str,
    priority: str = "MUST"
):
    """Add a new task (Research Lead only)."""
    # Check if user is Research Lead
    lead_id = USER_IDS.get("Tuấn")
    if interaction.user.id != lead_id:
        await interaction.response.send_message(
            "Chỉ Research Lead mới có quyền thêm task.",
            ephemeral=True
        )
        return
    
    data = load_tasks()
    
    new_task = {
        "id": task_id.upper(),
        "date": date,
        "owner": owner,
        "description": description,
        "priority": priority.upper(),
        "done": False,
        "created_at": datetime.now(tz).isoformat()
    }
    
    data["tasks"].append(new_task)
    save_tasks(data)
    
    embed = discord.Embed(
        title="Task Added",
        description=(
            f"**ID:** `{task_id.upper()}`\n"
            f"**Date:** {date}\n"
            f"**Owner:** {owner}\n"
            f"**Description:** {description}\n"
            f"**Priority:** {priority.upper()}"
        ),
        color=discord.Color.blue()
    )
    
    await interaction.response.send_message(embed=embed)


@tree.command(name="status", description="Xem tổng quan tiến độ dự án")
async def status_command(interaction: discord.Interaction):
    """Show project status overview."""
    data = load_tasks()
    all_tasks = data.get("tasks", [])
    
    total = len(all_tasks)
    done = len([t for t in all_tasks if t.get("done", False)])
    pending = total - done
    
    # Count by owner
    by_owner = {}
    for task in all_tasks:
        owner = task.get("owner", "Unassigned")
        if owner not in by_owner:
            by_owner[owner] = {"total": 0, "done": 0}
        by_owner[owner]["total"] += 1
        if task.get("done", False):
            by_owner[owner]["done"] += 1
    
    lines = [
        f"**Tổng quan tiến độ:**\n",
        f"📊 Tổng tasks: {total}",
        f"✅ Hoàn thành: {done}",
        f"⏳ Đang chờ: {pending}",
        f"📈 Tiến độ: {done/total*100:.1f}%" if total > 0 else "📈 Tiến độ: 0%",
        f"\n**Theo thành viên:**"
    ]
    
    for owner, stats in by_owner.items():
        pct = stats["done"]/stats["total"]*100 if stats["total"] > 0 else 0
        lines.append(f"• {owner}: {stats['done']}/{stats['total']} ({pct:.0f}%)")
    
    embed = discord.Embed(
        title="Project Status",
        description="\n".join(lines),
        color=discord.Color.purple(),
        timestamp=datetime.now(tz)
    )
    
    await interaction.response.send_message(embed=embed)


@tree.command(name="debug", description="Debug: xem raw status từ Google Sheets (Research Lead only)")
async def debug_command(interaction: discord.Interaction):
    """Show raw task status values loaded from Google Sheets for debugging."""
    lead_id = USER_IDS.get("Tuấn")
    if interaction.user.id != lead_id:
        await interaction.response.send_message("Chỉ Research Lead mới dùng được lệnh này.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    data = load_tasks()
    tasks = data.get("tasks", [])

    if not tasks:
        await interaction.followup.send("Không load được task nào từ Sheets.", ephemeral=True)
        return

    today_str = get_today_str()
    lines = [f"**Debug: {len(tasks)} tasks loaded. Today = `{today_str}`**\n"]

    # Show data source status
    if _using_sheets:
        lines.append("📗 **Nguồn dữ liệu: Google Sheets** ✅\n")
    else:
        lines.append("📕 **Nguồn dữ liệu: tasks.json (FALLBACK)** ⚠️")
        if _last_sheets_error:
            err_short = _last_sheets_error[:200]
            lines.append(f"❌ **Lỗi Sheets:** `{err_short}`\n")
        else:
            lines.append("(USE_GOOGLE_SHEETS=False hoặc chưa load lần nào)\n")

    lines.append("Format: `[ID] [date] [done?] [raw status] — owner: task`\n")

    # Show last 20 tasks to avoid char limit
    for task in tasks[-20:]:
        done_flag = "✅" if task.get("done") else "❌"
        raw_status = task.get("status", "N/A")
        ws = task.get("worksheet", "?")
        lines.append(
            f"`{task.get('id','?')}` [{task.get('date','?')}] {done_flag} `\"{raw_status}\"` "
            f"({ws}) — {task.get('owner','?')}: {task.get('description','?')[:40]}"
        )

    content = "\n".join(lines)
    # Discord limit is 2000 chars per message
    if len(content) > 1900:
        content = content[:1900] + "\n...(truncated)"

    await interaction.followup.send(content, ephemeral=True)


# ========== NEW COMMANDS ==========

@tree.command(name="week", description="Xem tasks cả tuần")
async def week_command(interaction: discord.Interaction):
    """Show all tasks for the current week."""
    week_tasks, monday, sunday = get_week_tasks()
    
    if not week_tasks:
        await interaction.response.send_message(
            "Không có task nào trong tuần này.",
            ephemeral=True
        )
        return
    
    # Group by date
    tasks_by_date = {}
    for task in week_tasks:
        task_date = task.get("date", "")
        if task_date not in tasks_by_date:
            tasks_by_date[task_date] = []
        tasks_by_date[task_date].append(task)
    
    lines = []
    for date_str in sorted(tasks_by_date.keys()):
        lines.append(f"\n**📅 {date_str}**")
        for task in tasks_by_date[date_str]:
            status_icon = "✅" if task.get("done") else "⏳"
            priority_icon = "🔴" if "MUST" in task.get("priority", "") else "🟡"
            lines.append(f"  {status_icon} {priority_icon} `{task.get('id')}` {task.get('description')} ({task.get('owner')})")
    
    embed = discord.Embed(
        title=f"📆 Tasks tuần này ({monday.strftime('%d/%m')} - {sunday.strftime('%d/%m')})",
        description="\n".join(lines),
        color=discord.Color.blue()
    )
    
    # Stats
    done = len([t for t in week_tasks if t.get("done")])
    total = len(week_tasks)
    embed.set_footer(text=f"Hoàn thành: {done}/{total} ({done/total*100:.0f}%)" if total > 0 else "")
    
    await interaction.response.send_message(embed=embed)


@tree.command(name="overdue", description="Xem tasks quá hạn")
async def overdue_command(interaction: discord.Interaction):
    """Show all overdue tasks."""
    overdue = get_overdue_tasks()
    
    if not overdue:
        await interaction.response.send_message(
            "🎉 Không có task nào quá hạn!",
            ephemeral=True
        )
        return
    
    lines = []
    for task in overdue:
        priority_icon = "🔴" if "MUST" in task.get("priority", "") else "🟡"
        lines.append(f"⚠️ {priority_icon} `{task.get('id')}` [{task.get('date')}] {task.get('description')} ({task.get('owner')})")
    
    embed = discord.Embed(
        title="⚠️ Tasks Quá Hạn",
        description="\n".join(lines),
        color=discord.Color.red()
    )
    embed.set_footer(text=f"Tổng: {len(overdue)} tasks quá hạn")
    
    await interaction.response.send_message(embed=embed)


@tree.command(name="upcoming", description="Xem tasks sắp tới (2-3 ngày)")
async def upcoming_command(interaction: discord.Interaction):
    """Show upcoming tasks for next 3 days."""
    upcoming = get_upcoming_tasks(days=3)
    
    if not upcoming:
        await interaction.response.send_message(
            "Không có task nào trong 3 ngày tới.",
            ephemeral=True
        )
        return
    
    # Group by date
    tasks_by_date = {}
    for task in upcoming:
        task_date = task.get("date", "")
        if task_date not in tasks_by_date:
            tasks_by_date[task_date] = []
        tasks_by_date[task_date].append(task)
    
    lines = []
    for date_str in sorted(tasks_by_date.keys()):
        lines.append(f"\n**📅 {date_str}**")
        for task in tasks_by_date[date_str]:
            priority_icon = "🔴" if "MUST" in task.get("priority", "") else "🟡"
            lines.append(f"  {priority_icon} `{task.get('id')}` {task.get('description')} ({task.get('owner')})")
    
    embed = discord.Embed(
        title="📋 Tasks Sắp Tới (3 ngày)",
        description="\n".join(lines),
        color=discord.Color.gold()
    )
    
    await interaction.response.send_message(embed=embed)


@tree.command(name="remind", description="Nhắc nhở một người cụ thể")
@app_commands.describe(member="Người cần nhắc nhở", message="Nội dung nhắc nhở")
async def remind_command(interaction: discord.Interaction, member: discord.Member, message: str = ""):
    """Send a reminder to a specific user."""
    # Get user's pending tasks
    user_name = None
    for name, uid in USER_IDS.items():
        if uid == member.id:
            user_name = name
            break
    
    tasks = get_tasks_for_user(user_name) if user_name else []
    
    lines = []
    if message:
        lines.append(f"📢 **Nhắc nhở:** {message}\n")
    
    if tasks:
        lines.append(f"**Các task pending của bạn:**")
        for task in tasks[:5]:  # Limit to 5 tasks
            priority_icon = "🔴" if "MUST" in task.get("priority", "") else "🟡"
            lines.append(f"  {priority_icon} `{task.get('id')}` [{task.get('date')}] {task.get('description')}")
    
    embed = discord.Embed(
        title=f"⏰ Nhắc nhở cho {member.display_name}",
        description="\n".join(lines) if lines else "Hãy cập nhật tiến độ công việc!",
        color=discord.Color.orange()
    )
    embed.set_footer(text=f"Từ: {interaction.user.display_name}")
    
    await interaction.response.send_message(content=f"{member.mention}", embed=embed)


@tree.command(name="summary", description="Báo cáo tổng kết tuần")
async def summary_command(interaction: discord.Interaction):
    """Show weekly summary report."""
    week_tasks, monday, sunday = get_week_tasks()
    overdue = get_overdue_tasks()
    
    # Calculate stats
    total = len(week_tasks)
    done = len([t for t in week_tasks if t.get("done")])
    pending = total - done
    
    # Stats by owner
    by_owner = {}
    for task in week_tasks:
        owner = task.get("owner", "Unassigned")
        if owner not in by_owner:
            by_owner[owner] = {"total": 0, "done": 0}
        by_owner[owner]["total"] += 1
        if task.get("done"):
            by_owner[owner]["done"] += 1
    
    lines = [
        f"**📆 Tuần: {monday.strftime('%d/%m')} - {sunday.strftime('%d/%m')}**\n",
        f"📊 **Tổng quan:**",
        f"  • Tổng tasks tuần này: {total}",
        f"  • Hoàn thành: {done} ✅",
        f"  • Đang chờ: {pending} ⏳",
        f"  • Tiến độ: {done/total*100:.1f}%" if total > 0 else "  • Tiến độ: 0%",
        "",
        f"👥 **Theo thành viên:**"
    ]
    
    for owner, stats in by_owner.items():
        pct = stats["done"]/stats["total"]*100 if stats["total"] > 0 else 0
        status = "✅" if pct == 100 else "🟡" if pct >= 50 else "🔴"
        lines.append(f"  {status} {owner}: {stats['done']}/{stats['total']} ({pct:.0f}%)")
    
    if overdue:
        lines.append(f"\n⚠️ **Tasks quá hạn:** {len(overdue)}")
        for task in overdue[:3]:
            lines.append(f"  • [{task.get('date')}] {task.get('description')} ({task.get('owner')})")
        if len(overdue) > 3:
            lines.append(f"  ... và {len(overdue) - 3} tasks khác")
    
    embed = discord.Embed(
        title="📈 Báo Cáo Tổng Kết Tuần",
        description="\n".join(lines),
        color=discord.Color.purple(),
        timestamp=datetime.now(tz)
    )
    
    await interaction.response.send_message(embed=embed)


@tree.command(name="checkprogress", description="Kiểm tra ai chưa hoàn thành tasks hôm nay")
async def checkprogress_command(interaction: discord.Interaction):
    """Manually trigger progress check to see who hasn't completed today's tasks."""
    today_str = get_today_str()
    tasks_today = get_tasks_for_date(today_str)
    pending_tasks = [t for t in tasks_today if not t.get("done", False)]
    
    if not pending_tasks:
        await interaction.response.send_message(
            "🎉 Tất cả tasks hôm nay đã hoàn thành!",
            ephemeral=False
        )
        return
    
    # Group pending tasks by user
    pending_by_user = {}
    for task in pending_tasks:
        owner = task.get("owner", "Unassigned")
        if owner not in pending_by_user:
            pending_by_user[owner] = []
        pending_by_user[owner].append(task)
    
    description_lines = [f"**📋 Tasks hôm nay ({today_str}) chưa hoàn thành:**\n"]
    
    for owner, user_tasks in pending_by_user.items():
        user_id = USER_IDS.get(owner)
        mention = f"<@{user_id}>" if user_id else f"**{owner}**"
        description_lines.append(f"{mention}: **{len(user_tasks)} task(s) pending**")
        
        # Show task details
        for task in user_tasks[:3]:  # Limit to 3 tasks per user
            priority_icon = "🔴" if "MUST" in task.get("priority", "") else "🟡"
            description_lines.append(f"  {priority_icon} `{task.get('id')}` {task.get('description')}")
        
        if len(user_tasks) > 3:
            description_lines.append(f"  ... và {len(user_tasks) - 3} task(s) khác")
        
        description_lines.append("")
    
    description_lines.append(
        f"💬 Vui lòng cập nhật trạng thái trong <#{PROGRESS_UPDATE_CHANNEL_ID}>"
    )
    
    embed = discord.Embed(
        title="🔍 Kiểm Tra Tiến Độ",
        description="\n".join(description_lines),
        color=discord.Color.orange(),
        timestamp=datetime.now(tz)
    )
    
    done_count = len(tasks_today) - len(pending_tasks)
    embed.set_footer(text=f"Hoàn thành: {done_count}/{len(tasks_today)} tasks ({done_count/len(tasks_today)*100:.0f}%)" if len(tasks_today) > 0 else "")
    
    await interaction.response.send_message(embed=embed)


# ========== DEADLINE REMINDER (AUTO) ==========

@tasks.loop(minutes=1)
async def deadline_reminder():
    """Check for tasks with approaching deadlines and notify users."""
    now = datetime.now(tz)
    
    # Run at 08:00 and 20:00
    if now.hour not in [8, 20] or now.minute != 0:
        return
    
    deadline_tasks = get_deadline_soon_tasks()
    
    if not deadline_tasks:
        return
    
    channel = bot.get_channel(ANNOUNCEMENTS_CHANNEL_ID)
    if not channel:
        print(f"Warning: Could not find announcements channel {ANNOUNCEMENTS_CHANNEL_ID}")
        return
    
    # Group by owner
    tasks_by_owner = {}
    for task in deadline_tasks:
        owner = task.get("owner", "")
        if owner not in tasks_by_owner:
            tasks_by_owner[owner] = []
        tasks_by_owner[owner].append(task)
    
    for owner, tasks in tasks_by_owner.items():
        user_id = USER_IDS.get(owner)
        
        lines = []
        for task in tasks:
            priority_icon = "🔴" if "MUST" in task.get("priority", "") else "🟡"
            lines.append(f"  {priority_icon} `{task.get('id')}` [{task.get('date')}] {task.get('description')}")
        
        embed = discord.Embed(
            title="⏰ Nhắc Nhở Deadline Sắp Tới!",
            description=f"**{owner}**, bạn có {len(tasks)} task sắp hết hạn:\n\n" + "\n".join(lines),
            color=discord.Color.red(),
            timestamp=now
        )
        embed.set_footer(text="Vui lòng hoàn thành hoặc update tiến độ")
        
        mention = f"<@{user_id}>" if user_id else f"**{owner}**"
        await channel.send(content=mention, embed=embed)
    
    print(f"Sent deadline reminders for {len(deadline_tasks)} tasks at {now}")


# Error handling
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors."""
    print(f"Command error: {error}")




# Run bot
if __name__ == "__main__":
    print("Starting Research Project Task Management Bot...")
    print("Press Ctrl+C to stop.")
    bot.run(BOT_TOKEN)
