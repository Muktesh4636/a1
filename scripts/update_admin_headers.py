#!/usr/bin/env python3
"""
Script to update header structure in all admin pages
"""

import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent
ADMIN_TEMPLATES_DIR = BASE_DIR / "backend" / "game" / "templates" / "admin"

# Files to update
FILES_TO_UPDATE = [
    "all_bets.html",
    "deposit_requests.html",
    "players.html",
    "recent_rounds.html",
    "round_details.html",
    "transactions.html",
    "user_details.html",
    "wallets.html",
    "admin_management.html",
    "game_settings.html",
    "edit_admin.html",
    "create_admin.html",
]

# Page titles mapping
PAGE_TITLES = {
    "all_bets.html": ("All Bets", "View all bets placed across all rounds"),
    "deposit_requests.html": ("Deposit Requests", "Manage pending deposit requests"),
    "players.html": ("Players", "View and manage all players"),
    "recent_rounds.html": ("Recent Rounds", "View recent game rounds and results"),
    "round_details.html": ("Round Details", "Detailed information about a game round"),
    "transactions.html": ("Transactions", "View all transaction history"),
    "user_details.html": ("User Details", "Detailed information about a user"),
    "wallets.html": ("Wallets", "View and manage user wallets"),
    "admin_management.html": ("Admin Management", "Manage admin users and permissions"),
    "game_settings.html": ("Game Settings", "Configure game timing and settings"),
    "edit_admin.html": ("Edit Admin", "Edit admin user details"),
    "create_admin.html": ("Create Admin", "Create a new admin user"),
}

def update_header(file_path, title, subtitle):
    """Update header structure in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern to match old header structure
        old_header_pattern = r'<div class="header">\s*<h1>[^<]*</h1>\s*(?:<a[^>]*>Django Admin</a>)?\s*</div>'
        
        # New header structure
        new_header = """            <div class="header">
                <div class="header-left">
                    <h1>""" + title + """</h1>
                    <p>""" + subtitle + """</p>
                </div>
                <div class="header-actions">
                    {% if is_super_admin %}
                    <a href="/admin/" target="_blank" class="action-btn">Django Admin</a>
                    {% endif %}
                </div>
            </div>"""
        
        # Try to replace
        content = re.sub(old_header_pattern, new_header, content, flags=re.MULTILINE | re.DOTALL)
        
        # Also update header CSS if needed
        if '.header {' in content and 'header-left' not in content:
            # Add header-left and header-actions styles
            header_css_addition = """
        .header-left h1 {
            color: #1a202c;
            font-size: 32px;
            font-weight: 700;
            margin: 0 0 4px 0;
        }
        
        .header-left p {
            color: #718096;
            font-size: 14px;
            margin: 0;
        }
        
        .header-actions {
            display: flex;
            gap: 12px;
            align-items: center;
        }
        
        .action-btn {
            padding: 10px 20px;
            background: #00CED1;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.2s;
            border: none;
            cursor: pointer;
        }
        
        .action-btn:hover {
            background: #00B8B8;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 206, 209, 0.3);
        }
        
        """
            
            # Insert after .header { ... }
            header_css_pattern = r'(\.header \{[^}]*\})'
            match = re.search(header_css_pattern, content)
            if match:
                # Find the closing brace and insert after it
                pos = match.end()
                content = content[:pos] + header_css_addition + content[pos:]
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated header: {file_path.name}")
            return True
        else:
            print(f"⏭️  No header changes needed: {file_path.name}")
            return False
    except Exception as e:
        print(f"❌ Error updating {file_path.name}: {e}")
        return False

def main():
    """Main function"""
    print("🔄 Updating header structures in admin pages...\n")
    
    updated_count = 0
    for filename in FILES_TO_UPDATE:
        file_path = ADMIN_TEMPLATES_DIR / filename
        if file_path.exists():
            title, subtitle = PAGE_TITLES.get(filename, (filename.replace('.html', '').replace('_', ' ').title(), ""))
            if update_header(file_path, title, subtitle):
                updated_count += 1
        else:
            print(f"⚠️  File not found: {filename}")
    
    print(f"\n✅ Updated {updated_count} files")

if __name__ == "__main__":
    main()

