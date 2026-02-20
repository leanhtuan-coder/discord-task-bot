"""
Discord Bot Configuration
Reads from environment variables (for Railway) or uses hardcoded values (for local dev)
"""
import os

# Load local development config if exists (for local testing)
# Create .env.local file with: BOT_TOKEN = "your_token_here"
_local_config_path = os.path.join(os.path.dirname(__file__), '.env.local')
if os.path.exists(_local_config_path):
    with open(_local_config_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ.setdefault(key, value)

# Discord Bot Token - Railway will use environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Channel IDs
DAILY_TASKS_CHANNEL_ID = int(os.getenv("DAILY_TASKS_CHANNEL_ID", "1470050961883140289"))
PROGRESS_UPDATE_CHANNEL_ID = int(os.getenv("PROGRESS_UPDATE_CHANNEL_ID", "1470050998025326668"))
ANNOUNCEMENTS_CHANNEL_ID = int(os.getenv("ANNOUNCEMENTS_CHANNEL_ID", "1470050849030930526"))

# User IDs
USER_IDS = {
    "Tuấn": int(os.getenv("USER_ID_TUAN", "972863389690920971")),
    "Thắng": int(os.getenv("USER_ID_THANG", "1081547094520766474")),
    "Ngọc": int(os.getenv("USER_ID_NGOC", "1460205441459163231")),
    "Tú": int(os.getenv("USER_ID_TU", "1388827370341007447")),
}

# Role IDs
ROLE_IDS = {
    "Research Lead": int(os.getenv("ROLE_RESEARCH_LEAD", "1470051164254109787")),
    "Methodology": int(os.getenv("ROLE_METHODOLOGY", "1470051310479999144")),
    "Data & Tools": int(os.getenv("ROLE_DATA_TOOLS", "1470051402561880145")),
    "Logistics": int(os.getenv("ROLE_LOGISTICS", "1470051442713825424")),
}

# Timezone
TIMEZONE = os.getenv("TIMEZONE", "Asia/Ho_Chi_Minh")

# ========== GOOGLE SHEETS INTEGRATION ==========
USE_GOOGLE_SHEETS = os.getenv("USE_GOOGLE_SHEETS", "True") == "True"
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "1JGTBm1j8dyXzoeklIOUrZoXaGz2MFpuA96mLAZCGHeU")

# Worksheet tabs to read tasks from (comma-separated for multiple)
GOOGLE_SHEET_WORKSHEET = os.getenv("GOOGLE_SHEET_WORKSHEET", "Timeline Feb 7-22,Post-Feb-22 Execution")

# ========== GOOGLE SERVICE ACCOUNT (for Railway) ==========
# Railway will use this environment variable for credentials.json content
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "")


