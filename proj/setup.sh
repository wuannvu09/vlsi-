#!/usr/bin/env bash
# Cai dat moi truong: ngspice, Python packages, PDK sky130. Chay tren Ubuntu / WSL.
cd "$(dirname "$0")"
set -e
if ! command -v ngspice >/dev/null; then
  if command -v apt-get >/dev/null; then sudo apt-get update && sudo apt-get install -y ngspice python3-venv python3-pip
  elif command -v brew >/dev/null; then brew install ngspice
  else echo "Hay tu cai ngspice (>= 36) roi chay lai."; exit 1; fi
fi
ngspice -v 2>/dev/null | head -3 || true
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q -r requirements.txt

# Tim PDK co san (open_pdks, IIC-OSIC-TOOLS, volare)
LIB=""
for d in "$PDK_ROOT" /foss/pdks /usr/local/share/pdk /usr/share/pdk "$HOME/.volare" /opt; do
  [ -n "$d" ] && [ -d "$d" ] || continue
  LIB=$(find "$d" -name sky130.lib.spice -path '*sky130A*' 2>/dev/null | head -1)
  [ -n "$LIB" ] && break
done
if [ -z "$LIB" ]; then
  echo "Chua co PDK sky130 -> tai bang volare (vai tram MB)..."
  VER=$(volare ls-remote --pdk sky130 2>/dev/null | grep -oE '[0-9a-f]{40}' | head -1)
  [ -n "$VER" ] || { echo "Khong lay duoc danh sach phien ban PDK (kiem tra mang)."; exit 1; }
  volare enable --pdk sky130 "$VER"
  LIB=$(find "$HOME/.volare" -name sky130.lib.spice -path '*sky130A*' | head -1)
fi
[ -n "$LIB" ] || { echo "Khong tim thay sky130.lib.spice"; exit 1; }
echo ".lib $LIB tt" > sim/pdk.spice
echo "PDK: $LIB"
echo "Xong. Chay tiep: ./run_all.sh"
