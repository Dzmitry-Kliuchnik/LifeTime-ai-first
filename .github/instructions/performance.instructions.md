---
description: 'Performance optimization guidelines for Python FastAPI and Vue.js applications'
applyTo: '**/*.py, **/*.vue, **/*.ts, **/*.js'
---

# Performance Optimization Guidelines

Comprehensive performance practices for fullstack applications with Python FastAPI backend and Vue.js frontend.

## General Performance Philosophy

- **Measure First** - Profile before optimizing, use data to drive decisions
- **Optimize for the User** - Focus on metrics that affect user experience
- **Progressive Enhancement** - Start with a solid foundation, then optimize
- **Sustainable Performance** - Build performance considerations into development workflow
- **Monitor Continuously** - Track performance metrics in production

## Backend Performance (Python/FastAPI)

### Database Optimization

#### Query Performance
```python
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import func, and_, or_

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_users_with_notes_optimized(self, limit: int = 50, offset: int = 0):
        """Efficiently fetch users with their notes using eager loading."""
        return (
            self.db.query(User)
            .options(selectinload(User.notes))  # Eager load relationships
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def get_user_statistics_efficient(self):
        """Use database aggregation instead of Python loops."""
        return (
            self.db.query(
                func.count(User.id).label('total_users'),
                func.count(User.id).filter(User.is_active == True).label('active_users'),
                func.avg(User.age).label('average_age')
            )
            .first()
        )
    
    def search_users_indexed(self, search_term: str, limit: int = 20):
        """Use database indexes for text search."""
        # Assuming you have a full-text search index on name and email
        return (
            self.db.query(User)
            .filter(
                or_(
                    User.name.ilike(f'%{search_term}%'),
                    User.email.ilike(f'%{search_term}%')
                )
            )
            .limit(limit)
            .all()
        )

# Database connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql://user:password@localhost/dbname",
    poolclass=QueuePool,
    pool_size=20,  # Number of connections to maintain
    max_overflow=30,  # Additional connections allowed
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections every hour
    echo=False  # Disable in production
)
```

#### Database Indexes
```python
# models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Index

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)  # Indexed for lookups
    name = Column(String, index=True)  # Indexed for search
    created_at = Column(DateTime, index=True)  # Indexed for sorting/filtering
    
    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_user_name_email', 'name', 'email'),
        Index('idx_user_created_active', 'created_at', 'is_active'),
    )
```

### API Response Optimization

#### Pagination and Filtering
```python
from fastapi import Query, Depends
from typing import Optional

class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(20, ge=1, le=100, description="Page size"),
        sort_by: Optional[str] = Query(None, description="Sort field"),
        sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order")
    ):
        self.page = page
        self.size = size
        self.sort_by = sort_by
        self.sort_order = sort_order
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

@app.get("/api/users", response_model=PaginatedResponse[UserResponse])
async def get_users(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(None, min_length=2, max_length=50),
    active_only: bool = Query(False),
    user_service: UserService = Depends()
):
    """Get paginated users with optional filtering."""
    
    filters = {}
    if search:
        filters['search'] = search
    if active_only:
        filters['is_active'] = True
    
    users, total_count = await user_service.get_users_paginated(
        limit=pagination.size,
        offset=pagination.offset,
        sort_by=pagination.sort_by,
        sort_order=pagination.sort_order,
        **filters
    )
    
    return PaginatedResponse(
        items=users,
        total=total_count,
        page=pagination.page,
        size=pagination.size,
        pages=(total_count + pagination.size - 1) // pagination.size
    )
```

#### Response Caching
```python
from functools import wraps
from typing import Any, Dict
import redis
import json
import hashlib

# Redis cache setup
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_response(expiration: int = 300):
    """Cache API responses for specified duration."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"api_cache:{func.__name__}:{hashlib.md5(str(sorted(kwargs.items())).encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(
                cache_key,
                expiration,
                json.dumps(result, default=str)
            )
            
            return result
        return wrapper
    return decorator

@app.get("/api/statistics")
@cache_response(expiration=600)  # Cache for 10 minutes
async def get_statistics():
    """Get application statistics (cached)."""
    # Expensive calculation here
    return await statistics_service.calculate_stats()
```

### Async Programming Optimization

