# Google Sheets Integration cho Discord Bot

## Hiện tại bot đang lấy tasks từ đâu?

**Bot hiện tại đang đọc tasks từ file `tasks.json`** (trong folder `discord_bot/`).

File này chứa 46 tasks đã được pre-load sẵn từ task tracker (Feb 8-22).

---

## Để sync với Google Sheets:

### Bước 1: Tạo Google Sheets API credentials

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới (hoặc chọn project có sẵn)
3. Enable **Google Sheets API**:
   - APIs & Services → Enable APIs and Services
   - Tìm "Google Sheets API" → Enable
4. Tạo Service Account:
   - APIs & Services → Credentials → Create Credentials → Service Account
   - Đặt tên: `discord-bot-sheets-reader`
   - Role: **Editor**
5. Tạo JSON Key:
   - Click vào service account vừa tạo
   - Keys tab → Add Key → Create new key → JSON
   - Tải file JSON về, đổi tên thành `credentials.json`
   - Lưu vào folder `discord_bot/`

### Bước 2: Chia sẻ Google Sheets với Service Account

1. Mở Google Sheets chứa tasks
2. Click **Share**
3. Paste **email của service account** (dạng `xxx@yyy.iam.gserviceaccount.com`)
4. Chọn role: **Editor** → Send

### Bước 3: Copy Sheet ID

Sheet ID nằm trong URL:
```
https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
```

---

## Cấu trúc Google Sheet cần có

Sheet cần có các cột sau:

| ID | Date | Owner | Description | Priority | Done | Created At | Completed At | Completed By |
|----|------|-------|-------------|----------|------|------------|--------------|--------------|
| T001 | 08/02 | Tuấn | Tạo Facebook page | MUST | TRUE | 2026-02-07 | 2026-02-08 | 972863389690920971 |
| T002 | 08/02 | Tuấn | Tạo group chat | MUST | FALSE | 2026-02-07 | | |

---

## Setup Integration

Cài dependencies:
```bash
pip install gspread google-auth
```

Sau đó mình sẽ tạo file `sheets_sync.py` để sync Google Sheets với bot.
