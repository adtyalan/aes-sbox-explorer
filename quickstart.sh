#!/bin/bash
# Quick Start Script untuk Fitur Excel Upload S-Box

echo "🚀 AES S-Box Upload Feature - Quick Start"
echo "========================================"
echo ""

# Check Python
echo "✓ Checking Python installation..."
python --version

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q openpyxl pandas fastapi uvicorn numpy

# Check if sample files exist
echo ""
echo "📄 Checking sample Excel files..."
if [ ! -f "sample_sbox_column.xlsx" ]; then
    echo "⚠️  Sample files not found. Creating them..."
    python create_sample_sbox_excel.py
else
    echo "✓ Sample files found:"
    ls -lh sample_sbox*.xlsx
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📖 Next steps:"
echo "1. Open Terminal 1: uvicorn api:app --reload"
echo "2. Open Terminal 2: Use index.html in browser"
echo "3. Go to Step 2 and click 'Pilih File Excel'"
echo "4. Try uploading one of the sample files"
echo ""
echo "For more details, see: EXCEL_UPLOAD_GUIDE.md"
