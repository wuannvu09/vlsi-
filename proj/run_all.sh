#!/usr/bin/env bash
# Chay toan bo: VTC -> chon k -> I-V, AND, HA14, HA18 -> phan tich -> sinh slide
cd "$(dirname "$0")"
[ -f .venv/bin/activate ] && . .venv/bin/activate
# Windows (Git Bash / MSYS2): venv dung Scripts/, ngspice console la ngspice_con
[ -f .venv/Scripts/activate ] && . .venv/Scripts/activate
NGSPICE=ngspice; command -v ngspice_con >/dev/null && NGSPICE=ngspice_con
PY=python3; [ -n "$VIRTUAL_ENV" ] && [ -f "$VIRTUAL_ENV/Scripts/python.exe" ] && PY=python
export PYTHONUTF8=1
mkdir -p data figs logs output
run(){ echo ">> ngspice $1"; (cd sim && $NGSPICE -b "$1.spice" > "../logs/$1.log" 2>&1) || echo "   (ngspice tra ve loi, xem logs/$1.log)"; }
run 02_inv_vtc
$PY scripts/analyze.py --vtc
for f in 01_iv 03_and 04_ha14 05_ha18; do run $f; done
$PY scripts/analyze.py --all
# Schematic Xschem + LVS + anh slide 13 (bo qua neu chua cai xschem/netgen)
if command -v xschem >/dev/null && { command -v netgen-lvs >/dev/null || command -v netgen >/dev/null; }; then
  echo ">> xschem/build.sh"; ./xschem/build.sh || echo "   (schematic/LVS loi, xem xschem/lvs/)"
fi
$PY slides/build_slides.py
echo "Ket qua: results.json | Kiem tra: logs/check_report.md | Slide: output/BTL_VLSI_AND_HalfAdder_HUST.pptx"
