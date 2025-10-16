---
description: 'Code review standards and guidelines for Python FastAPI and Vue.js applications'
applyTo: '**/*.py, **/*.vue, **/*.ts, **/*.js, **/*.md'
---

# Code Review Guidelines

Comprehensive code review standards to ensure code quality, security, maintainability, and team alignment.

## General Code Review Philosophy

- **Collaborative Learning** - Reviews are opportunities to share knowledge and improve skills
- **Quality Focus** - Prioritize correctness, readability, and maintainability
- **Constructive Feedback** - Provide actionable, respectful suggestions
- **Security Mindset** - Always consider security implications
- **Performance Awareness** - Consider performance impact of changes
- **Documentation Priority** - Ensure code is well-documented and self-explanatory

## Pre-Review Checklist (Author)

### Before Submitting PR
- ✅ All tests pass locally (`pytest` for backend, `npm test` for frontend)
- ✅ Code follows established style guidelines (Black, ESLint, Prettier)
- ✅ No linting errors or warnings
- ✅ Security considerations have been addressed
- ✅ Performance impact has been evaluated
- ✅ Documentation is updated (README, API docs, code comments)
- ✅ Commit messages follow conventional commit format
- ✅ PR description clearly explains changes and reasoning

### PR Description Template
```markdown
## Summary
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)  
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Changes Made
- Specific change 1
- Specific change 2
- Specific change 3

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] Edge cases considered

## Security Considerations
- [ ] Input validation implemented
- [ ] Authentication/authorization checked
- [ ] No sensitive data exposed
- [ ] Security best practices followed

## Performance Impact
- [ ] No negative performance impact
- [ ] Performance improvements documented
- [ ] Database queries optimized
- [ ] Caching implemented where appropriate

## Breaking Changes
List any breaking changes and migration steps required.

## Screenshots/Videos
Include visual changes if applicable.

## Related Issues
Closes #123, Related to #456
```

## Review Guidelines by File Type

### Python/FastAPI Code Review

#### Code Quality Checklist
```python
# ✅ GOOD: Clear, typed function with proper documentation
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Retrieve a user by ID with proper authorization.
    
    Args:
        user_id: The ID of the user to retrieve
        db: Database session dependency
        current_user: Authenticated user making the request
        
    Returns:
        UserResponse: User data if authorized
        
    Raises:
        HTTPException: 404 if user not found, 403 if unauthorized
    """
    if not current_user.can_view_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)

# ❌ BAD: Unclear function, missing types, no documentation
def get_user(id, db, user):
    u = db.query(User).filter(User.id == id).first()
    if not u:
        raise HTTPException(404)
    return u
```

#### Security Review Points
```python
# ✅ GOOD: Proper input validation and SQL injection prevention
@router.get("/users/search")
async def search_users(
    query: str = Query(..., min_length=2, max_length=50, regex="^[a-zA-Z0-9\s]+$"),
    db: Session = Depends(get_db)
):
    """Search users with validated input."""
    # Using ORM prevents SQL injection
    users = db.query(User).filter(
        User.name.ilike(f"%{query}%")
    ).limit(20).all()
    
    return [UserResponse.from_orm(user) for user in users]

# ❌ BAD: SQL injection vulnerability
@router.get("/users/search")  
async def search_users_bad(query: str, db: Session = Depends(get_db)):
    # DANGEROUS: Direct string interpolation in SQL
    sql = f"SELECT * FROM users WHERE name LIKE '%{query}%'"
    users = db.execute(text(sql)).fetchall()
    return users
```

#### Performance Review Points
```python
# ✅ GOOD: Efficient database query with pagination
@router.get("/users/{user_id}/notes")
async def get_user_notes(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get user notes with efficient pagination."""
    offset = (page - 1) * size
    
    notes = (
        db.query(Note)
        .options(selectinload(Note.tags))  # Eager load to prevent N+1
        .filter(Note.user_id == user_id)
        .offset(offset)
        .limit(size)
        .all()
    )
    
    return [NoteResponse.from_orm(note) for note in notes]

# ❌ BAD: N+1 query problem and no pagination
@router.get("/users/{user_id}/notes")
async def get_user_notes_bad(user_id: int, db: Session = Depends(get_db)):
    notes = db.query(Note).filter(Note.user_id == user_id).all()  # No limit
    
    # N+1 problem: separate query for each note's tags
    result = []
    for note in notes:
        tags = db.query(Tag).filter(Tag.note_id == note.id).all()  # N+1!
        result.append({"note": note, "tags": tags})
    
    return result
```

### Vue.js/TypeScript Code Review

