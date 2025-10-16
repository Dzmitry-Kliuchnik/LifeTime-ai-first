---
description: 'Security best practices for Python FastAPI and Vue.js applications'
applyTo: '**/*.py, **/*.ts, **/*.vue, **/*.js'
---

# Security Guidelines

Comprehensive security practices for fullstack web applications with Python FastAPI backend and Vue.js frontend.

## General Security Philosophy

- **Security by Design** - Build security considerations into every aspect of development
- **Defense in Depth** - Implement multiple layers of security controls
- **Principle of Least Privilege** - Grant minimum necessary permissions
- **Input Validation Everywhere** - Never trust any external input
- **Fail Securely** - Ensure failures don't expose sensitive information
- **Security Awareness** - Stay informed about latest threats and vulnerabilities

## Input Validation and Sanitization

### Backend Input Validation (FastAPI/Python)

#### Pydantic Schema Validation
```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re

class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="Valid email address")
    age: Optional[int] = Field(None, ge=13, le=120, description="User age between 13-120")
    phone: Optional[str] = Field(None, regex=r'^\+?[\d\s\-\(\)]{10,15}$')
    
    @validator('name')
    def validate_name(cls, v):
        # Remove any HTML tags and excessive whitespace
        cleaned = re.sub(r'<[^>]*>', '', v).strip()
        if not cleaned:
            raise ValueError('Name cannot be empty or contain only HTML')
        return cleaned
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            # Remove all non-digit characters except +
            cleaned = re.sub(r'[^\d+]', '', v)
            if len(cleaned) < 10:
                raise ValueError('Phone number too short')
        return v

class Config:
    # Prevent extra fields from being accepted
    extra = 'forbid'
    # Enable validation on assignment
    validate_assignment = True
```

#### SQL Injection Prevention
```python
from sqlalchemy.orm import Session
from sqlalchemy import text

# ✅ CORRECT: Use SQLAlchemy ORM or parameterized queries
def get_user_by_email_secure(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# ✅ CORRECT: Parameterized raw SQL if needed
def get_users_by_status_secure(db: Session, status: str):
    result = db.execute(
        text("SELECT * FROM users WHERE status = :status"), 
        {"status": status}
    )
    return result.fetchall()

# ❌ DANGEROUS: String concatenation (vulnerable to SQL injection)
def get_user_by_email_vulnerable(db: Session, email: str):
    # NEVER DO THIS!
    query = f"SELECT * FROM users WHERE email = '{email}'"
    return db.execute(text(query)).fetchall()
```

### Frontend Input Validation (Vue.js/TypeScript)

#### Form Input Sanitization
```typescript
// utils/sanitize.ts
import DOMPurify from 'dompurify'

export class InputSanitizer {
  static sanitizeHtml(input: string): string {
    return DOMPurify.sanitize(input, { 
      ALLOWED_TAGS: [],
      ALLOWED_ATTR: []
    })
  }

  static sanitizeText(input: string): string {
    return input
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/javascript:/gi, '')
      .replace(/on\w+\s*=/gi, '')
      .trim()
  }

  static validateEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email) && email.length <= 254
  }

  static validateUrl(url: string): boolean {
    try {
      const parsedUrl = new URL(url)
      return ['http:', 'https:'].includes(parsedUrl.protocol)
    } catch {
      return false
    }
  }
}
```

