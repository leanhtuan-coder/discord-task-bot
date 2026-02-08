#!/usr/bin/env python
"""Test multi-worksheet loading"""
from sheets_sync import load_tasks_from_sheets

# Test loading from both worksheets
tasks_data = load_tasks_from_sheets(
    '1JGTBm1j8dyXzoeklIOUrZoXaGz2MFpuA96mLAZCGHeU',
    'Timeline Feb 7-22,Post-Feb-22 Execution'
)

tasks = tasks_data['tasks']
print(f"\n✅ Total tasks loaded: {len(tasks)}\n")

# Group by worksheet
from collections import defaultdict
by_worksheet = defaultdict(list)
for task in tasks:
    by_worksheet[task.get('worksheet', 'Unknown')].append(task)

for ws_name, ws_tasks in by_worksheet.items():
    print(f"📋 {ws_name}: {len(ws_tasks)} tasks")

print(f"\n📊 Sample tasks:")
for task in tasks[:5]:
    print(f"  {task['id']} - {task['description']} ({task.get('worksheet', 'N/A')})")
