#!/usr/bin/env python3
"""
Script to remove duplicate/old CSS rules from admin pages
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ADMIN_TEMPLATES_DIR = BASE_DIR / "backend" / "game" / "templates" / "admin"

FILES_TO_CLEAN = [
    "all_bets.html",
    "deposit_requests.html",
    "players.html",
    "game_settings.html",
    "admin_management.html",
    "wallets.html",
    "user_details.html",
    "transactions.html",
    "round_details.html",
]

def remove_old_menu_css(content):
    """Remove old sidebar menu CSS that conflicts with new styles"""
    # Remove old menu CSS patterns
    patterns_to_remove = [
        r'\.sidebar-menu \{\s*list-style: none;\s*padding: 12px 0;\s*\}\s*\.sidebar-menu li \{ margin: 0; \}',
        r'\.sidebar-menu a \{\s*display: flex;\s*align-items: center;\s*padding: 12px 20px;\s*color: #4a5568;\s*text-decoration: none;\s*transition: all 0\.2s;\s*font-size: 14px;\s*font-weight: 500;\s*\}',
        r'\.sidebar-menu a:hover \{\s*background: #f7fafc;\s*color: #667eea;\s*\}',
        r'\.sidebar-menu a\.active \{\s*background: #edf2f7;\s*color: #667eea;\s*border-left: 3px solid #667eea;\s*font-weight: 600;\s*\}',
    ]
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.MULTILINE)
    
    return content

def fix_sidebar_background(content):
    """Ensure sidebar has dark teal background"""
    # Fix sidebar background
    content = re.sub(
        r'(\.sidebar \{[^}]*?)background:[^;]+;',
        r'\1background: #004D4D;',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    return content

def remove_duplicate_css(content):
    """Remove duplicate CSS rules"""
    # Find and remove duplicate .sidebar-menu rules (keep the first one with new styles)
    lines = content.split('\n')
    new_lines = []
    seen_menu_css = False
    skip_old_menu = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Detect start of old menu CSS block
        if '.sidebar-menu {' in line and 'padding: 0;' not in content[max(0, i-5):i+5]:
            # Check if this is the old CSS (has padding: 12px)
            if i + 1 < len(lines) and 'padding: 12px' in lines[i + 1]:
                # Skip old menu CSS block
                skip_old_menu = True
                i += 1
                continue
        
        # Detect end of old menu CSS block
        if skip_old_menu:
            if '.menu-icon {' in line or '.menu-badge {' in line or (i + 1 < len(lines) and '.main-content {' in lines[i + 1]):
                skip_old_menu = False
            else:
                i += 1
                continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)

def clean_file(file_path):
    """Clean duplicate CSS from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Remove old menu CSS
        content = remove_old_menu_css(content)
        
        # Fix sidebar background
        content = fix_sidebar_background(content)
        
        # Remove duplicate CSS more carefully
        # Remove old sidebar-menu CSS that comes after new CSS
        old_menu_pattern = r'(\.menu-badge \{[^}]+\})\s+(\.sidebar-menu \{\s*list-style: none;\s*padding: 12px 0;\s*\}\s*\.sidebar-menu li \{ margin: 0; \}\s*\.sidebar-menu a \{[^}]+\}\s*\.sidebar-menu a:hover \{[^}]+\}\s*\.sidebar-menu a\.active \{[^}]+\}\s*\.sidebar-menu \.menu-icon \{[^}]+\})'
        content = re.sub(old_menu_pattern, r'\1', content, flags=re.MULTILINE | re.DOTALL)
        
        # Ensure sidebar background is correct
        if '.sidebar {' in content:
            content = re.sub(
                r'(\.sidebar \{[^}]*?)(background:[^;]+;)',
                r'\1background: #004D4D;',
                content,
                flags=re.MULTILINE | re.DOTALL
            )
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Cleaned: {file_path.name}")
            return True
        else:
            print(f"⏭️  No cleanup needed: {file_path.name}")
            return False
    except Exception as e:
        print(f"❌ Error cleaning {file_path.name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔄 Cleaning duplicate CSS from admin pages...\n")
    
    updated = 0
    for filename in FILES_TO_CLEAN:
        file_path = ADMIN_TEMPLATES_DIR / filename
        if file_path.exists():
            if clean_file(file_path):
                updated += 1
        else:
            print(f"⚠️  Not found: {filename}")
    
    print(f"\n✅ Cleaned {updated} files")

if __name__ == "__main__":
    main()