#### Secure Form Component
```vue
<template>
  <form @submit.prevent="handleSubmit">
    <div class="form-group">
      <label for="user-input">User Input</label>
      <input
        id="user-input"
        v-model="sanitizedInput"
        type="text"
        :maxlength="maxLength"
        @input="sanitizeInput"
        @blur="validateInput"
      />
      <div v-if="errors.input" class="error">{{ errors.input }}</div>
    </div>
    
    <button type="submit" :disabled="!isValid">Submit</button>
  </form>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { InputSanitizer } from '@/utils/sanitize'

const rawInput = ref('')
const errors = ref({ input: '' })
const maxLength = 100

const sanitizedInput = computed({
  get: () => rawInput.value,
  set: (value: string) => {
    rawInput.value = InputSanitizer.sanitizeText(value)
  }
})

const isValid = computed(() => 
  rawInput.value.length > 0 && !errors.value.input
)

function sanitizeInput(event: Event) {
  const target = event.target as HTMLInputElement
  const sanitized = InputSanitizer.sanitizeText(target.value)
  if (sanitized !== target.value) {
    target.value = sanitized
    rawInput.value = sanitized
  }
}

function validateInput() {
  if (rawInput.value.length === 0) {
    errors.value.input = 'Input is required'
  } else if (rawInput.value.length > maxLength) {
    errors.value.input = `Input must be less than ${maxLength} characters`
  } else {
    errors.value.input = ''
  }
}
</script>
```

## Authentication and Authorization

### JWT Token Security (Backend)

#### Secure JWT Implementation
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import bcrypt

# Strong password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Use strong, randomly generated secret keys
SECRET_KEY = secrets.token_urlsafe(32)  # In production, load from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt with automatic salt generation."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        """Create JWT access token with expiration."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Verify and decode JWT token."""
        token = credentials.credentials
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")
            
            if user_id is None or token_type != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            return {"user_id": user_id, "payload": payload}
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

# Rate limiting for authentication attempts
from collections import defaultdict
from time import time

class RateLimiter:
    def __init__(self, max_attempts: int = 5, window_minutes: int = 15):
        self.max_attempts = max_attempts
        self.window_seconds = window_minutes * 60
        self.attempts = defaultdict(list)
    
    def is_allowed(self, key: str) -> bool:
        now = time()
        # Clean old attempts
        self.attempts[key] = [
            attempt_time for attempt_time in self.attempts[key]
            if now - attempt_time < self.window_seconds
        ]
        
        if len(self.attempts[key]) >= self.max_attempts:
            return False
        
        self.attempts[key].append(now)
        return True

rate_limiter = RateLimiter()

@app.post("/auth/login")
async def login(credentials: UserLoginRequest, request: Request):
    client_ip = request.client.host
    
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Proceed with authentication...
```

### Frontend Authentication (Vue.js)

#### Secure Token Storage and Management
```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginCredentials } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  
  // Secure cookie configuration
  const COOKIE_OPTIONS = {
    httpOnly: false, // Must be false for client-side access
    secure: true, // HTTPS only in production
    sameSite: 'strict' as const,
    maxAge: 30 * 60 * 1000 // 30 minutes
  }

  async function login(credentials: LoginCredentials) {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest' // CSRF protection
        },
        credentials: 'same-origin', // Include cookies
        body: JSON.stringify(credentials)
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
      }

      const { access_token, user: userData } = await response.json()
      
      // Store token securely (consider using HTTP-only cookies in production)
      accessToken.value = access_token
      user.value = userData
      
      // Set cookie with secure options
      document.cookie = `access_token=${access_token}; ${Object.entries(COOKIE_OPTIONS)
        .map(([key, value]) => `${key}=${value}`)
        .join('; ')}`
        
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  function logout() {
    accessToken.value = null
    user.value = null
    
    // Clear cookies
    document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/'
    
    // Redirect to login
    router.push('/login')
  }

  // Automatic token refresh
  function setupTokenRefresh() {
    const refreshInterval = setInterval(async () => {
      if (isAuthenticated.value) {
        try {
          await refreshToken()
        } catch (error) {
          console.error('Token refresh failed:', error)
          logout()
        }
      }
    }, 25 * 60 * 1000) // Refresh 5 minutes before expiry

    // Clear interval on logout
    return () => clearInterval(refreshInterval)
  }

  return {
    user: readonly(user),
    isAuthenticated,
    login,
    logout,
    setupTokenRefresh
  }
})
```

#### API Request Interceptor with Security Headers
```typescript
// api/client.ts
class ApiClient {
  private baseURL = '/api'
  
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const authStore = useAuthStore()
    
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest', // CSRF protection
        ...options.headers,
      },
      credentials: 'same-origin', // Include cookies
    }

    // Add authentication header
    if (authStore.isAuthenticated) {
      config.headers = {
        ...config.headers,
        'Authorization': `Bearer ${authStore.accessToken}`
      }
    }

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, config)
      
      // Handle authentication errors
      if (response.status === 401) {
        authStore.logout()
        throw new Error('Authentication required')
      }
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error)
      throw error
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }
}

