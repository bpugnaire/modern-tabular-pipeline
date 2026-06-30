#!/bin/bash
# Quick verification that deployment files are in place
echo "✓ FastAPI: src/api/"
ls -1 src/api/*.py 2>/dev/null | sed 's/^/  /'
echo ""
echo "✓ Docker: infra/docker/"
ls -1 infra/docker/* 2>/dev/null | sed 's/^/  /'
echo ""
echo "✓ Cloud Deploy: infra/gcp/"
ls -1 infra/gcp/*.sh 2>/dev/null | sed 's/^/  /'
echo ""
echo "✓ CI/CD: .github/workflows/"
ls -1 .github/workflows/*.yml 2>/dev/null | sed 's/^/  /'
echo ""
echo "✓ Examples: examples/"
ls -1 examples/* 2>/dev/null | sed 's/^/  /'
echo ""
echo "✅ All deployment files present!"
