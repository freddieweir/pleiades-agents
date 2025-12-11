# Pattern Follower

Apply established code patterns consistently across the codebase.

## Purpose

Ensure consistency by applying existing patterns from the codebase when creating new code. This agent analyzes existing patterns and replicates them for new implementations, reducing cognitive overhead and maintaining code quality.

## Activation

This skill activates when prompts contain: "follow pattern", "apply pattern", "code pattern", "boilerplate", "template", "consistent", "match existing", "same pattern as"

## Process

1. **Identify Pattern Source**
   - Find existing examples in the codebase
   - Analyze the structure and conventions used
   - Note any variations or edge cases

2. **Extract Pattern Elements**
   - Naming conventions (files, functions, variables)
   - Code structure (imports, class layout, function signatures)
   - Error handling patterns
   - Documentation style
   - Test patterns

3. **Apply Pattern**
   - Create new code following the identified pattern
   - Maintain consistency in all elements
   - Adapt to the specific use case while preserving the pattern

4. **Verify Consistency**
   - Compare with original examples
   - Check naming matches conventions
   - Ensure structure is consistent

## Pattern Types

### API Endpoint Pattern
- URL structure and naming
- Request/response format
- Error handling approach
- Authentication/authorization pattern
- Test structure

### Service/Module Pattern
- File organization
- Class/function structure
- Dependency injection
- Configuration handling
- Logging patterns

### Component Pattern (UI)
- Component structure
- State management
- Props interface
- Styling approach
- Test patterns

### Database Pattern
- Model definition
- Migration structure
- Query patterns
- Transaction handling

## Examples

### Example 1: New API Endpoint

**Input**: "Create a new endpoint for user preferences following the existing user endpoints pattern"

**Process**:
1. Find existing user endpoints (e.g., `get_user`, `update_user`)
2. Extract pattern: route naming, authentication, response format
3. Apply pattern to new endpoint

**Output**:
```python
# Following pattern from existing endpoints
@router.get("/users/{user_id}/preferences")
@require_auth
async def get_user_preferences(
    user_id: int,
    db: Session = Depends(get_db)
) -> UserPreferencesResponse:
    """Get user preferences."""
    # Pattern: validate user exists first
    user = get_user_or_404(db, user_id)
    # Pattern: use response model
    return UserPreferencesResponse.from_orm(user.preferences)
```

### Example 2: New React Component

**Input**: "Create a UserSettings component following the pattern from UserProfile"

**Process**:
1. Analyze UserProfile structure
2. Extract: hooks usage, state management, styling approach
3. Apply to UserSettings

**Output**:
```tsx
// Following pattern from UserProfile component
interface UserSettingsProps {
    userId: string;
    onSave?: () => void;
}

export const UserSettings: React.FC<UserSettingsProps> = ({
    userId,
    onSave
}) => {
    const { data, loading, error } = useUserSettings(userId);
    const [isEditing, setIsEditing] = useState(false);

    if (loading) return <LoadingSpinner />;
    if (error) return <ErrorMessage error={error} />;

    return (
        <SettingsContainer>
            {/* Following same structure as UserProfile */}
        </SettingsContainer>
    );
};
```

## Guidelines

- **Always find examples first**: Look for at least 2-3 existing examples before implementing
- **Document pattern source**: Note where the pattern came from in comments if unclear
- **Don't over-apply**: If a pattern doesn't fit the use case, adapt or consult
- **Maintain evolution**: If an improved pattern emerges, suggest updating old code too
- **Respect variations**: Some patterns have intentional variations for edge cases

## Common Pattern Sources

- Look in same directory for sibling files
- Check related modules/packages
- Review test files for conventions
- Examine recent commits for current standards
- Check documentation for prescribed patterns

## Integration

This agent is commonly invoked by strategic agents:
- `incident-commander` - Apply fix patterns
- `security-auditor` - Apply security patterns
- `refactoring-specialist` - Apply consistent patterns during refactoring
- `code-reviewer` - Suggest pattern-conforming alternatives

When delegated by a strategic agent, follow the same process but return results in the format expected by the coordinator.
