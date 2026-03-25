"""
Security Module for ET AI Concierge
Handles authentication, authorization, data encryption, and security monitoring
"""

from __future__ import annotations

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import bcrypt
from cryptography.fernet import Fernet
import re

class UserRole(Enum):
    """User roles for authorization"""
    GUEST = "guest"
    USER = "user"
    PREMIUM_USER = "premium_user"
    ADVISOR = "advisor"
    ADMIN = "admin"

class SecurityLevel(Enum):
    """Security levels for different operations"""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    VERIFIED = "verified"
    PREMIUM = "premium"
    ADMIN = "admin"

@dataclass
class SecurityContext:
    """Security context for a user session"""
    user_id: str
    role: UserRole
    session_id: str
    ip_address: str
    device_fingerprint: str
    authenticated_at: datetime
    expires_at: datetime
    permissions: List[str]

class AuthenticationManager:
    """Handles user authentication and session management"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.active_sessions: Dict[str, SecurityContext] = {}
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_session_token(self, user_id: str, role: UserRole) -> str:
        """Generate JWT session token"""
        payload = {
            'user_id': user_id,
            'role': role.value,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=24),
            'session_id': secrets.token_urlsafe(32)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def validate_session_token(self, token: str) -> Optional[Dict[str, Any]]:\n        \"\"\"Validate JWT session token\"\"\"\n        try:\n            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])\n            return payload\n        except jwt.ExpiredSignatureError:\n            return None\n        except jwt.InvalidTokenError:\n            return None\n    \n    def create_session(self, user_id: str, role: UserRole, \n                      ip_address: str, device_info: str) -> SecurityContext:\n        \"\"\"Create new user session\"\"\"\n        session_id = secrets.token_urlsafe(32)\n        device_fingerprint = self._generate_device_fingerprint(device_info)\n        \n        context = SecurityContext(\n            user_id=user_id,\n            role=role,\n            session_id=session_id,\n            ip_address=ip_address,\n            device_fingerprint=device_fingerprint,\n            authenticated_at=datetime.utcnow(),\n            expires_at=datetime.utcnow() + timedelta(hours=24),\n            permissions=self._get_role_permissions(role)\n        )\n        \n        self.active_sessions[session_id] = context\n        return context\n    \n    def _generate_device_fingerprint(self, device_info: str) -> str:\n        \"\"\"Generate device fingerprint for security\"\"\"\n        return hashlib.sha256(device_info.encode()).hexdigest()[:16]\n    \n    def _get_role_permissions(self, role: UserRole) -> List[str]:\n        \"\"\"Get permissions for user role\"\"\"\n        permissions_map = {\n            UserRole.GUEST: ['read_public_content'],\n            UserRole.USER: ['read_public_content', 'read_basic_recommendations', 'track_journey'],\n            UserRole.PREMIUM_USER: ['read_public_content', 'read_basic_recommendations', \n                                  'read_premium_content', 'advanced_analytics', 'track_journey'],\n            UserRole.ADVISOR: ['read_public_content', 'read_basic_recommendations', \n                             'read_premium_content', 'create_recommendations', 'view_user_data'],\n            UserRole.ADMIN: ['*']  # All permissions\n        }\n        return permissions_map.get(role, [])\n    \n    def check_rate_limit(self, ip_address: str, max_attempts: int = 5, \n                        window_minutes: int = 15) -> bool:\n        \"\"\"Check if IP is rate limited\"\"\"\n        now = datetime.utcnow()\n        \n        # Check if IP is blocked\n        if ip_address in self.blocked_ips:\n            if now < self.blocked_ips[ip_address]:\n                return False\n            else:\n                del self.blocked_ips[ip_address]\n        \n        # Check failed attempts\n        if ip_address not in self.failed_attempts:\n            self.failed_attempts[ip_address] = []\n        \n        # Clean old attempts\n        cutoff_time = now - timedelta(minutes=window_minutes)\n        self.failed_attempts[ip_address] = [\n            attempt for attempt in self.failed_attempts[ip_address]\n            if attempt > cutoff_time\n        ]\n        \n        # Check if limit exceeded\n        if len(self.failed_attempts[ip_address]) >= max_attempts:\n            # Block IP for 1 hour\n            self.blocked_ips[ip_address] = now + timedelta(hours=1)\n            return False\n        \n        return True\n    \n    def record_failed_attempt(self, ip_address: str):\n        \"\"\"Record failed authentication attempt\"\"\"\n        if ip_address not in self.failed_attempts:\n            self.failed_attempts[ip_address] = []\n        self.failed_attempts[ip_address].append(datetime.utcnow())\n\nclass DataEncryption:\n    \"\"\"Handles data encryption and decryption\"\"\"\n    \n    def __init__(self, encryption_key: Optional[str] = None):\n        if encryption_key:\n            self.key = encryption_key.encode()\n        else:\n            self.key = Fernet.generate_key()\n        self.cipher = Fernet(self.key)\n    \n    def encrypt_sensitive_data(self, data: str) -> str:\n        \"\"\"Encrypt sensitive data\"\"\"\n        encrypted = self.cipher.encrypt(data.encode())\n        return encrypted.decode()\n    \n    def decrypt_sensitive_data(self, encrypted_data: str) -> str:\n        \"\"\"Decrypt sensitive data\"\"\"\n        decrypted = self.cipher.decrypt(encrypted_data.encode())\n        return decrypted.decode()\n    \n    def hash_pii(self, pii_data: str) -> str:\n        \"\"\"Hash PII data for anonymization\"\"\"\n        return hashlib.sha256(pii_data.encode()).hexdigest()\n\nclass InputValidator:\n    \"\"\"Validates and sanitizes user inputs\"\"\"\n    \n    @staticmethod\n    def validate_email(email: str) -> bool:\n        \"\"\"Validate email format\"\"\"\n        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'\n        return re.match(pattern, email) is not None\n    \n    @staticmethod\n    def validate_phone(phone: str) -> bool:\n        \"\"\"Validate Indian phone number\"\"\"\n        pattern = r'^[+]?[91]?[6-9]\\d{9}$'\n        return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None\n    \n    @staticmethod\n    def validate_pan(pan: str) -> bool:\n        \"\"\"Validate PAN number format\"\"\"\n        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'\n        return re.match(pattern, pan.upper()) is not None\n    \n    @staticmethod\n    def sanitize_input(user_input: str) -> str:\n        \"\"\"Sanitize user input to prevent injection attacks\"\"\"\n        # Remove potentially dangerous characters\n        dangerous_chars = ['<', '>', '\"', \"'\", '&', ';', '(', ')', '|', '`']\n        sanitized = user_input\n        for char in dangerous_chars:\n            sanitized = sanitized.replace(char, '')\n        return sanitized.strip()\n    \n    @staticmethod\n    def validate_investment_amount(amount: str) -> Tuple[bool, Optional[float]]:\n        \"\"\"Validate investment amount\"\"\"\n        try:\n            amount_float = float(amount.replace(',', ''))\n            if amount_float < 0:\n                return False, None\n            if amount_float > 10000000:  # 1 crore limit\n                return False, None\n            return True, amount_float\n        except ValueError:\n            return False, None\n\nclass SecurityMonitor:\n    \"\"\"Monitors security events and anomalies\"\"\"\n    \n    def __init__(self):\n        self.security_events: List[Dict[str, Any]] = []\n        self.anomaly_thresholds = {\n            'max_requests_per_minute': 100,\n            'max_failed_logins': 5,\n            'suspicious_locations': True,\n            'unusual_access_patterns': True\n        }\n    \n    def log_security_event(self, event_type: str, user_id: str, \n                          ip_address: str, details: Dict[str, Any]):\n        \"\"\"Log security event\"\"\"\n        event = {\n            'timestamp': datetime.utcnow().isoformat(),\n            'event_type': event_type,\n            'user_id': user_id,\n            'ip_address': ip_address,\n            'details': details,\n            'severity': self._calculate_severity(event_type, details)\n        }\n        self.security_events.append(event)\n        \n        # Check for immediate threats\n        if event['severity'] == 'HIGH':\n            self._handle_high_severity_event(event)\n    \n    def _calculate_severity(self, event_type: str, details: Dict[str, Any]) -> str:\n        \"\"\"Calculate event severity\"\"\"\n        high_severity_events = [\n            'multiple_failed_logins',\n            'suspicious_location_access',\n            'potential_injection_attack',\n            'unauthorized_access_attempt'\n        ]\n        \n        if event_type in high_severity_events:\n            return 'HIGH'\n        elif event_type.startswith('failed_'):\n            return 'MEDIUM'\n        else:\n            return 'LOW'\n    \n    def _handle_high_severity_event(self, event: Dict[str, Any]):\n        \"\"\"Handle high severity security events\"\"\"\n        # In production, this would trigger alerts, notifications, etc.\n        print(f\"HIGH SEVERITY SECURITY EVENT: {event['event_type']}\")\n        print(f\"User: {event['user_id']}, IP: {event['ip_address']}\")\n        print(f\"Details: {event['details']}\")\n    \n    def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:\n        \"\"\"Get security summary for the last N hours\"\"\"\n        cutoff_time = datetime.utcnow() - timedelta(hours=hours)\n        \n        recent_events = [\n            event for event in self.security_events\n            if datetime.fromisoformat(event['timestamp']) > cutoff_time\n        ]\n        \n        event_counts = {}\n        severity_counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0}\n        \n        for event in recent_events:\n            event_type = event['event_type']\n            event_counts[event_type] = event_counts.get(event_type, 0) + 1\n            severity_counts[event['severity']] += 1\n        \n        return {\n            'time_period_hours': hours,\n            'total_events': len(recent_events),\n            'event_breakdown': event_counts,\n            'severity_breakdown': severity_counts,\n            'high_risk_events': [\n                event for event in recent_events\n                if event['severity'] == 'HIGH'\n            ]\n        }\n\nclass AuthorizationManager:\n    \"\"\"Handles user authorization and permissions\"\"\"\n    \n    def __init__(self):\n        self.resource_permissions = self._define_resource_permissions()\n    \n    def _define_resource_permissions(self) -> Dict[str, Dict[UserRole, List[str]]]:\n        \"\"\"Define permissions for different resources\"\"\"\n        return {\n            'recommendations': {\n                UserRole.GUEST: ['read_basic'],\n                UserRole.USER: ['read_basic', 'read_personalized'],\n                UserRole.PREMIUM_USER: ['read_basic', 'read_personalized', 'read_premium'],\n                UserRole.ADVISOR: ['read_basic', 'read_personalized', 'read_premium', 'create'],\n                UserRole.ADMIN: ['*']\n            },\n            'user_data': {\n                UserRole.GUEST: [],\n                UserRole.USER: ['read_own'],\n                UserRole.PREMIUM_USER: ['read_own', 'export_own'],\n                UserRole.ADVISOR: ['read_assigned_users'],\n                UserRole.ADMIN: ['read_all', 'modify_all']\n            },\n            'analytics': {\n                UserRole.GUEST: [],\n                UserRole.USER: ['view_own_journey'],\n                UserRole.PREMIUM_USER: ['view_own_journey', 'detailed_analytics'],\n                UserRole.ADVISOR: ['view_client_analytics'],\n                UserRole.ADMIN: ['view_all_analytics']\n            }\n        }\n    \n    def check_permission(self, user_role: UserRole, resource: str, action: str) -> bool:\n        \"\"\"Check if user has permission for action on resource\"\"\"\n        if resource not in self.resource_permissions:\n            return False\n        \n        role_permissions = self.resource_permissions[resource].get(user_role, [])\n        \n        # Admin has all permissions\n        if '*' in role_permissions:\n            return True\n        \n        return action in role_permissions\n\n# Security utilities\ndef generate_secure_token(length: int = 32) -> str:\n    \"\"\"Generate cryptographically secure token\"\"\"\n    return secrets.token_urlsafe(length)\n\ndef mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:\n    \"\"\"Mask sensitive data for display\"\"\"\n    if len(data) <= visible_chars:\n        return mask_char * len(data)\n    \n    return data[:visible_chars] + mask_char * (len(data) - visible_chars)\n\n# Example usage and testing\nif __name__ == \"__main__\":\n    # Test authentication\n    auth_manager = AuthenticationManager(\"your-secret-key\")\n    \n    # Test password hashing\n    password = \"secure_password_123\"\n    hashed = auth_manager.hash_password(password)\n    print(f\"Password verified: {auth_manager.verify_password(password, hashed)}\")\n    \n    # Test input validation\n    print(f\"Valid email: {InputValidator.validate_email('user@example.com')}\")\n    print(f\"Valid PAN: {InputValidator.validate_pan('ABCDE1234F')}\")\n    \n    # Test data masking\n    print(f\"Masked PAN: {mask_sensitive_data('ABCDE1234F', visible_chars=2)}\")\n    \n    # Test authorization\n    auth_manager_perm = AuthorizationManager()\n    print(f\"User can read recommendations: {auth_manager_perm.check_permission(UserRole.USER, 'recommendations', 'read_basic')}\")