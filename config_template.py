"""
Discord Bot Configuration Template
Copy this file to config.py and fill in your values.
"""
import os

# Discord Bot Token (from Developer Portal → Bot → Token)
# For Railway: Set as environment variable BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Channel IDs (Right-click channel → Copy ID)
DAILY_TASKS_CHANNEL_ID = int(os.getenv("DAILY_TASKS_CHANNEL_ID", "1470050961883140289"))
PROGRESS_UPDATE_CHANNEL_ID = int(os.getenv("PROGRESS_UPDATE_CHANNEL_ID", "1470050998025326668"))
ANNOUNCEMENTS_CHANNEL_ID = int(os.getenv("ANNOUNCEMENTS_CHANNEL_ID", "1470050849030930526"))

# User IDs (Right-click user → Copy ID)
USER_IDS = {
    "Tuấn": int(os.getenv("USER_ID_TUAN", "972863389690920971")),
    "Thắng": int(os.getenv("USER_ID_THANG", "1081547094520766474")),
    "Ngọc": int(os.getenv("USER_ID_NGOC", "123456789012345678")),
    "Tú": int(os.getenv("USER_ID_TU", "1388827370341007447")),
}

# Role IDs (Server Settings → Roles → Right-click → Copy ID)
ROLE_IDS = {
    "Research Lead": int(os.getenv("ROLE_RESEARCH_LEAD", "1470051164254109787")),
    "Methodology": int(os.getenv("ROLE_METHODOLOGY", "1470051310479999144")),
    "Data & Tools": int(os.getenv("ROLE_DATA_TOOLS", "1470051402561880145")),
    "Logistics": int(os.getenv("ROLE_LOGISTICS", "1470051442713825424")),
}

# Timezone for scheduled messages
TIMEZONE = os.getenv("TIMEZONE", "Asia/Ho_Chi_Minh")

# ========== GOOGLE SHEETS INTEGRATION ==========
USE_GOOGLE_SHEETS = os.getenv("USE_GOOGLE_SHEETS", "True") == "True"

# Google Sheet ID (from URL)
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "1JGTBm1j8dyXzoeklIOUrZoXaGz2MFpuA96mLAZCGHeU")

# Worksheet tab name
GOOGLE_SHEET_WORKSHEET = os.getenv("GOOGLE_SHEET_WORKSHEET", "Timeline Feb 7-22")
