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
        """Detect if request is an attack attempt - Enhanced for API protection"""
        attack_detected = False
        attack_type = None
        
        # Check request path
        path = request.path.lower()
        is_api_endpoint = path.startswith('/api/')
        
        # API-specific attack patterns
        API_ABUSE_PATTERNS = [
            '/api/admin', '/api/user', '/api/auth', '/api/token',
            '/api/v1/admin', '/api/v2/admin', '/api/rest/admin',
        ]
        
        # Check for admin API scanning
        if is_api_endpoint:
            for pattern in API_ABUSE_PATTERNS:
                if pattern in path:
                    attack_detected = True
                    attack_type = 'api_admin_scan'
                    break
        
        # Check request path for admin scans
        if not attack_detected:
            for pattern in AttackDetector.ADMIN_SCAN_PATTERNS:
                if pattern in path:
                    attack_detected = True
                    attack_type = 'admin_scan'
                    break
        
        # Check request body for POST/PUT/PATCH requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body_str = str(request.body).lower()
                
                # SQL Injection
                for pattern in AttackDetector.SQL_INJECTION_PATTERNS:
                    if pattern in body_str:
                        attack_detected = True
                        attack_type = 'sql_injection' + ('_api' if is_api_endpoint else '')
                        break
                
                # XSS
                if not attack_detected:
                    for pattern in AttackDetector.XSS_PATTERNS:
                        if pattern in body_str:
                            attack_detected = True
                            attack_type = 'xss' + ('_api' if is_api_endpoint else '')
                            break
                
                # Command Injection
                if not attack_detected:
                    for pattern in AttackDetector.COMMAND_INJECTION_PATTERNS:
                        if pattern in body_str:
                            attack_detected = True
                            attack_type = 'command_injection' + ('_api' if is_api_endpoint else '')
                            break
                
                # API-specific: Check for JWT token manipulation
                if is_api_endpoint and not attack_detected:
                    jwt_abuse_patterns = [
                        'none', 'null', 'undefined', 'admin', 'true',
                        '{"alg":"none"}', '{"alg":"null"}',
                    ]
                    for pattern in jwt_abuse_patterns:
                        if pattern in body_str:
                            attack_detected = True
                            attack_type = 'jwt_manipulation'
                            break
                
                # API-specific: Check for excessive payload size (potential DoS)
                if is_api_endpoint and len(request.body) > 1000000:  # 1MB limit
                    attack_detected = True
                    attack_type = 'api_payload_dos'
            except:
                pass
        
        # Check query parameters for GET requests
        if request.method == 'GET':
            try:
                query_str = str(request.GET).lower()
                for pattern in AttackDetector.SQL_INJECTION_PATTERNS:
                    if pattern in query_str:
                        attack_detected = True
                        attack_type = 'sql_injection_query' + ('_api' if is_api_endpoint else '')
                        break
            except:
                pass
        
        # Check path traversal
        if not attack_detected:
            for pattern in AttackDetector.PATH_TRAVERSAL_PATTERNS:
                if pattern in path:
                    attack_detected = True
                    attack_type = 'path_traversal' + ('_api' if is_api_endpoint else '')
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
            
            # Log the attack (request=None for permanent blocks from other sources)
            AttackDetector.log_attack(ip, 'permanent_block', request=None)
            
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def log_attack(ip, attack_type, request=None):
        """Log attack attempt to file with full details - Enhanced for API attacks and VPN tracking"""
        try:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, 'attacks.log')
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Enhanced logging with request details
            endpoint = request.path if request else 'unknown'
            method = request.method if request else 'unknown'
            is_api = endpoint.startswith('/api/') if request else False
            
            # Get fingerprint if available (VPN-resistant tracking)
            fingerprint = getattr(request, '_fingerprint', None) if request else None
            fingerprint_str = f" | Fingerprint: {fingerprint[:16]}..." if fingerprint else ""
            
            # Get User-Agent for device tracking
            user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')[:50] if request else 'unknown'
            
            # Log with IP address, attack type, endpoint, fingerprint, and timestamp
            log_entry = f"{timestamp} | IP: {ip} | Type: {attack_type} | Endpoint: {endpoint} | Method: {method} | API: {is_api}{fingerprint_str} | User-Agent: {user_agent} | Status: BLOCKED\n"
            
            with open(log_file, 'a') as f:
                f.write(log_entry)
            
            # Also log to blocked IPs file
            blocked_file = os.path.join(log_dir, 'blocked_ips.log')
            with open(blocked_file, 'a') as f:
                f.write(f"{timestamp} | IP: {ip} | Reason: {attack_type} | Endpoint: {endpoint}{fingerprint_str}\n")
            
            # API-specific log file
            if is_api:
                api_log_file = os.path.join(log_dir, 'api_attacks.log')
                with open(api_log_file, 'a') as f:
                    f.write(f"{timestamp} | IP: {ip} | Type: {attack_type} | Endpoint: {endpoint} | Method: {method}{fingerprint_str} | BLOCKED\n")
            
            # VPN-resistant fingerprint log
            if fingerprint:
                fingerprint_log_file = os.path.join(log_dir, 'fingerprint_attacks.log')
                with open(fingerprint_log_file, 'a') as f:
                    f.write(f"{timestamp} | Fingerprint: {fingerprint} | IP: {ip} | Type: {attack_type} | Endpoint: {endpoint} | BLOCKED\n")
        except:
            pass
    
    @staticmethod
    def get_blocked_ips():
        """Get list of all blocked IPs"""
        blocked = []
        # Check cache for blocked IPs
        # This is a simplified version - in production, you'd query all keys
        return blocked