#### Efficient Async Patterns
```python
import asyncio
from typing import List
import aiohttp
from concurrent.futures import ThreadPoolExecutor

class OptimizedService:
    def __init__(self):
        self.http_session = None
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
    
    async def init_session(self):
        """Initialize HTTP session for connection reuse."""
        if not self.http_session:
            connector = aiohttp.TCPConnector(
                limit=100,  # Total connection pool size
                limit_per_host=30,  # Per-host connection limit
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            self.http_session = aiohttp.ClientSession(connector=connector)
    
    async def fetch_multiple_urls(self, urls: List[str]) -> List[dict]:
        """Efficiently fetch multiple URLs concurrently."""
        await self.init_session()
        
        async def fetch_one(url: str) -> dict:
            try:
                async with self.http_session.get(url, timeout=10) as response:
                    return await response.json()
            except Exception as e:
                return {"error": str(e), "url": url}
        
        # Use semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(10)
        
        async def fetch_with_limit(url: str):
            async with semaphore:
                return await fetch_one(url)
        
        tasks = [fetch_with_limit(url) for url in urls]
        return await asyncio.gather(*tasks)
    
    async def cpu_intensive_task(self, data: List[Any]) -> Any:
        """Run CPU-intensive tasks in thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.thread_pool,
            self._process_data,
            data
        )
    
    def _process_data(self, data: List[Any]) -> Any:
        """CPU-intensive processing (runs in thread pool)."""
        # Heavy computation here
        return sum(item.calculate_complex_value() for item in data)
```

## Frontend Performance (Vue.js)

### Component Optimization

#### Lazy Loading and Code Splitting
```typescript
// router/index.ts - Route-level code splitting
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/HomeView.vue')
    },
    {
      path: '/users',
      name: 'Users', 
      component: () => import('@/views/UsersView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/analytics',
      name: 'Analytics',
      // Lazy load heavy components
      component: () => import(
        /* webpackChunkName: "analytics" */ 
        '@/views/AnalyticsView.vue'
      )
    }
  ]
})
```

#### Component Performance Patterns
```vue
<template>
  <div class="user-list">
    <!-- Virtual scrolling for large lists -->
    <VirtualList
      v-if="users.length > 100"
      :items="users"
      :item-height="60"
      :container-height="400"
      #default="{ item }"
    >
      <UserCard :user="item" :key="item.id" />
    </VirtualList>
    
    <!-- Regular rendering for smaller lists -->
    <template v-else>
      <UserCard
        v-for="user in users"
        :key="user.id"
        :user="user"
        v-memo="[user.id, user.updatedAt]"
      />
    </template>
    
    <!-- Suspense for async components -->
    <Suspense>
      <AsyncUserStats />
      <template #fallback>
        <UserStatsSkeleton />
      </template>
    </Suspense>
  </div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent } from 'vue'
import type { User } from '@/types/user'

// Lazy load heavy components
const AsyncUserStats = defineAsyncComponent({
  loader: () => import('@/components/UserStats.vue'),
  delay: 200,
  timeout: 3000,
  errorComponent: () => import('@/components/ErrorComponent.vue'),
  loadingComponent: () => import('@/components/LoadingComponent.vue')
})

const props = defineProps<{
  users: User[]
}>()

// Memoized computed properties
const sortedUsers = computed(() => 
  [...props.users].sort((a, b) => a.name.localeCompare(b.name))
)

const usersByStatus = computed(() => {
  const active = []
  const inactive = []
  
  for (const user of props.users) {
    if (user.isActive) {
      active.push(user)
    } else {
      inactive.push(user)
    }
  }
  
  return { active, inactive }
})
</script>
```

### State Management Optimization

#### Efficient Pinia Stores
```typescript
// stores/user.ts
import { defineStore } from 'pinia'
import { ref, computed, shallowRef } from 'vue'
import type { User } from '@/types/user'

export const useUserStore = defineStore('user', () => {
  // Use shallowRef for large objects to avoid deep reactivity
  const users = shallowRef<Map<number, User>>(new Map())
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Computed properties are cached automatically
  const usersList = computed(() => Array.from(users.value.values()))
  
  const activeUsers = computed(() => 
    usersList.value.filter(user => user.isActive)
  )
  
  const userCount = computed(() => users.value.size)
  
  // Optimized actions
  function setUsers(newUsers: User[]) {
    // Use Map for O(1) lookups
    const userMap = new Map()
    for (const user of newUsers) {
      userMap.set(user.id, user)
    }
    users.value = userMap
  }
  
  function updateUser(userId: number, updates: Partial<User>) {
    const currentUser = users.value.get(userId)
    if (currentUser) {
      // Create new object to trigger reactivity
      const updatedUser = { ...currentUser, ...updates }
      users.value.set(userId, updatedUser)
      // Trigger reactivity for shallowRef
      users.value = new Map(users.value)
    }
  }
  
  async function fetchUsers(params: { page: number; size: number }) {
    if (loading.value) return // Prevent duplicate requests
    
    loading.value = true
    error.value = null
    
    try {
      const response = await userApi.getUsers(params)
      setUsers(response.items)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
    } finally {
      loading.value = false
    }
  }
  
  // Debounced search
  const debouncedSearch = debounce(async (query: string) => {
    const results = await userApi.searchUsers(query)
    setUsers(results)
  }, 300)
  
  return {
    users: readonly(users),
    loading: readonly(loading),
    error: readonly(error),
    usersList,
    activeUsers,
    userCount,
    setUsers,
    updateUser,
    fetchUsers,
    searchUsers: debouncedSearch
  }
})
```

