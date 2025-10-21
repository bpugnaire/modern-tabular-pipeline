# Working with Git in VSCode

## The Pre-commit Hook Challenge

Our project uses pre-commit hooks that **auto-fix** code (Ruff formatting, trailing whitespace, etc.). This can cause issues with VSCode's Git UI because:

1. You click "Commit" in VSCode
2. Pre-commit hooks run and modify files
3. VSCode doesn't see the modified files
4. Commit appears to fail or hang

## ✅ Recommended Workflow

### Use the Integrated Terminal (Best Option)

Open VSCode's terminal (`Ctrl+`` or `Cmd+``) and run:

```bash
# Check what changed
git status

# Stage all changes
git add .

# Commit (pre-commit will auto-fix and re-stage)
git commit -m "Your commit message"

# Push
git push
```

**Why this works**: You see the pre-commit output and any auto-fixes happen transparently.

### Alternative: Two-Stage VSCode UI Commit

If you prefer the VSCode Git UI:

**Stage 1: Let pre-commit fix files**
1. Stage your changes in VSCode
2. Click "Commit"
3. Pre-commit runs and modifies files
4. Commit fails (this is expected!)

**Stage 2: Commit the fixed files**
1. You'll see new changes appear (the auto-fixes)
2. Stage these new changes
3. Click "Commit" again
4. Now it succeeds! ✓

## Quick Commands

We've added helper commands to the Makefile:

```bash
# Run all quality checks before committing
make quality

# Clean up temporary files
make clean
```

## VSCode Settings

We've configured VSCode to:
- Use Ruff for Python formatting
- Auto-format on save
- Exclude build artifacts from search/watch
- Use the project's virtual environment

The settings are in `.vscode/settings.json` and are committed to the repo for consistency.

## Recommended Extensions

Install these VSCode extensions (VSCode will prompt you):
- **Ruff** - Python linting and formatting
- **Python** - Python language support
- **Pylance** - Python type checking
- **dbt Power User** - dbt development tools
- **YAML** - YAML language support
- **Even Better TOML** - TOML support

## Git Best Practices

1. **Commit often** - Small, focused commits
2. **Write clear messages** - Use conventional commits format
3. **Run `make quality`** before big commits
4. **Check `git status`** after pre-commit runs
5. **Use feature branches** for major changes

## Troubleshooting

**"Nothing to commit" after VSCode commit fails:**
- Pre-commit modified files but didn't stage them
- Solution: Run `git add .` then `git commit` again

**"Working tree clean" but VSCode shows changes:**
- Restart VSCode or reload the window
- VSCode's Git cache might be stale

**Pre-commit seems stuck:**
- Check the terminal output
- Some hooks (like mypy) can take 10-20 seconds
