# 🚀 Deploy Discord Bot to Railway

Hướng dẫn deploy bot lên Railway để chạy 24/7 miễn phí.

---

## 📋 Prerequisites

- ✅ Bot đã chạy được trên máy local
- ✅ Có file `credentials.json` từ Google Cloud
- ✅ Có tài khoản GitHub
- ✅ Có tài khoản Railway (đăng ký bằng GitHub)

---

## 🔧 Bước 1: Chuẩn bị GitHub Repository

### 1.1. Khởi tạo Git (nếu chưa có)

```bash
cd discord_bot
git init
git add .
git commit -m "Initial commit: Discord bot with Google Sheets"
```

### 1.2. Tạo repository trên GitHub

1. Vào https://github.com/new
2. Tạo repository mới (ví dụ: `discord-task-bot`)
3. **KHÔNG** chọn "Add a README file"
4. Click "Create repository"

### 1.3. Push code lên GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/discord-task-bot.git
git branch -M main
git push -u origin main
```

> ⚠️ **Lưu ý:** File `credentials.json` và `config.py` sẽ KHÔNG được push lên GitHub (đã có trong `.gitignore`)

---

## 🚂 Bước 2: Deploy lên Railway

### 2.1. Đăng nhập Railway

1. Vào https://railway.app/
2. Click "Login with GitHub"
3. Cho phép Railway truy cập GitHub repositories

### 2.2. Tạo Project mới

1. Click "New Project"
2. Chọn "Deploy from GitHub repo"
3. Chọn repository `discord-task-bot` vừa tạo
4. Railway sẽ tự động detect và deploy

### 2.3. Thêm Environment Variables

Click vào project → Tab "Variables" → Add các biến sau:

#### **Bắt buộc:**

| Variable Name | Value | Ghi chú |
|--------------|-------|---------|
| `BOT_TOKEN` | `MTQ3MDA1...` | Discord bot token |
| `GOOGLE_SHEET_ID` | `1JGTBm1j8d...` | ID của Google Sheet |
| `GOOGLE_CREDENTIALS_JSON` | `{"type":"service_account",...}` | Nội dung file credentials.json |

#### **Tùy chọn (nếu khác default):**

| Variable Name | Default Value |
|--------------|---------------|
| `GOOGLE_SHEET_WORKSHEET` | `Timeline Feb 7-22` |
| `DAILY_TASKS_CHANNEL_ID` | `1470050961883140289` |
| `PROGRESS_UPDATE_CHANNEL_ID` | `1470050998025326668` |
| `ANNOUNCEMENTS_CHANNEL_ID` | `1470050849030930526` |
| `TIMEZONE` | `Asia/Ho_Chi_Minh` |

#### **User IDs (nếu cần):**
- `USER_ID_TUAN`, `USER_ID_THANG`, `USER_ID_NGOC`, `USER_ID_TU`

#### **Role IDs (nếu cần):**
- `ROLE_RESEARCH_LEAD`, `ROLE_METHODOLOGY`, `ROLE_DATA_TOOLS`, `ROLE_LOGISTICS`

---

## 📝 Bước 3: Lấy giá trị `GOOGLE_CREDENTIALS_JSON`

### Option 1: Sử dụng Python (dễ nhất)

```bash
python -c "import json; print(json.dumps(json.load(open('credentials.json'))))"
```

Copy toàn bộ output (bao gồm cả dấu `{}`) và paste vào Railway.

### Option 2: Manual

1. Mở file `credentials.json`
2. Copy toàn bộ nội dung
3. **Minify JSON** tại https://jsonformatter.org/json-minifier
4. Paste vào Railway

> ⚠️ **Quan trọng:** Phải là JSON trên 1 dòng, không có xuống dòng!

---

## ✅ Bước 4: Kiểm tra Deployment

### 4.1. Xem Logs

1. Vào Railway project → Tab "Deployments"
2. Click vào deployment đang chạy
3. Tab "Logs" sẽ hiển thị:

```
Google Sheets integration enabled.
Starting Research Project Task Management Bot...
Bot is online: DSA Research Bot#5514
Connected to 1 server(s)
Synced 10 slash command(s) to Research Project
Scheduled tasks started.
```

### 4.2. Test Bot trên Discord

1. Gõ `/` trong Discord
2. Kiểm tra 10 commands xuất hiện
3. Test `/today`, `/week`, `/status`

---

## 🔄 Cập nhật Code

Khi bạn sửa code:

```bash
git add .
git commit -m "Update: description of changes"
git push
```

Railway sẽ **tự động** detect và redeploy!

---

## 💰 Railway Free Tier

- **$5 credit/tháng** (miễn phí)
- Đủ để chạy bot 24/7
- Không cần thẻ credit
- Auto sleep sau 500h/tháng (vẫn đủ cho bot)

---

## 🐛 Troubleshooting

### Bot không online?

**Check logs:**
```
Railway Project → Deployments → View Logs
```

**Common issues:**

| Lỗi | Giải pháp |
|-----|-----------|
| `BOT_TOKEN` invalid | Check token Discord Developer Portal |
| `credentials.json` not found | Check `GOOGLE_CREDENTIALS_JSON` env var |
| Import error | Check `requirements.txt` có đầy đủ |
| Google Sheets API error | Check sheet sharing với service account |

### Credentials.json issues:

1. **Check format:** Phải là JSON minified (1 dòng)
2. **Check quotes:** Sử dụng double quotes `"`, không phải single quotes `'`
3. **Re-generate:** Tạo lại service account key nếu cần

### Bot restart liên tục:

Check logs xem lỗi gì, thường do:
- Missing environment variables
- Invalid Google credentials
- Sheet không được share

---

## 📞 Support

Nếu gặp vấn đề:
1. Check Railway logs
2. Verify tất cả environment variables
3. Test bot locally trước khi deploy

---

## 🎉 Done!

Bot của bạn giờ chạy 24/7 trên Railway! 🚀