### Network Optimization

#### Efficient API Communication
```typescript
// composables/useApi.ts
import { ref, Ref } from 'vue'

interface UseApiOptions {
  immediate?: boolean
  debounce?: number
  retries?: number
}

interface UseApiReturn<T> {
  data: Ref<T | null>
  loading: Ref<boolean>
  error: Ref<string | null>
  execute: (...args: any[]) => Promise<void>
  abort: () => void
}

export function useApi<T>(
  apiCall: (...args: any[]) => Promise<T>,
  options: UseApiOptions = {}
): UseApiReturn<T> {
  const data = ref<T | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  let abortController: AbortController | null = null
  
  const execute = async (...args: any[]) => {
    // Abort previous request
    if (abortController) {
      abortController.abort()
    }
    
    abortController = new AbortController()
    loading.value = true
    error.value = null
    
    let retries = options.retries || 0
    
    while (retries >= 0) {
      try {
        const result = await apiCall(...args, {
          signal: abortController.signal
        })
        data.value = result
        break
      } catch (err) {
        if (err.name === 'AbortError') {
          return // Request was aborted
        }
        
        if (retries > 0) {
          retries--
          await new Promise(resolve => setTimeout(resolve, 1000))
          continue
        }
        
        error.value = err instanceof Error ? err.message : 'API call failed'
      }
    }
    
    loading.value = false
  }
  
  const abort = () => {
    if (abortController) {
      abortController.abort()
    }
  }
  
  // Debounced execution
  const debouncedExecute = options.debounce 
    ? debounce(execute, options.debounce)
    : execute
  
  if (options.immediate) {
    debouncedExecute()
  }
  
  return {
    data,
    loading,
    error,
    execute: debouncedExecute,
    abort
  }
}
```

#### Request Optimization
```typescript
// api/client.ts
class OptimizedApiClient {
  private requestCache = new Map<string, Promise<any>>()
  private pendingRequests = new Set<string>()
  
  async get<T>(url: string, options: RequestInit = {}): Promise<T> {
    const cacheKey = `GET:${url}:${JSON.stringify(options)}`
    
    // Return cached promise if request is pending
    if (this.requestCache.has(cacheKey)) {
      return this.requestCache.get(cacheKey)
    }
    
    const requestPromise = this.executeRequest<T>(url, {
      ...options,
      method: 'GET'
    })
    
    // Cache the promise
    this.requestCache.set(cacheKey, requestPromise)
    
    // Clean up cache after request completes
    requestPromise.finally(() => {
      this.requestCache.delete(cacheKey)
    })
    
    return requestPromise
  }
  
  private async executeRequest<T>(url: string, options: RequestInit): Promise<T> {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    return response.json()
  }
  
  // Request batching for multiple similar requests
  private batchQueue = new Map<string, Array<{
    resolve: (value: any) => void
    reject: (error: any) => void
    params: any
  }>>()
  
  batchRequest<T>(
    endpoint: string, 
    params: any,
    batchKey: string = endpoint
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      if (!this.batchQueue.has(batchKey)) {
        this.batchQueue.set(batchKey, [])
        
        // Process batch after next tick
        setTimeout(() => this.processBatch(batchKey), 0)
      }
      
      this.batchQueue.get(batchKey)!.push({ resolve, reject, params })
    })
  }
  
  private async processBatch(batchKey: string) {
    const batch = this.batchQueue.get(batchKey)
    if (!batch || batch.length === 0) return
    
    this.batchQueue.delete(batchKey)
    
    try {
      const batchParams = batch.map(item => item.params)
      const results = await this.post(`/api/batch/${batchKey}`, { items: batchParams })
      
      results.forEach((result: any, index: number) => {
        batch[index].resolve(result)
      })
    } catch (error) {
      batch.forEach(item => item.reject(error))
    }
  }
}
```