#### Component Quality Checklist
```vue
<!-- ✅ GOOD: Well-structured component with proper TypeScript -->
<template>
  <div class="user-card" :class="cardClasses">
    <img 
      :src="user.avatar || defaultAvatar" 
      :alt="`${user.name} avatar`"
      class="user-card__avatar"
      @error="handleImageError"
    />
    
    <div class="user-card__content">
      <h3 class="user-card__name">{{ user.name }}</h3>
      <p class="user-card__email">{{ user.email }}</p>
      
      <div class="user-card__actions">
        <button 
          type="button"
          @click="handleEdit"
          :disabled="!canEdit"
          class="btn btn--primary"
        >
          Edit
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { User } from '@/types/user'

interface Props {
  user: User
  readonly?: boolean
}

interface Emits {
  edit: [user: User]
  delete: [userId: number]
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false
})

const emit = defineEmits<Emits>()

const defaultAvatar = '/images/default-avatar.png'
const imageError = ref(false)

const canEdit = computed(() => !props.readonly && props.user.isActive)

const cardClasses = computed(() => ({
  'user-card--readonly': props.readonly,
  'user-card--inactive': !props.user.isActive,
  'user-card--image-error': imageError.value
}))

function handleEdit() {
  if (canEdit.value) {
    emit('edit', props.user)
  }
}

function handleImageError() {
  imageError.value = true
}
</script>

<style scoped>
.user-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--surface-color);
}

.user-card--readonly {
  opacity: 0.7;
}

.user-card__avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.user-card__name {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.user-card__email {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
}
</style>
```

```vue
<!-- ❌ BAD: Poor component structure, no types, mixed concerns -->
<template>
  <div class="card" @click="edit">
    <img :src="user.avatar" />
    <div>
      <h3>{{ user.name }}</h3>
      <p>{{ user.email }}</p>
      <button @click="deleteUser">Delete</button>
    </div>
  </div>
</template>

<script setup>
// No TypeScript, no proper prop definitions
const props = defineProps(['user'])

function edit() {
  // Direct API call in component - should be in store/service
  fetch(`/api/users/${props.user.id}`, { method: 'PUT' })
    .then(() => window.location.reload()) // Poor UX
}

function deleteUser() {
  // No confirmation, poor error handling
  fetch(`/api/users/${props.user.id}`, { method: 'DELETE' })
}
</script>

<style>
/* No scoped styles - potential CSS conflicts */
.card { padding: 10px; }
img { width: 50px; }
</style>
```

#### Store/Composable Review Points
```typescript
// ✅ GOOD: Well-structured Pinia store with proper error handling
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, CreateUserRequest, UpdateUserRequest } from '@/types/user'
import { userApi } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  // State
  const users = ref<User[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const activeUsers = computed(() => 
    users.value.filter(user => user.isActive)
  )

  const getUserById = computed(() => 
    (id: number) => users.value.find(user => user.id === id)
  )

  // Actions with proper error handling
  async function fetchUsers() {
    if (loading.value) return // Prevent duplicate requests

    loading.value = true
    error.value = null

    try {
      const response = await userApi.getUsers()
      users.value = response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch users'
      console.error('Failed to fetch users:', err)
    } finally {
      loading.value = false
    }
  }

  async function createUser(userData: CreateUserRequest): Promise<User | null> {
    try {
      const newUser = await userApi.createUser(userData)
      users.value.push(newUser)
      return newUser
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create user'
      throw err // Re-throw for component handling
    }
  }

  return {
    // State (readonly for external access)
    users: readonly(users),
    loading: readonly(loading),
    error: readonly(error),
    // Getters
    activeUsers,
    getUserById,
    // Actions
    fetchUsers,
    createUser
  }
})
```

## Review Process

### Review Phases

#### 1. Automated Checks (Before Human Review)
- CI/CD pipeline passes
- All tests pass
- Code coverage meets requirements
- No security vulnerabilities detected
- Linting passes
- Performance benchmarks are acceptable

#### 2. Initial Review (15-30 minutes)
- High-level architecture and design decisions
- Security implications
- Performance considerations
- Breaking changes assessment
- Test coverage adequacy

#### 3. Detailed Review (30-60 minutes)
- Code quality and readability
- Error handling
- Edge cases coverage
- Documentation quality
- Naming conventions
- Code duplication

#### 4. Final Review (10-15 minutes)
- Address reviewer feedback
- Verify all concerns resolved
- Final approval decision

### Review Comments Guidelines

#### Effective Review Comments
```markdown
# ✅ GOOD: Specific, actionable feedback
**Issue**: This query could cause performance problems with large datasets.
**Suggestion**: Consider adding pagination and an index on the `created_at` column.
**Example**: 
```python
# Add this index in a migration
CREATE INDEX idx_users_created_at ON users(created_at);

# Update query to use pagination
.offset(offset).limit(limit)
```

# ✅ GOOD: Educational comment
**Learning opportunity**: Using `shallowRef` here would be more efficient for large objects since we don't need deep reactivity on the user list.
**Reference**: https://vuejs.org/api/reactivity-advanced.html#shallowref

# ❌ BAD: Vague, unhelpful comment
This doesn't look right.

# ❌ BAD: Nitpicky without value
You used single quotes instead of double quotes here.
```

