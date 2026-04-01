#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo ""
echo "======================================"
echo "Running Ruff lint and format checks..."
echo "======================================"
uv run ruff check dungeonsheets/
uv run ruff format --check dungeonsheets/

cd examples/

if [ "${DUNGEONSHEETS_RUN_PDF_BUILDS:-0}" = "1" ]; then
    echo ""
    echo "======================================"
    echo "Testing makesheets (standard)..."
    echo "======================================"
    uv run makesheets --debug

    echo ""
    echo "======================================"
    echo "Testing makesheets (fancy)..."
    echo "======================================"
    uv run makesheets --debug --fancy
else
    echo ""
    echo "======================================"
    echo "Skipping PDF build checks (DUNGEONSHEETS_RUN_PDF_BUILDS not set)..."
    echo "======================================"
fi

echo ""
echo "======================================"
echo "Testing makesheets (epub)..."
echo "======================================"
uv run makesheets --debug --output-format=epub

echo ""
echo "======================================"
echo "Running pytest with coverage..."
echo "======================================"
cd ../
uv run pytest --cov=dungeonsheets tests/

echo ""
echo "======================================"
echo "All tests passed successfully!"
echo "======================================"
