# Pre-commit Hooks Test

This file tests that pre-commit hooks are working properly.

## What Pre-commit Hooks Do

1. **detect-secrets**: Scans for API keys, passwords, and other secrets
2. **bandit**: Checks for Python security vulnerabilities  
3. **black**: Formats Python code consistently
4. **isort**: Organizes imports
5. **Standard checks**: Trailing whitespace, large files, etc.

## Usage

Pre-commit hooks run automatically on `git commit`. To run manually:

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run detect-secrets --all-files

# Skip hooks for emergency commits
git commit --no-verify -m "Emergency commit"
```

## Security Benefits

✅ **Prevents secret leaks**: API keys, passwords, tokens  
✅ **Catches security issues**: SQL injection, XSS, etc.  
✅ **Maintains code quality**: Consistent formatting and imports  
✅ **Automated scanning**: No manual review needed
