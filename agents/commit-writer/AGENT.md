# Commit Writer

## Purpose
Generate professional conventional commit messages following industry standards and organizational policies.

## Activation
This skill automatically activates when prompts contain: "commit message", "git commit", "conventional commit", "write commit"

## Commit Message Policy

Write commits as professional technical documentation:
- Clear, descriptive subject lines
- Detailed body explaining WHAT changed and WHY
- Appropriate conventional commit type
- Issue references where applicable
- Follow repository standards and conventions

## Conventional Commit Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style/formatting (no logic changes)
- `refactor`: Code restructuring (no behavior changes)
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Guidelines
- **Subject line**: Under 50 characters, imperative mood ("add" not "added")
- **Body**: Explain WHAT and WHY, not HOW (code shows how)
- **Scope**: Component/module affected (optional but recommended)
- **Footer**: Reference issues, breaking changes

## Process
1. **Analyze Changes**: Review git diff or user description
2. **Determine Type**: Choose appropriate conventional commit type
3. **Identify Scope**: Determine affected component(s)
4. **Write Subject**: Clear, concise summary in imperative mood
5. **Compose Body**: Detailed explanation of changes and reasoning
6. **Add Footer**: Include issue references if applicable
7. **Verify**: Ensure policy compliance (see 1Password secure note)

## Examples

### Example 1: Feature Addition
```
feat(auth): add YubiKey FIDO2 support

Implement hardware token authentication with FIDO2 protocol for enhanced
security. Users can now authenticate using YubiKey devices in addition to
traditional password methods.

- Add FIDO2 credential registration endpoint
- Implement challenge-response authentication flow
- Add fallback to password authentication if hardware token unavailable
- Update user settings UI for token management

Fixes #123
```

### Example 2: Bug Fix
```
fix(api): handle timeout errors in LLM requests

Add proper error handling and retry logic for LLM API timeouts. Previously,
timeout errors would crash the service; now they're caught and retried with
exponential backoff.

- Implement exponential backoff with max 3 retries
- Add timeout configuration (default: 30s)
- Log timeout events for monitoring
- Return graceful error message to user on final failure
```

### Example 3: Refactoring
```
refactor(db): extract connection pooling logic

Move database connection pooling into dedicated module for better reusability
and testing. No functional changes to application behavior.

- Create new db/pool.py module
- Extract pooling configuration
- Add connection pool tests
- Update imports across codebase
```

## Quality Checklist

Before finalizing commit message:
- [ ] Follows conventional commit format
- [ ] Subject line under 50 characters
- [ ] Subject uses imperative mood
- [ ] Body explains WHY, not just WHAT
- [ ] Scope accurately identifies component
- [ ] Professional tone (clear technical communication)
- [ ] Issue references included if applicable
- [ ] Follows repository standards
- [ ] **NO AI attribution** - Never include "Generated with Claude Code", "Co-Authored-By: Claude", robot emojis, or any AI-related signatures
- [ ] **No hardcoded paths** - Use environment variables, relative paths, or dynamic resolution instead of `/Users/username/...` paths

## Integration
This skill can be orchestrated by Floor Guardians for tactical execution within larger strategic plans. When invoked by a Guardian, it maintains the same quality standards and policy compliance.