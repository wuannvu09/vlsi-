#!/usr/bin/env bash
# LVS: so netlist xuat tu schematic Xschem voi subckt trong sim/cells_sky130.spice bang netgen.
# Ket qua: xschem/lvs/<cell>.out, tom tat ghi them vao logs/check_report.md
cd "$(dirname "$0")"
PDK_ROOT=${PDK_ROOT:-$(sed -E 's#^\.lib +(.*)/sky130A/.*#\1#' ../sim/pdk.spice)}
export PDK_ROOT
SETUP=$PDK_ROOT/sky130A/libs.tech/netgen/sky130A_setup.tcl
NETGEN=$(command -v netgen-lvs || command -v netgen)
mkdir -p netlist lvs

# 1. Netlist tu schematic (dinh dang LVS: chi L, W, nf, m)
for c in inv nand2 oai21 and2 ha14; do
  xschem -x -q --command "set top_subckt 1; set lvs_netlist 1; xschem set format lvs_format; \
    set netlist_dir [file normalize netlist]; xschem netlist" $c.sch >/dev/null 2>&1
  [ -s netlist/$c.spice ] || { echo "Xschem khong xuat duoc netlist/$c.spice"; exit 1; }
done

# 2. Ban tham chieu: thay bieu thuc {..} trong cells_sky130.spice bang so (k, Wn, L tu results.json)
python3 - <<'EOF'
import json, re
s = json.load(open("../results.json"))["setup"]
env = {"k": s["k"], "Wn": s["wn"], "L": s["l"]}
txt = open("../sim/cells_sky130.spice").read()
txt = re.sub(r"\{([^}]*)\}", lambda m: f"{eval(m.group(1), {}, env):g}", txt)
open("lvs/cells_ref.spice", "w").write(txt + "\n.end\n")
EOF

# 3. netgen
summary=""
for c in inv nand2 oai21 and2 ha14; do
  C=$(echo $c | tr a-z A-Z)
  "$NETGEN" -batch lvs "netlist/$c.spice $c" "lvs/cells_ref.spice $C" "$SETUP" lvs/$c.out >lvs/$c.log 2>&1
  if grep -q "^Result: Circuits match uniquely" lvs/$c.log && ! grep -qiE "property errors|mismatch" lvs/$c.out
  then r="khop (topology + W/L)"; else r="KHONG KHOP, xem xschem/lvs/$c.out"; fi
  echo "LVS $c: $r"
  summary+="- LVS ${c} (schematic Xschem vs cells_sky130.spice ${C}): ${r}\n"
done

# 4. Ghi vao check_report.md (thay muc LVS cu neu co)
REP=../logs/check_report.md
if [ -f "$REP" ]; then
  python3 - "$REP" <<'EOF'
import sys
p = sys.argv[1]; t = open(p).read().split("## LVS schematic Xschem")[0].rstrip("\n")
open(p, "w").write(t + "\n")
EOF
  printf "\n## LVS schematic Xschem (netgen, %s)\n%b" "$(date +%F)" "$summary" >> "$REP"
fi