export const apiClient = new ApiClient()
```

## Cross-Site Scripting (XSS) Prevention

### Backend XSS Protection
```python
import bleach
from markupsafe import escape

def sanitize_html_content(content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks."""
    allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
    allowed_attributes = {}
    
    return bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )

def escape_user_input(text: str) -> str:
    """Escape user input for safe HTML rendering."""
    return escape(text)

# Use in Pydantic models
class CreatePostRequest(BaseModel):
    title: str
    content: str
    
    @validator('title', 'content')
    def sanitize_text(cls, v):
        return sanitize_html_content(v)
```

### Frontend XSS Protection
```vue
<template>
  <div>
    <!-- ✅ SAFE: Vue automatically escapes text content -->
    <p>{{ userInput }}</p>
    
    <!-- ✅ SAFE: Sanitized HTML rendering -->
    <div v-html="sanitizedHtml"></div>
    
    <!-- ❌ DANGEROUS: Never use v-html with unsanitized user input -->
    <!-- <div v-html="rawUserInput"></div> -->
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import DOMPurify from 'dompurify'

const props = defineProps<{
  userInput: string
  rawHtml: string
}>()

// Sanitize HTML before rendering
const sanitizedHtml = computed(() => 
  DOMPurify.sanitize(props.rawHtml, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em'],
    ALLOWED_ATTR: []
  })
)
</script>
```

## Content Security Policy (CSP)

### Backend CSP Headers
```python
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Content Security Policy
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://trusted-cdn.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://api.trusted-service.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'"
    )
    
    response.headers["Content-Security-Policy"] = csp_policy
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "yourdomain.com"]
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Never use "*" in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Environment and Configuration Security

### Backend Environment Security
```python
# core/config.py
from pydantic import BaseSettings, validator
import secrets
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str
    database_echo: bool = False
    
    # Security
    secret_key: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS
    allowed_origins: list[str] = ["http://localhost:3000"]
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600
    
    # Encryption
    encryption_key: Optional[str] = None
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('Secret key must be at least 32 characters long')
        return v
    
    @validator('allowed_origins')
    def validate_origins(cls, v):
        for origin in v:
            if origin == "*":
                raise ValueError('Wildcard origins not allowed in production')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Generate secure defaults
def generate_secret_key() -> str:
    return secrets.token_urlsafe(32)

settings = Settings()
```

### Frontend Environment Security
```typescript
// config/environment.ts
interface EnvironmentConfig {
  apiBaseUrl: string
  enableDevTools: boolean
  logLevel: 'debug' | 'info' | 'warn' | 'error'
  csrfTokenName: string
}

function getConfig(): EnvironmentConfig {
  // Only expose safe environment variables
  const isDev = import.meta.env.DEV
  
  return {
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '/api',
    enableDevTools: isDev,
    logLevel: isDev ? 'debug' : 'warn',
    csrfTokenName: 'X-CSRF-Token'
  }
}

export const config = getConfig()

// Never expose sensitive data in frontend code
// ❌ DON'T DO THIS:
// export const API_KEY = 'secret-key-12345'
// export const DATABASE_URL = 'postgresql://...'
```

## File Upload Security

### Backend File Upload Security
```python
import os
import magic
from pathlib import Path
from fastapi import UploadFile, HTTPException, status

class FileUploadService:
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt'}
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/png', 'image/gif', 
        'application/pdf', 'text/plain'
    }
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR = Path("uploads")
    
    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """Validate uploaded file for security."""
        
        # Check file size
        if file.size > FileUploadService.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {FileUploadService.MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in FileUploadService.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {FileUploadService.ALLOWED_EXTENSIONS}"
            )
        
        # Check MIME type using python-magic
        file_content = file.file.read()
        file.file.seek(0)  # Reset file pointer
        
        detected_mime = magic.from_buffer(file_content, mime=True)
        if detected_mime not in FileUploadService.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File content doesn't match allowed types"
            )
    
    @staticmethod
    def generate_safe_filename(filename: str) -> str:
        """Generate a safe filename to prevent directory traversal."""
        import uuid
        import re
        
        # Remove directory traversal attempts
        safe_name = os.path.basename(filename)
        
        # Remove or replace dangerous characters
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', safe_name)
        
        # Generate unique filename to prevent conflicts
        name, ext = os.path.splitext(safe_name)
        unique_id = uuid.uuid4().hex[:8]
        
        return f"{name}_{unique_id}{ext}"

@app.post("/upload")
async def upload_file(file: UploadFile):
    FileUploadService.validate_file(file)
    
    safe_filename = FileUploadService.generate_safe_filename(file.filename)
    file_path = FileUploadService.UPLOAD_DIR / safe_filename
    
    # Ensure upload directory exists
    FileUploadService.UPLOAD_DIR.mkdir(exist_ok=True)
    
    # Save file securely
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return {"filename": safe_filename, "size": len(content)}
```

## Security Testing and Monitoring

### Security Test Cases
```python
# tests/security/test_security.py
import pytest
from fastapi.testclient import TestClient

class TestSecurityVulnerabilities:
    
    def test_sql_injection_protection(self, client: TestClient):
        """Test that SQL injection attempts are blocked."""
        malicious_input = "1' OR '1'='1"
        response = client.get(f"/api/users/{malicious_input}")
        
        # Should return 422 (validation error) or 404, not 200
        assert response.status_code in [404, 422]
    
    def test_xss_protection(self, client: TestClient):
        """Test that XSS attempts are sanitized."""
        malicious_script = "<script>alert('xss')</script>"
        response = client.post("/api/users", json={
            "name": malicious_script,
            "email": "test@example.com"
        })
        
        if response.status_code == 201:
            user_data = response.json()
            assert "<script>" not in user_data["name"]
    
    def test_authentication_required(self, client: TestClient):
        """Test that protected endpoints require authentication."""
        response = client.get("/api/protected-resource")
        assert response.status_code == 401
    
    def test_rate_limiting(self, client: TestClient):
        """Test that rate limiting is enforced."""
        for _ in range(10):  # Assuming rate limit is less than 10 requests
            response = client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": "wrongpassword"
            })
        
        # Eventually should hit rate limit
        assert response.status_code == 429
    
    def test_csrf_protection(self, client: TestClient):
        """Test CSRF protection for state-changing operations."""
        response = client.post("/api/users", json={"name": "Test"})
        # Should require proper CSRF token or fail
        assert response.status_code in [403, 401]
```

## Security Checklist

### Pre-Deployment Security Review
- ✅ All user inputs are validated and sanitized
- ✅ SQL injection protection is implemented
- ✅ XSS protection is in place
- ✅ Authentication and authorization are properly configured
- ✅ Secrets are not hardcoded in the source code
- ✅ HTTPS is enforced in production
- ✅ Security headers are configured (CSP, HSTS, etc.)
- ✅ Rate limiting is implemented for sensitive endpoints
- ✅ File upload validation is comprehensive
- ✅ Error messages don't expose sensitive information
- ✅ Dependencies are up to date and free of known vulnerabilities
- ✅ Security tests are included and passing
- ✅ Logging is configured for security events
- ✅ CORS is properly configured (no wildcard origins)
- ✅ Session management is secure (HTTP-only cookies, secure flags)