#### Comment Categories
Use prefixes to categorize feedback:
- **MUST**: Critical issues that must be fixed before merge
- **SHOULD**: Important improvements that should be addressed
- **CONSIDER**: Suggestions for consideration
- **QUESTION**: Clarification needed
- **LEARNING**: Educational opportunities
- **PRAISE**: Positive feedback on good practices

### Security-Focused Review

#### Security Review Checklist
- ✅ All user inputs are validated and sanitized
- ✅ No hardcoded secrets or sensitive data
- ✅ Proper authentication and authorization
- ✅ SQL injection prevention measures
- ✅ XSS prevention implemented
- ✅ File upload security (if applicable)
- ✅ Rate limiting considerations
- ✅ Error messages don't expose sensitive information
- ✅ Dependencies are up to date and secure
- ✅ Proper logging without sensitive data

### Performance-Focused Review

#### Performance Review Checklist
- ✅ Database queries are optimized
- ✅ N+1 query problems avoided
- ✅ Proper pagination implemented
- ✅ Caching strategies appropriate
- ✅ Bundle size impact considered (frontend)
- ✅ Memory usage patterns reviewed
- ✅ Async patterns used correctly
- ✅ No obvious performance bottlenecks

## Advanced Review Practices

### Code Review Tools Integration

#### GitHub PR Templates
```yaml
# .github/pull_request_template.md
## Description
Brief summary of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature  
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing complete

## Code Quality
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Code is well-commented
- [ ] Documentation updated

## Security
- [ ] Security implications considered
- [ ] Input validation implemented
- [ ] No sensitive data exposed

## Performance
- [ ] Performance impact assessed
- [ ] Database queries optimized
- [ ] Bundle size impact minimal (frontend)
```

#### Automated Review Checks
```yaml
# .github/workflows/code-review.yml
name: Automated Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Security Scan
        uses: securecodewarrior/github-action-add-sarif@v1
        with:
          sarif-file: 'security-scan-results.sarif'
      
      - name: Check Code Coverage
        run: |
          # Backend coverage
          cd backend && pytest --cov=app --cov-report=json
          # Frontend coverage  
          cd frontend && npm run test:coverage
          
      - name: Performance Budget Check
        run: |
          cd frontend
          npm run build
          npx bundlesize
      
      - name: Documentation Check
        run: |
          # Check if documentation was updated
          git diff --name-only origin/main...HEAD | grep -E "\.(md|rst)$" || echo "No docs updated"
```

### Review Metrics and Improvement

#### Tracking Review Effectiveness
```typescript
// Review metrics to track
interface ReviewMetrics {
  averageReviewTime: number      // Time to first review
  reviewCycles: number           // Number of review rounds
  defectsFoundInReview: number   // Issues caught in review
  defectsFoundInProduction: number // Issues that escaped review
  reviewParticipation: number    // Team members participating
}

// Goals for healthy review process
const reviewGoals = {
  averageReviewTime: 24, // hours
  reviewCycles: 2,       // maximum rounds
  reviewCoverage: 100,   // percentage of PRs reviewed
  reviewerDistribution: 80 // percentage having multiple reviewers
}
```

## Review Best Practices

### For Authors
- Keep PRs small and focused (< 400 lines of changes)
- Write clear PR descriptions with context and reasoning
- Test thoroughly before requesting review
- Respond to feedback promptly and professionally
- Ask questions when feedback is unclear
- Update documentation alongside code changes

### For Reviewers
- Review within 24 hours when possible
- Focus on important issues, not minor style preferences
- Provide specific, actionable feedback
- Ask questions to understand the reasoning
- Approve when ready, even if minor suggestions remain
- Consider the learning opportunities for junior developers

### For Teams
- Establish clear review criteria and standards
- Rotate reviewers to spread knowledge
- Have at least two reviewers for critical changes
- Use pair programming for complex features
- Regular retrospectives on review process effectiveness
- Celebrate good code and positive review practices

## Common Review Anti-Patterns to Avoid

### Author Anti-Patterns
- ❌ Submitting untested code
- ❌ Making PRs too large or unfocused
- ❌ Not responding to reviewer feedback
- ❌ Being defensive about suggestions
- ❌ Rushing to merge without proper review

### Reviewer Anti-Patterns
- ❌ Focusing only on style instead of substance
- ❌ Being overly critical or negative
- ❌ Approving without actually reviewing
- ❌ Blocking on personal preferences
- ❌ Not providing constructive alternatives

### Team Anti-Patterns
- ❌ Skipping reviews for "urgent" changes
- ❌ Only having one person review everything
- ❌ Not enforcing review standards consistently
- ❌ Treating reviews as gatekeeping instead of collaboration
- ❌ Not measuring or improving review effectiveness