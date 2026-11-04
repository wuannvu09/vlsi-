#!/usr/bin/env bash
# Sinh schematic -> LVS -> xuat anh nen trang cho slide 13 (chi xuat khi LVS khop het).
#   ./xschem/build.sh        (can: xschem, netgen-lvs, rsvg-convert)
cd "$(dirname "$0")"
set -e
PDK_ROOT=${PDK_ROOT:-$(sed -E 's#^\.lib +(.*)/sky130A/.*#\1#' ../sim/pdk.spice)}
export PDK_ROOT
PY=python3; [ -x ../.venv/bin/python ] && PY=../.venv/bin/python   # can Pillow
python3 gen_sch.py
./lvs.sh | tee lvs/summary.txt
if grep -q "KHONG KHOP" lvs/summary.txt; then echo "LVS chua khop -> khong xuat anh."; exit 1; fi

mkdir -p svg
export_png(){ # $1 = schematic, $2 = file png
  # an layer 15, 17 (chu thich id/gm/vgs cho mo phong tuong tac); font hep de nhan khong de len day;
  # zoom theo khung bbox.json do gen_sch.py tinh (zoom_full cua Xschem bo qua chu, cat mat tieu de)
  local box; box=$(python3 -c "import json;print(*json.load(open('bbox.json'))['$1'])")
  xschem -x --preinit "set dark_colorscheme 0; set enable_layer(15) 0; set enable_layer(17) 0; \
    set svg_font_name {Liberation Sans Narrow}" \
    --command "xschem zoom_box $box; xschem print svg [file normalize svg/$1.svg]; xschem exit closewindow force" \
    "$1.sch" >/dev/null 2>&1
  rsvg-convert -w 1800 -b white "svg/$1.svg" -o "$2"
  # cat vien trang thua (giu le 30 px)
  "$PY" -c "
from PIL import Image, ImageOps
im = Image.open('$2').convert('RGB'); b = ImageOps.invert(im).getbbox(); p = 30
im.crop((max(b[0]-p,0), max(b[1]-p,0), min(b[2]+p,im.width), min(b[3]+p,im.height))).save('$2')"
  echo "  $2"
}
echo "Xuat anh:"
export_png and2  ../figs/schematic_and.png
export_png ha14  ../figs/schematic_ha.png
for c in inv nand2 oai21; do export_png $c ../figs/schematic_$c.png; done
