#!/usr/bin/env bash

# Sanal ortamı etkinleştir
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
else
  echo "Sanal ortam bulunamadı. 'python3 -m venv .venv' ile oluşturun."
  exit 1
fi

if [ -z "$1" ]; then
  echo "Kullanım: ./run-unix.sh <input> [output]"
  exit 1
fi

if [ -z "$2" ]; then
  python3 docx-converter.py -i "$1"
else
  python3 docx-converter.py -i "$1" -o "$2"
fi
