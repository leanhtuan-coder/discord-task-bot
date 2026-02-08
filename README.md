# Discord Bot - Research Project Task Management

## Hệ thống quản lý công việc cho dự án nghiên cứu
**Guided AI Use in Learning Data Structures and Algorithms**

---

## 1. DISCORD SERVER SETUP

### 1.1 Server Name (Đề xuất)

Chọn một trong các phương án sau:

1. **DSA + AI Research Project** (ngắn gọn, rõ ràng)
2. **Guided AI Use in DSA – Research Team** (đầy đủ tên nghiên cứu)
3. **FPT Research: AI in DSA Learning** (thể hiện trường)

---

### 1.2 Channel Structure

```
📁 PROJECT OVERVIEW
 ├─ #announcements          → Thông báo quan trọng từ Research Lead
 ├─ #research-scope         → Mô tả nghiên cứu, RQs, constraints
 ├─ #timeline-milestones    → Các mốc thời gian quan trọng

📁 TASK & PROGRESS
 ├─ #daily-tasks            → Bot gửi task hằng ngày
 ├─ #progress-update        → Team cập nhật tiến độ
 ├─ #task-discussion        → Thảo luận về task, blockers

📁 RESEARCH CONTENT
 ├─ #methodology            → Design nghiên cứu, instruments
 ├─ #experiment-design      → Pre-test, intervention, post-test
 ├─ #data-analysis          → Data cleaning, statistical analysis
 ├─ #paper-writing          → Introduction, Related Work, Results

📁 GENERAL
 ├─ #resources              → Links, papers, tools hữu ích
 ├─ #meeting-notes          → Ghi chép họp team
 ├─ #random                 → Off-topic, casual chat
```

---

### 1.3 Roles

| Role | Màu (Hex) | Trách nhiệm |
|------|-----------|-------------|
| `@Research Lead` | #E74C3C (đỏ) | Điều phối, timeline, recruitment, coordination |
| `@Methodology` | #3498DB (xanh dương) | Research design, instruments, rubrics, analysis |
| `@Data & Tools` | #2ECC71 (xanh lá) | Google Forms, LMS, data visualization |
| `@Logistics` | #F39C12 (cam) | Room booking, materials, attendance |
| `@Bot` | #95A5A6 (xám) | Bot tự động |

**Gán role cho team:**
- Tuấn → @Research Lead
- Thắng → @Methodology
- Ngọc → @Data & Tools
- Tú → @Logistics

---

## 2. BOT ARCHITECTURE

### 2.1 Tổng quan

```
┌─────────────────────────────────────────────────┐
│                  Discord Bot                     │
├─────────────────────────────────────────────────┤
│  Scheduler (APScheduler)                        │
│  ├─ 09:00 → Daily Task Reminder                 │
│  └─ 22:00 → End-of-Day Progress Reminder        │
├─────────────────────────────────────────────────┤
│  Slash Commands                                  │
│  ├─ /today    → Tasks hôm nay của team          │
│  ├─ /mytasks  → Tasks của user                  │
│  └─ /done     → Đánh dấu hoàn thành             │
├─────────────────────────────────────────────────┤
│  Data Source                                     │
│  └─ tasks.json (MVP)                            │
│      ↓ (future)                                 │
│  └─ Google Sheets sync                          │
└─────────────────────────────────────────────────┘
```

### 2.2 File Structure

```
discord_bot/
├── bot.py              # Main bot code
├── tasks.json          # Task data (MVP)
├── config.py           # Configuration (token, channels)
├── requirements.txt    # Dependencies
└── README.md           # This file
```

---

## 3. SETUP INSTRUCTIONS

### 3.1 Tạo Discord Bot

1. Truy cập [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application** → Đặt tên: `DSA Research Bot`
3. Vào tab **Bot** → Click **Add Bot**
4. Bật các Intents:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
5. Copy **TOKEN** (quan trọng, giữ bí mật)

### 3.2 Mời Bot vào Server

1. Vào tab **OAuth2** → **URL Generator**
2. Chọn Scopes: `bot`, `applications.commands`
3. Chọn Bot Permissions:
   - Send Messages
   - Send Messages in Threads
   - Embed Links
   - Mention Everyone
   - Use Slash Commands
4. Copy URL → Mở trong browser → Chọn server → Authorize

### 3.3 Cài đặt môi trường

```bash
# Tạo virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt
```

### 3.4 Cấu hình

Tạo file `config.py`:

```python
# Discord Bot Token (lấy từ Developer Portal)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Channel IDs (Right-click channel → Copy ID)
DAILY_TASKS_CHANNEL_ID = 123456789012345678
PROGRESS_UPDATE_CHANNEL_ID = 123456789012345678

# User IDs (Right-click user → Copy ID)
USER_IDS = {
    "Tuấn": 123456789012345678,
    "Thắng": 123456789012345678,
    "Ngọc": 123456789012345678,
    "Tú": 123456789012345678,
}

# Role IDs (Server Settings → Roles → Right-click → Copy ID)
ROLE_IDS = {
    "Research Lead": 123456789012345678,
    "Methodology": 123456789012345678,
    "Data & Tools": 123456789012345678,
    "Logistics": 123456789012345678,
}

# Timezone
TIMEZONE = "Asia/Ho_Chi_Minh"
```

### 3.5 Chạy Bot

```bash
python bot.py
```

---

## 4. USAGE

### Slash Commands

| Command | Mô tả | Ví dụ |
|---------|-------|-------|
| `/today` | Xem tất cả tasks hôm nay | `/today` |
| `/mytasks` | Xem tasks của bạn | `/mytasks` |
| `/done <task_id>` | Đánh dấu task hoàn thành | `/done T001` |
| `/addtask` | Thêm task mới (Lead only) | `/addtask ...` |

### Automatic Messages

- **09:00**: Bot gửi danh sách tasks của ngày vào #daily-tasks
- **22:00**: Bot nhắc cập nhật tiến độ vào #daily-tasks

---

## 5. FUTURE IMPROVEMENTS

- [ ] Sync với Google Sheets thay vì JSON
- [ ] Weekly summary report
- [ ] Task completion statistics
- [ ] Reminder DM cho người chưa cập nhật
- [ ] Integration với GitHub issues

---

## 6. TROUBLESHOOTING

**Bot không online:**
- Kiểm tra token đúng chưa
- Kiểm tra Intents đã bật chưa

**Slash commands không hiện:**
- Đợi 1-2 giờ để Discord sync
- Hoặc kick bot khỏi server rồi add lại

**Không mention được:**
- Kiểm tra bot có permission Mention Everyone không
- Kiểm tra User/Role ID đúng chưa