### Bundle Optimization

#### Vite Configuration for Performance
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { splitVendorChunkPlugin } from 'vite'

export default defineConfig({
  plugins: [
    vue(),
    splitVendorChunkPlugin()
  ],
  
  build: {
    // Generate source maps for debugging
    sourcemap: true,
    
    // Rollup options for optimization
    rollupOptions: {
      output: {
        // Manual chunk splitting
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'ui-vendor': ['axios', 'date-fns'],
          'chart-vendor': ['chart.js', 'vue-chartjs']
        }
      }
    },
    
    // Chunk size warnings
    chunkSizeWarningLimit: 1000
  },
  
  // Optimize dependencies
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'axios']
  }
})
```

## Monitoring and Measurement

### Performance Monitoring

#### Backend Monitoring
```python
import time
from functools import wraps
import logging

# Performance monitoring decorator
def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log slow operations
            if execution_time > 1.0:  # Log if takes more than 1 second
                logging.warning(
                    f"Slow operation: {func.__name__} took {execution_time:.2f}s"
                )
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logging.error(
                f"Error in {func.__name__} after {execution_time:.2f}s: {str(e)}"
            )
            raise
    
    return wrapper

# Database query monitoring
@app.middleware("http")
async def db_query_monitor(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests
    if process_time > 2.0:
        logging.warning(f"Slow request: {request.url} took {process_time:.2f}s")
    
    return response
```

#### Frontend Performance Monitoring
```typescript
// utils/performance.ts
class PerformanceMonitor {
  private static instance: PerformanceMonitor
  
  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor()
    }
    return PerformanceMonitor.instance
  }
  
  measurePageLoad() {
    if (typeof window !== 'undefined' && 'performance' in window) {
      window.addEventListener('load', () => {
        setTimeout(() => {
          const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
          
          const metrics = {
            dns: navigation.domainLookupEnd - navigation.domainLookupStart,
            tcp: navigation.connectEnd - navigation.connectStart,
            ttfb: navigation.responseStart - navigation.requestStart,
            download: navigation.responseEnd - navigation.responseStart,
            dom: navigation.domContentLoadedEventEnd - navigation.navigationStart,
            load: navigation.loadEventEnd - navigation.navigationStart
          }
          
          console.log('Page Load Metrics:', metrics)
          
          // Send to analytics service
          this.sendMetrics('page-load', metrics)
        }, 0)
      })
    }
  }
  
  measureComponentRender(componentName: string) {
    const startMark = `${componentName}-start`
    const endMark = `${componentName}-end`
    
    performance.mark(startMark)
    
    return () => {
      performance.mark(endMark)
      performance.measure(componentName, startMark, endMark)
      
      const measure = performance.getEntriesByName(componentName)[0]
      if (measure.duration > 100) { // Log if render takes > 100ms
        console.warn(`Slow component render: ${componentName} took ${measure.duration}ms`)
      }
      
      // Clean up
      performance.clearMarks(startMark)
      performance.clearMarks(endMark)
      performance.clearMeasures(componentName)
    }
  }
  
  private sendMetrics(type: string, data: any) {
    // Send performance data to monitoring service
    // Implementation depends on your analytics provider
  }
}

export const performanceMonitor = PerformanceMonitor.getInstance()
```

## Performance Best Practices Checklist

### Backend Performance
- ✅ Database queries are optimized with proper indexes
- ✅ N+1 query problems are avoided with eager loading
- ✅ Connection pooling is configured for database
- ✅ API responses are paginated for large datasets
- ✅ Caching is implemented for expensive operations
- ✅ Async programming patterns are used correctly
- ✅ CPU-intensive tasks run in thread pools
- ✅ Response compression is enabled
- ✅ Database migrations don't block production

### Frontend Performance
- ✅ Components are lazy-loaded where appropriate
- ✅ Bundle size is optimized with code splitting
- ✅ Virtual scrolling is used for large lists
- ✅ Images are optimized and lazy-loaded
- ✅ Unnecessary re-renders are prevented with v-memo
- ✅ API calls are debounced and cached
- ✅ Large objects use shallowRef for reactivity
- ✅ Performance monitoring is implemented
- ✅ Critical rendering path is optimized