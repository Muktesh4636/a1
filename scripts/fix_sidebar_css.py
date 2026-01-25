#!/usr/bin/env python3
"""
Script to fix sidebar CSS in all admin pages
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ADMIN_TEMPLATES_DIR = BASE_DIR / "backend" / "game" / "templates" / "admin"

FILES_TO_FIX = [
    "all_bets.html",
    "deposit_requests.html",
    "players.html",
    "game_settings.html",
    "admin_management.html",
    "wallets.html",
    "user_details.html",
    "transactions.html",
    "round_details.html",
    "edit_admin.html",
    "create_admin.html",
]

# Old sidebar CSS patterns to replace
OLD_SIDEBAR_CSS_PATTERNS = [
    (r'\.sidebar \{\s*width: 260px;\s*background: #ffffff;', 
     '.sidebar {\n            width: 260px;\n            background: #004D4D;'),
    (r'\.sidebar \{\s*width: 260px;\s*background: #f5f7fa;', 
     '.sidebar {\n            width: 260px;\n            background: #004D4D;'),
    (r'border-right: 1px solid #e2e8f0;', ''),
    (r'box-shadow: 0 0 20px rgba\(0,0,0,0\.05\);', ''),
]

# Old sidebar-header CSS to replace
OLD_HEADER_CSS = r'\.sidebar-header \{\s*padding: 24px 20px;\s*border-bottom: 1px solid #e2e8f0;\s*background: linear-gradient\(135deg, #667eea 0%, #764ba2 100%\);\s*\}'
NEW_HEADER_CSS = """        .sidebar-header {
            padding: 24px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }"""

OLD_HEADER_H2_CSS = r'\.sidebar-header h2 \{\s*color: white;\s*font-size: 20px;\s*font-weight: 600;\s*margin: 0;\s*\}'
NEW_LOGO_CSS = """        .sidebar-header .logo {
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
        }"""

OLD_MENU_CSS = r'\.sidebar-menu \{\s*list-style: none;\s*padding: 12px 0;\s*\}'
OLD_MENU_LI_CSS = r'\.sidebar-menu li \{\s*margin: 0;\s*\}'
OLD_MENU_A_CSS = r'\.sidebar-menu a \{\s*display: flex;\s*align-items: center;\s*padding: 12px 20px;\s*color: #4a5568;\s*text-decoration: none;\s*transition: all 0\.2s;\s*font-size: 14px;\s*font-weight: 500;\s*\}'
OLD_MENU_A_HOVER = r'\.sidebar-menu a:hover \{\s*background: #f7fafc;\s*color: #667eea;\s*\}'
OLD_MENU_A_ACTIVE = r'\.sidebar-menu a\.active \{\s*background: #edf2f7;\s*color: #667eea;\s*border-left: 3px solid #667eea;\s*font-weight: 600;\s*\}'
OLD_MENU_ICON = r'\.sidebar-menu \.menu-icon \{\s*margin-right: 12px;\s*font-size: 18px;\s*width: 20px;\s*text-align: center;\s*\}'

def fix_file(file_path):
    """Fix sidebar CSS in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Fix sidebar background
        content = re.sub(r'\.sidebar \{[^}]*background:[^;]+;', 
                        lambda m: m.group(0).replace('#ffffff', '#004D4D').replace('#f5f7fa', '#004D4D'), 
                        content)
        
        # Remove old border and box-shadow from sidebar
        content = re.sub(r'border-right: 1px solid #e2e8f0;\s*', '', content)
        content = re.sub(r'box-shadow: 0 0 20px rgba\(0,0,0,0\.05\);\s*', '', content)
        
        # Replace old sidebar-header CSS
        content = re.sub(OLD_HEADER_CSS, NEW_HEADER_CSS, content, flags=re.MULTILINE | re.DOTALL)
        
        # Replace old h2 CSS with new logo CSS
        if '.sidebar-header h2 {' in content and '.sidebar-header .logo {' not in content:
            content = re.sub(OLD_HEADER_H2_CSS, NEW_LOGO_CSS, content, flags=re.MULTILINE | re.DOTALL)
        
        # Ensure main-content has white background
        if '.main-content {' in content and 'background: #ffffff' not in content:
            content = re.sub(r'(\.main-content \{[^}]*)(\})', 
                           r'\1\n            background: #ffffff;\2', 
                           content)
        
        # Fix body background
        content = re.sub(r'background: #f5f7fa;', 'background: #ffffff;', content)
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {file_path.name}")
            return True
        else:
            print(f"⏭️  No changes: {file_path.name}")
            return False
    except Exception as e:
        print(f"❌ Error fixing {file_path.name}: {e}")
        return False

def main():
    print("🔄 Fixing sidebar CSS in all admin pages...\n")
    
    updated = 0
    for filename in FILES_TO_FIX:
        file_path = ADMIN_TEMPLATES_DIR / filename
        if file_path.exists():
            if fix_file(file_path):
                updated += 1
        else:
            print(f"⚠️  Not found: {filename}")
    
    print(f"\n✅ Fixed {updated} files")

if __name__ == "__main__":
    main()

