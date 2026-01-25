#!/usr/bin/env python3
"""
Script to update all admin pages with the new UI design
"""

import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent
ADMIN_TEMPLATES_DIR = BASE_DIR / "backend" / "game" / "templates" / "admin"

# Files to update (excluding login.html and _sidebar_menu.html which are already updated)
FILES_TO_UPDATE = [
    "admin_management.html",
    "all_bets.html",
    "deposit_requests.html",
    "game_settings.html",
    "players.html",
    "recent_rounds.html",
    "round_details.html",
    "transactions.html",
    "user_details.html",
    "wallets.html",
    "edit_admin.html",
    "create_admin.html",
]

# Sidebar CSS replacement
OLD_SIDEBAR_CSS = r"""\.sidebar \{
            width: 260px;
            background: #ffffff;
            min-height: 100vh;
            box-shadow: 0 0 20px rgba\(0,0,0,0\.05\);
            position: fixed;
            left: 0;
            top: 0;
            overflow-y: auto;
            z-index: 1000;
            border-right: 1px solid #e2e8f0;
        \}
        
        \.sidebar-header \{
            padding: 24px 20px;
            border-bottom: 1px solid #e2e8f0;
            background: linear-gradient\(135deg, #667eea 0%, #764ba2 100%\);
        \}
        
        \.sidebar-header h2 \{
            color: white;
            font-size: 20px;
            font-weight: 600;
            margin: 0;
        \}
        
        \.sidebar-menu \{
            list-style: none;
            padding: 12px 0;
        \}
        
        \.sidebar-menu li \{
            margin: 0;
        \}
        
        \.sidebar-menu a \{
            display: flex;
            align-items: center;
            padding: 12px 20px;
            color: #4a5568;
            text-decoration: none;
            transition: all 0\.2s;
            font-size: 14px;
            font-weight: 500;
        \}
        
        \.sidebar-menu a:hover \{
            background: #f7fafc;
            color: #667eea;
        \}
        
        \.sidebar-menu a\.active \{
            background: #edf2f7;
            color: #667eea;
            border-left: 3px solid #667eea;
            font-weight: 600;
        \}
        
        \.sidebar-menu \.menu-icon \{
            margin-right: 12px;
            font-size: 18px;
            width: 20px;
            text-align: center;
        \}
        
        \.main-content \{
            margin-left: 260px;
            flex: 1;
            padding: 32px;
            min-height: 100vh;
            width: calc\(100% - 260px\);
        \}"""

NEW_SIDEBAR_CSS = """        .sidebar {
            width: 260px;
            background: #004D4D;
            min-height: 100vh;
            position: fixed;
            left: 0;
            top: 0;
            overflow-y: auto;
            z-index: 1000;
        }
        
        .sidebar-header {
            padding: 24px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .sidebar-header .logo {
            display: flex;
            align-items: center;
            gap: 8px;
            color: white;
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .sidebar-header .logo-icon {
            font-size: 24px;
        }
        
        .sidebar-header .subtitle {
            color: rgba(255, 255, 255, 0.7);
            font-size: 13px;
            font-weight: 400;
            margin-top: 4px;
        }
        
        .sidebar-menu-wrapper {
            padding: 12px 0;
        }
        
        .menu-section {
            margin-bottom: 24px;
        }
        
        .menu-section-title {
            color: rgba(255, 255, 255, 0.5);
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 8px 20px;
            margin-bottom: 4px;
        }
        
        .sidebar-menu {
            list-style: none;
            padding: 0;
        }
        
        .sidebar-menu li {
            margin: 0;
        }
        
        .sidebar-menu a {
            display: flex;
            align-items: center;
            padding: 12px 20px;
            color: rgba(255, 255, 255, 0.8);
            text-decoration: none;
            transition: all 0.2s;
            font-size: 14px;
            font-weight: 500;
            position: relative;
        }
        
        .sidebar-menu a:hover {
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }
        
        .sidebar-menu a.active {
            background: rgba(255, 255, 255, 0.15);
            color: white;
            font-weight: 600;
        }
        
        .sidebar-menu a.active::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3px;
            background: #00CED1;
        }
        
        .sidebar-menu .menu-icon {
            margin-right: 12px;
            font-size: 18px;
            width: 20px;
            text-align: center;
        }
        
        .menu-badge {
            margin-left: auto;
            font-size: 11px;
            color: rgba(255, 255, 255, 0.6);
            font-weight: 400;
        }
        
        .main-content {
            margin-left: 260px;
            flex: 1;
            padding: 32px;
            min-height: 100vh;
            width: calc(100% - 260px);
            background: #ffffff;
        }"""

# Sidebar HTML replacement
OLD_SIDEBAR_HTML = r'<div class="sidebar-header">\s*<h2>🎲 Admin Panel</h2>\s*</div>'
NEW_SIDEBAR_HTML = """        <div class="sidebar-header">
            <div class="logo">
                <span class="logo-icon">→</span>
                <span>Gundu ata</span>
            </div>
            <div class="subtitle">Game control</div>
        </div>"""

# Body background replacement
OLD_BODY_BG = r'background: #f5f7fa;'
NEW_BODY_BG = 'background: #ffffff;'

def update_file(file_path):
    """Update a single file with new UI styles"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace sidebar CSS
        content = re.sub(OLD_SIDEBAR_CSS, NEW_SIDEBAR_CSS, content, flags=re.MULTILINE)
        
        # Replace sidebar header HTML
        content = re.sub(OLD_SIDEBAR_HTML, NEW_SIDEBAR_HTML, content, flags=re.MULTILINE)
        
        # Replace body background
        content = content.replace(OLD_BODY_BG, NEW_BODY_BG)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {file_path.name}")
            return True
        else:
            print(f"⏭️  No changes needed: {file_path.name}")
            return False
    except Exception as e:
        print(f"❌ Error updating {file_path.name}: {e}")
        return False

def main():
    """Main function to update all admin pages"""
    print("🔄 Updating admin pages with new UI design...\n")
    
    updated_count = 0
    for filename in FILES_TO_UPDATE:
        file_path = ADMIN_TEMPLATES_DIR / filename
        if file_path.exists():
            if update_file(file_path):
                updated_count += 1
        else:
            print(f"⚠️  File not found: {filename}")
    
    print(f"\n✅ Updated {updated_count} files")

if __name__ == "__main__":
    main()

