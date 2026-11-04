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

# uu tien libs.tech/combined (ban ngspice/ in nhieu loi include nfet_20v0, vo hai nhung log ban)
find_lib(){
  local f
  for sub in combined ngspice; do
    f=$(find "$1" -path "*sky130A/libs.tech/$sub/sky130.lib.spice" 2>/dev/null | head -1)
    [ -n "$f" ] && { echo "$f"; return; }
  done
}

# Tim PDK co san (open_pdks, IIC-OSIC-TOOLS, volare)
LIB=""
for d in "$PDK_ROOT" /foss/pdks /usr/local/share/pdk /usr/share/pdk "$HOME/.volare" /opt; do
  [ -n "$d" ] && [ -d "$d" ] || continue
  LIB=$(find_lib "$d")
  [ -n "$LIB" ] && break
done
if [ -z "$LIB" ]; then
  # Phien ban PDK co dinh de so lieu tai lap duoc (khop bang tham chieu trong TRANG_THAI.md)
  VER=c6d73a35f524070e85faff4a6a9eef49553ebc2b
  echo "Chua co PDK sky130 -> tai bang volare, phien ban $VER (vai tram MB)..."
  volare enable --pdk sky130 "$VER"
  LIB=$(find_lib "$HOME/.volare")
fi
[ -n "$LIB" ] || { echo "Khong tim thay sky130.lib.spice"; exit 1; }
echo ".lib $LIB tt" > sim/pdk.spice
echo "PDK: $LIB"
echo "Xong. Chay tiep: ./run_all.sh"
