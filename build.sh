#!/bin/bash
set -e

# echo "📦 Installing dependencies..."
# mkdir -p build
# pip install -r requirements.txt --target build

echo "🧱 Copying source files..."
mkdir -p ./build
cp *.py requirements.txt .env cookies.txt build/

echo "🧩 Creating zip..."
cd build
zip -r ../ytdl-function.zip .
cd ..

echo "✅ Done"
