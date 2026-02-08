"""
Google Sheets Integration Module
Sync tasks from Google Sheets to Discord Bot

Instructions:
1. Follow GOOGLE_SHEETS_SETUP.md to get credentials.json
2. Add GOOGLE_SHEET_ID to config.py
3. Bot will automatically sync from Google Sheets instead of tasks.json
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from zoneinfo import ZoneInfo
import os


def get_sheets_client():
    """Create and return Google Sheets client."""
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Try to load from environment variable (for Railway deployment)
    from config import GOOGLE_CREDENTIALS_JSON
    if GOOGLE_CREDENTIALS_JSON:
        import json
        from google.oauth2.service_account import Credentials
        
        creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    
    # Otherwise load from credentials.json file (for local development)
    creds_file = os.path.join(os.path.dirname(__file__), 'credentials.json')
    
    if not os.path.exists(creds_file):
        raise FileNotFoundError(
            "credentials.json not found. "
            "Please follow GOOGLE_SHEETS_SETUP.md to create it."
        )
    
    creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
    client = gspread.authorize(creds)
    
    return client


def load_tasks_from_sheets(sheet_id, worksheet_name="Timeline Feb 7-22", tz=ZoneInfo("Asia/Ho_Chi_Minh")):
    """
    Load tasks from Google Sheets.
    
    Expected columns:
    - Date (str): Date in DD/MM format (e.g., 07/02)
    - Task Name (str): Name of the task
    - Task Description (str): Detailed description
    - Priority (str): MUST or NICE
    - Owner (str): Name of person responsible
    - Dependencies (str): Dependencies
    - Deliverable (str): Expected deliverable
    - Status (str): "Done", "To do", "In progress", etc.
    - Notes (str): Additional notes
    
    Args:
        sheet_id (str): Google Sheet ID
        worksheet_name (str): Name of the worksheet tab to read from
        tz (ZoneInfo): Timezone
    
    Returns:
        dict: {"tasks": [list of task dicts]}
    """
    client = get_sheets_client()
    sheet = client.open_by_key(sheet_id)
    
    try:
        worksheet = sheet.worksheet(worksheet_name)
    except Exception as e:
        print(f"Error: Could not find worksheet '{worksheet_name}'")
        print(f"Available worksheets: {[ws.title for ws in sheet.worksheets()]}")
        raise e
    
    # Get all values as raw data
    all_values = worksheet.get_all_values()
    
    if len(all_values) < 2:
        print("Warning: Sheet has less than 2 rows (header + data)")
        return {"tasks": []}
    
    # First row is header
    headers = all_values[0]
    
    # Map column names (handle case-insensitive)
    col_map = {}
    date_col_idx = None
    
    for idx, header in enumerate(headers):
        header_str = str(header).strip()
        header_lower = header_str.lower()
        col_map[header_lower] = idx
        
        # Check if this header looks like a date (DD/MM format)
        import re
        if re.match(r'^\d{2}/\d{2}', header_str):
            date_col_idx = idx
            col_map['date'] = idx
    
    print(f"Debug: Found columns: {list(col_map.keys())}")
    print(f"Debug: Date column index: {date_col_idx}")
    
    tasks = []
    task_id_counter = 1
    current_date = None  # For handling merged date cells
    
    # Process each data row
    for row in all_values[1:]:  # Skip header row
        # Ensure row has enough columns
        while len(row) < len(headers):
            row.append('')
        
        # Get task name - try different column names
        task_name = ''
        for col_name in ['task name', 'task', 'name']:
            if col_name in col_map:
                task_name = str(row[col_map[col_name]]).strip()
                break
        
        # Skip if no task name
        if not task_name:
            continue
        
        # Get date - use detected date column or column 0
        date_col = date_col_idx if date_col_idx is not None else 0
        date_str = str(row[date_col]).strip()

        
        if date_str:
            # Parse date - handle formats like "07/02 (T7)"
            date_parts = date_str.split('(')[0].strip()
            current_date = date_parts
        elif current_date:
            # Use previous date for merged cells
            date_parts = current_date
        else:
            # Skip rows without date
            continue
        
        # Generate task ID
        task_id = f"T{task_id_counter:03d}"
        task_id_counter += 1
        
        # Get owner
        owner = ''
        for col_name in ['owner', 'người thực hiện']:
            if col_name in col_map:
                owner = str(row[col_map[col_name]]).strip()
                break
        
        # Get task description
        task_desc = ''
        for col_name in ['task description', 'description', 'mô tả']:
            if col_name in col_map:
                task_desc = str(row[col_map[col_name]]).strip()
                break
        
        # Get priority
        priority = 'MUST'
        for col_name in ['priority', 'ưu tiên']:
            if col_name in col_map:
                priority = str(row[col_map[col_name]]).strip().upper()
                break
        
        # Get status
        status = 'To do'
        for col_name in ['status', 'trạng thái']:
            if col_name in col_map:
                status = str(row[col_map[col_name]]).strip()
                break
        
        is_done = status.lower() in ['done', 'hoàn thành', 'completed']
        
        # Get other fields
        deliverable = ''
        for col_name in ['deliverable', 'kết quả']:
            if col_name in col_map:
                deliverable = str(row[col_map[col_name]]).strip()
                break
        
        dependencies = ''
        for col_name in ['dependencies', 'phụ thuộc']:
            if col_name in col_map:
                dependencies = str(row[col_map[col_name]]).strip()
                break
        
        notes = ''
        for col_name in ['notes', 'ghi chú']:
            if col_name in col_map:
                notes = str(row[col_map[col_name]]).strip()
                break
        
        task = {
            'id': task_id,
            'date': date_parts,
            'owner': owner,
            'description': task_name,
            'full_description': task_desc,
            'priority': priority,
            'done': is_done,
            'status': status,
            'deliverable': deliverable,
            'dependencies': dependencies,
            'notes': notes,
        }
        
        tasks.append(task)
    
    print(f"Debug: Loaded {len(tasks)} tasks from Google Sheets")
    return {"tasks": tasks}




def save_task_to_sheets(sheet_id, task_name, updates, worksheet_name="Timeline Feb 7-22"):
    """
    Update a specific task in Google Sheets by Task Name.
    
    Args:
        sheet_id (str): Google Sheet ID
        task_name (str): Task Name to update
        updates (dict): Fields to update, e.g., {"Status": "Done", "Notes": "Completed"}
        worksheet_name (str): Name of the worksheet tab
    """
    client = get_sheets_client()
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet(worksheet_name)
    
    # Find the cell with this task name
    try:
        cell = worksheet.find(task_name, in_column=2)  # Task Name is column B (2)
    except Exception:
        raise ValueError(f"Task '{task_name}' not found in Google Sheets")
    
    row_num = cell.row
    
    # Get header row to map column names
    headers = worksheet.row_values(1)
    
    # Update each field
    for field_name, value in updates.items():
        if field_name in headers:
            col_num = headers.index(field_name) + 1
            worksheet.update_cell(row_num, col_num, value)



def mark_task_done_in_sheets(sheet_id, task_description, completed_by, worksheet_name="Timeline Feb 7-22", tz=ZoneInfo("Asia/Ho_Chi_Minh")):
    """
    Mark a task as done in Google Sheets by changing Status to "Done".
    
    Args:
        sheet_id (str): Google Sheet ID
        task_description (str): Task Name/description to mark done
        completed_by (str): User ID who completed it
        worksheet_name (str): Name of the worksheet tab
        tz (ZoneInfo): Timezone for timestamp
    """
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M")
    
    updates = {
        'Status': 'Done',
        'Notes': f'Completed by {completed_by} at {now}',
    }
    
    save_task_to_sheets(sheet_id, task_description, updates, worksheet_name)



def test_connection(sheet_id):
    """Test connection to Google Sheets."""
    try:
        client = get_sheets_client()
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.sheet1
        
        title = sheet.title
        rows = len(worksheet.get_all_records())
        
        print(f"✅ Successfully connected to Google Sheets")
        print(f"   Sheet title: {title}")
        print(f"   Number of tasks: {rows}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Google Sheets")
        print(f"   Error: {e}")
        return False


if __name__ == "__main__":
    # Test script
    from config import GOOGLE_SHEET_ID
    
    print("Testing Google Sheets connection...")
    test_connection(GOOGLE_SHEET_ID)
