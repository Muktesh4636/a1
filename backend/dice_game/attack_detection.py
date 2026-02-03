"""
Aggressive attack detection and automatic IP blocking
Detects hacking attempts and immediately blocks attacking IPs
"""
from django.core.cache import cache
from django.http import HttpResponseForbidden
import os
import subprocess
import time


class AttackDetector:
    """Detect and block hacking attempts aggressively"""
    
    # Attack patterns to detect
    SQL_INJECTION_PATTERNS = [
        'union select', 'union all', 'select *', 'drop table',
        'delete from', 'insert into', 'update set', 'exec(',
        'xp_cmdshell', 'or 1=1', 'or 1=1--', "' or '1'='1",
        'admin\'--', 'admin\'/*', '1\' or \'1\'=\'1',
    ]
    
    XSS_PATTERNS = [
        '<script>', '</script>', 'javascript:', 'onerror=',
        'onload=', 'onclick=', '<iframe', '<img src=x',
        'alert(', 'eval(', 'document.cookie',
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        '../', '..\\', '....//', '....\\\\',
        '%2e%2e%2f', '%2e%2e%5c',
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        '; ls', '; cat', '; rm', '; wget', '; curl',
        '| ls', '| cat', '| rm', '| wget', '| curl',
        '`ls`', '`cat`', '$(ls)', '$(cat)',
    ]
    
    ADMIN_SCAN_PATTERNS = [
        '/wp-admin', '/phpmyadmin', '/admin.php',
        '/administrator', '/.env', '/config.php',
        '/wp-config.php', '/.git', '/.svn',
    ]
    
    @staticmethod
    def detect_attack(request):
        """Detect if request is an attack attempt"""
        attack_detected = False
        attack_type = None
        
        # Check request path
        path = request.path.lower()
        for pattern in AttackDetector.ADMIN_SCAN_PATTERNS:
            if pattern in path:
                attack_detected = True
                attack_type = 'admin_scan'
                break
        
        # Check request body for POST requests
        if request.method == 'POST':
            try:
                body_str = str(request.body).lower()
                
                # SQL Injection
                for pattern in AttackDetector.SQL_INJECTION_PATTERNS:
                    if pattern in body_str:
                        attack_detected = True
                        attack_type = 'sql_injection'
                        break
                
                # XSS
                if not attack_detected:
                    for pattern in AttackDetector.XSS_PATTERNS:
                        if pattern in body_str:
                            attack_detected = True
                            attack_type = 'xss'
                            break
                
                # Command Injection
                if not attack_detected:
                    for pattern in AttackDetector.COMMAND_INJECTION_PATTERNS:
                        if pattern in body_str:
                            attack_detected = True
                            attack_type = 'command_injection'
                            break
            except:
                pass
        
        # Check path traversal
        if not attack_detected:
            for pattern in AttackDetector.PATH_TRAVERSAL_PATTERNS:
                if pattern in path:
                    attack_detected = True
                    attack_type = 'path_traversal'
                    break
        
        return attack_detected, attack_type
    
    @staticmethod
    def block_ip_permanently(ip):
        """Permanently block an IP address using multiple methods"""
        try:
            # Method 1: Add to application cache (permanent until cleared)
            cache.set(f'blocked_ip_{ip}', True, 31536000)  # 1 year
            
            # Method 2: Block with UFW firewall
            try:
                subprocess.run(
                    ['ufw', 'deny', 'from', ip],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                )
            except:
                pass
            
            # Method 3: Block with iptables
            try:
                subprocess.run(
                    ['iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                )
            except:
                pass
            
            # Method 4: Add to Fail2Ban
            try:
                subprocess.run(
                    ['fail2ban-client', 'set', 'sshd', 'banip', ip],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                )
            except:
                pass
            
            # Log the attack
            AttackDetector.log_attack(ip, 'permanent_block')
            
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def log_attack(ip, attack_type):
        """Log attack attempt to file"""
        try:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, 'attacks.log')
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            
            with open(log_file, 'a') as f:
                f.write(f"{timestamp} | IP: {ip} | Type: {attack_type}\n")
        except:
            pass
    
    @staticmethod
    def get_blocked_ips():
        """Get list of all blocked IPs"""
        blocked = []
        # Check cache for blocked IPs
        # This is a simplified version - in production, you'd query all keys
        return blocked
