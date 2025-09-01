#!/bin/bash
# This script helps set up .pypirc securely
echo "Setting up .pypirc for future PyPI uploads..."
cat > ~/.pypirc << EOF
[pypi]
username = __token__
password = YOUR-PYPI-TOKEN-HERE
EOF
chmod 600 ~/.pypirc
echo "✅ Created ~/.pypirc with secure permissions (600)"
echo "⚠️  Remember to replace YOUR-PYPI-TOKEN-HERE with your actual token!"
