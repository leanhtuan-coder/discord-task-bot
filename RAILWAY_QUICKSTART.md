# 🚀 Quick Start: Deploy to Railway

## Bước 1: Push code lên GitHub

```bash
cd discord_bot
git init
git add .
git commit -m "Initial commit"

# Tạo repo trên GitHub: https://github.com/new
# Sau đó:
git remote add origin https://github.com/YOUR_USERNAME/discord-task-bot.git
git branch -M main
git push -u origin main
```

## Bước 2: Lấy Google Credentials JSON (1 dòng)

```bash
python -c "import json; print(json.dumps(json.load(open('credentials.json'))))"
```

Copy output (bao gồm `{}`)

## Bước 3: Deploy trên Railway

1. **Login:** https://railway.app/ → Login with GitHub
2. **New Project:** Deploy from GitHub repo → Chọn `discord-task-bot`
3. **Add Variables:** Tab "Variables" → Add:

```
BOT_TOKEN = MTQ3MDA1MzYyNTU2Mzk3NTcyMA.GZI6gT.38Zmyun4w5nnFvH2Nfgoj-f5cupvAfiH1iGBU8
GOOGLE_SHEET_ID = 1JGTBm1j8dyXzoeklIOUrZoXaGz2MFpuA96mLAZCGHeU
GOOGLE_CREDENTIALS_JSON = {"type":"service_account",...}  ← paste JSON từ bước 2
GOOGLE_SHEET_WORKSHEET = Timeline Feb 7-22
```

4. **Save** → Railway tự động deploy

## Bước 4: Kiểm tra

**Xem logs:**
Railway → Deployments → View Logs

**Tìm:**
```
Bot is online: DSA Research Bot#5514
Synced 10 slash command(s)
```

## ✅ Done!

Bot giờ chạy 24/7! Mỗi khi push code mới, Railway tự động redeploy.

---

📖 **Chi tiết:** Xem [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)
