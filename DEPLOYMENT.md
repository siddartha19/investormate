# Deployment Guide for InvestorMate

This guide explains how to publish InvestorMate to PyPI.

## Prerequisites

1. **PyPI Account**
   - Create account at https://pypi.org/account/register/
   - Verify your email

2. **GitHub Repository**
   - Create repository: https://github.com/new
   - Name it `investormate`
   - Make it public

## Setup Steps

### 1. Configure PyPI Trusted Publisher

This allows GitHub Actions to publish without API tokens (more secure).

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in:
   - PyPI Project Name: `investormate`
   - Owner: `<your-github-username>`
   - Repository name: `investormate`
   - Workflow name: `publish.yml`
   - Environment name: (leave empty)

### 2. Push to GitHub

```bash
cd /Users/siddartha19/Downloads/investormate

# Add GitHub remote
git remote add origin https://github.com/<your-username>/investormate.git

# Push code and tag
git push -u origin main
git push origin v0.1.0
```

### 3. Automatic Publishing

When you push the tag `v0.1.0`, GitHub Actions will automatically:
- Build the package
- Run tests
- Publish to PyPI
- Create a GitHub release

Monitor the workflow at: https://github.com/<your-username>/investormate/actions

## Manual Publishing (Alternative)

If you prefer manual publishing:

```bash
# Install twine
pip install twine

# Build package
python -m build

# Check package
twine check dist/*

# Upload to Test PyPI (optional)
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Post-Publishing

### 1. Verify Installation

```bash
# In a new virtual environment
pip install investormate

# Test import
python -c "from investormate import Stock; print(Stock('AAPL'))"
```

### 2. Update Documentation

Update the GitHub repository description:
- Topic tags: python, finance, stocks, ai, yfinance, trading
- Description: "AI-powered stock analysis package for Python"
- Website: Link to PyPI page

### 3. Announce

Share on:
- Reddit: r/Python, r/algotrading, r/stocks
- Hacker News: "Show HN: InvestorMate - AI-powered stock analysis in Python"
- Twitter/X: Tag #Python #Finance #AI
- Dev.to: Write a blog post
- Python Weekly: Submit to newsletter

### Sample Announcement

```
🚀 InvestorMate v0.1.0 Released!

AI-powered stock analysis in Python. Ask any question about any stock.

Features:
✅ Multi-provider AI (OpenAI, Claude, Gemini)
✅ 60+ technical indicators
✅ Financial ratios & scoring
✅ Stock screening
✅ Portfolio analysis

pip install investormate

GitHub: https://github.com/<username>/investormate
PyPI: https://pypi.org/project/investormate/

#Python #Finance #AI #OpenSource
```

## Version Updates

For future releases:

1. Update version in `investormate/version.py`
2. Update `CHANGELOG.md`
3. Commit changes
4. Create new tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
5. Push: `git push origin v0.2.0`
6. GitHub Actions will auto-publish

## Troubleshooting

### Build Fails

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Rebuild
python -m build
```

### Import Errors

Make sure all `__init__.py` files exist:
```bash
find investormate -type d -exec touch {}/__init__.py \;
```

### Publishing Fails

1. Check PyPI trusted publisher is configured correctly
2. Verify tag name matches `v*` pattern
3. Check GitHub Actions logs for specific errors

## Security

- Never commit API keys
- Use environment variables in examples
- Keep dependencies updated
- Monitor security advisories

## Support

Issues: https://github.com/<your-username>/investormate/issues
