#!/usr/bin/env python3
"""Doc log ngspice + du lieu wrdata -> results.json, figs/*.png, logs/check_report.md.
   --vtc : chi xu ly VTC va chon k (ghi vao sim/params.spice)
   --all : xu ly toan bo"""
import json, math, os, re, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, *p)
VDD = 1.8
NUM = r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?'
LINE = re.compile(r'^\s*([A-Za-z_]\w*)\s*=\s*(' + NUM + r')')
RED, BLUE, GOLD, GREY = "#BE1E2D", "#1F5F9E", "#E2A30F", "#6B6461"
plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": .3, "figure.dpi": 160})

def read_log(name):
    p = D("logs", name + ".log")
    return open(p, encoding="utf-8", errors="replace").read().splitlines() if os.path.exists(p) else []

def parse_vals(lines):
    out = {}
    for ln in lines:
        m = LINE.match(ln)
        if m and m.group(1).lower() not in out:
            out[m.group(1).lower()] = float(m.group(2))
    return out

def read_data(name):
    p = D("data", name)
    if not os.path.exists(p): return None, None
    with open(p) as f:
        head = f.readline().split()
    arr = np.atleast_2d(np.loadtxt(p, skiprows=1))
    return head, arr

SI = {"f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "": 1.0}
def si(s):
    m = re.match(r'(' + NUM + r')([fpnum]?)', s.strip(), re.I)
    return float(m.group(1)) * SI[m.group(2).lower()] if m else None

def params():
    """Tham so trong sim/params.spice: vdd (V), l, wn (um), k, cl (F)"""
    s = open(D("sim", "params.spice")).read()
    return {k.lower(): si(v) for k, v in re.findall(r'\b(VDD|L|Wn|k|CL)=(\S+)', s)}

def split_sweeps(x, y):
    cuts = [0] + [i for i in range(1, len(x)) if x[i] < x[i-1]] + [len(x)]
    return [(x[a:b], y[a:b]) for a, b in zip(cuts[:-1], cuts[1:])]

def vt_extrap(vg, idd):
    gm = np.gradient(idd, vg)
    i = int(np.argmax(gm))
    return vg[i] - idd[i] / gm[i] - 0.05 / 2   # VDS = 50 mV

def do_vtc(R, warn):
    lines = read_log("02_inv_vtc")
    blocks, cur = [], None
    for ln in lines:
        m = re.match(r'^\s*KBLOCK\s+(' + NUM + ')', ln)
        if m:
            cur = {"k": float(m.group(1))}; blocks.append(cur); continue
        if cur is not None:
            mm = LINE.match(ln)
            if mm and mm.group(1).lower() in ("vm", "vil", "vih", "voh", "vol"):
                cur[mm.group(1).lower()] = float(mm.group(2))
    for b in blocks:
        if all(k in b for k in ("vil", "vol")): b["nml"] = b["vil"] - b["vol"]
        if all(k in b for k in ("voh", "vih")): b["nmh"] = b["voh"] - b["vih"]
    R["vtc"] = blocks
    if not blocks:
        warn.append("Khong doc duoc ket qua VTC trong logs/02_inv_vtc.log"); return
    good = [b for b in blocks if "vm" in b]
    best = min(good, key=lambda b: abs(b["vm"] - VDD / 2))
    R["k"] = best["k"]
    p = D("sim", "params.spice"); s = open(p).read()
    s = re.sub(r'\bk=' + NUM, "k=%g" % best["k"], s)
    open(p, "w").write(s)
    if abs(best["vm"] - VDD/2) > 0.1:
        warn.append("VM tot nhat = %.3f V, lech > 0.1 V so voi VDD/2: can mo rong dai quet k" % best["vm"])
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    for b in blocks:
        h, a = read_data("vtc_k%g.txt" % b["k"])
        if a is None:
            h, a = read_data("vtc_k%s.txt" % str(b["k"]).rstrip("0").rstrip("."))
        if a is not None:
            ax.plot(a[:, 0], a[:, 1], lw=2.2 if b is best else 1.2, label="k = %g" % b["k"])
    ax.plot([0, VDD], [0, VDD], "--", color=GREY, lw=1)
    ax.set_xlabel("Vin (V)"); ax.set_ylabel("Vout (V)"); P = params(); ax.set_title("VTC inverter, sky130, L = %g µm" % P["l"])
    ax.legend(); fig.tight_layout(); fig.savefig(D("figs", "vtc.png")); plt.close(fig)

def do_iv(R, warn):
    v = parse_vals(read_log("01_iv"))
    iv = {"idsat_n": v.get("idsat_n"), "idsat_p": v.get("idsat_p")}
    fig, axs = plt.subplots(2, 1, figsize=(5.0, 6.2))
    for ax, nm, col, lab in [(axs[0], "nmos_idvds.txt", BLUE, "NMOS"), (axs[0], "pmos_idvds.txt", RED, "PMOS")]:
        h, a = read_data(nm)
        if a is None: warn.append("Thieu data/" + nm); continue
        for j, (x, y) in enumerate(split_sweeps(a[:, 0], a[:, 1])):
            ax.plot(x, y * 1e6, color=col, lw=1.2, label=lab if j == len(split_sweeps(a[:, 0], a[:, 1])) - 1 else None)
    axs[0].set_xlabel("|VDS| (V)"); axs[0].set_ylabel("|ID| (µA)"); axs[0].set_title("ID–VDS, |VGS| = 0…1.8 V"); axs[0].legend()
    for nm, col, lab, key in [("nmos_idvgs.txt", BLUE, "NMOS", "vtn"), ("pmos_idvgs.txt", RED, "PMOS", "vtp")]:
        h, a = read_data(nm)
        if a is None: warn.append("Thieu data/" + nm); continue
        axs[1].plot(a[:, 0], a[:, 1] * 1e6, color=col, label=lab)
        iv[key] = float(vt_extrap(a[:, 0], a[:, 1]))
    axs[1].set_xlabel("|VGS| (V)"); axs[1].set_ylabel("|ID| (µA)"); axs[1].set_title("ID–VGS, |VDS| = 50 mV"); axs[1].legend()
    P = params(); m = re.search(r"^\.temp\s+(" + NUM + ")", open(D("sim", "01_iv.spice")).read(), re.M | re.I)
    fig.suptitle("W/L = %g/%g µm, sky130 tt, %s °C" % (P["wn"], P["l"], m.group(1) if m else "?"), fontsize=10); fig.tight_layout(); fig.savefig(D("figs", "iv.png")); plt.close(fig)
    if iv["idsat_n"] and iv["idsat_p"]:
        iv["ratio"] = iv["idsat_n"] / iv["idsat_p"]
    R["iv"] = iv

def wave(name, sigs, title):
    h, a = read_data(name)
    if a is None: return False
    fig, axs = plt.subplots(len(sigs), 1, figsize=(5.0, 1.15 * len(sigs) + 0.9), sharex=True)
    cols = [GREY, GREY, BLUE, RED]
    for i, (ax, s) in enumerate(zip(axs, sigs)):
        ax.plot(a[:, 0] * 1e9, a[:, i + 1], color=cols[i] if len(sigs) == 4 else ([GREY, GREY, RED][i]), lw=1.4)
        ax.set_ylabel(s, rotation=0, labelpad=22); ax.set_ylim(-0.2, 2.0); ax.set_yticks([0, 1.8])
    axs[-1].set_xlabel("t (ns)"); axs[0].set_title(title); fig.tight_layout()
    fig.savefig(D("figs", name.replace(".txt", ".png"))); plt.close(fig)
    return True

def do_tran(R, warn):
    a = parse_vals(read_log("03_and")); cl = "CL = %g fF" % (params()["cl"] * 1e15)
    R["and"] = a
    if not wave("wave_and.txt", ["A", "B", "Y"], "Cổng AND (NAND2 + INV), " + cl): warn.append("Thieu data/wave_and.txt")
    for key, log, wn, ttl in [("ha14", "04_ha14", "wave_ha14.txt", "Half Adder 14T"), ("ha18", "05_ha18", "wave_ha18.txt", "Half Adder 18T")]:
        R[key] = parse_vals(read_log(log))
        if not wave(wn, ["A", "B", "Carry", "Sum"], ttl + ", " + cl): warn.append("Thieu data/" + wn)
    need = {"and": ["tplh", "tphl", "tr", "tf", "voh", "vol", "pavg", "pstatic"],
            "ha14": ["tplh_c", "tphl_c", "tplh_s", "tphl_s", "pavg", "voh_s", "vol_s"],
            "ha18": ["tplh_c", "tphl_c", "tplh_s", "tphl_s", "pavg"]}
    for c, ks in need.items():
        for k in ks:
            if k not in R[c]: warn.append("Thieu ket qua '%s' trong log cua %s (meas that bai?)" % (k, c))
    for c, pre in [("and", ""), ("ha14", "_s"), ("ha14", "_c")]:
        voh, vol = R[c].get("voh" + pre), R[c].get("vol" + pre)
        if voh is not None and voh < 0.95 * VDD: warn.append("%s: VOH%s = %.3f V < 95%% VDD (khong full swing?)" % (c, pre, voh))
        if vol is not None and vol > 0.05 * VDD: warn.append("%s: VOL%s = %.3f V > 5%% VDD" % (c, pre, vol))
    for c in ("and", "ha14", "ha18"):
        for k, v in R[c].items():
            if k.startswith("tp") and (v <= 0 or v > 2e-9):
                warn.append("%s: %s = %.3g s ngoai khoang hop ly (0, 2 ns]: kiem tra lai menh de meas" % (c, k, v))
        d = R[c]
        if "tplh_s" in d and "tphl_s" in d:
            d["tpmax_s"] = max(d["tplh_s"], d["tphl_s"]); d["tpmax_c"] = max(d.get("tplh_c", 0), d.get("tphl_c", 0))
            d["tpmax"] = max(d["tpmax_s"], d["tpmax_c"])
        if "tplh" in d and "tphl" in d: d["tpmax"] = max(d["tplh"], d["tphl"])
        if "pavg" in d and "tpmax" in d: d["pdp"] = d["pavg"] * d["tpmax"]

def do_setup(R, warn):
    """Thong so thiet ke va testbench lay tu netlist (params.spice, nguon PULSE va .temp cua 03_and.spice)"""
    st = dict(params())
    tb = open(D("sim", "03_and.spice")).read()
    for nm in ("VA", "VB"):
        m = re.search(r'^' + nm + r'\s.*PULSE\(([^)]*)\)', tb, re.M)
        if m:
            p = m.group(1).split()   # V1 V2 TD TR TF PW PER
            st[nm.lower() + "_per"] = si(p[6]); st["src_tr"] = si(p[3]); st["src_tf"] = si(p[4])
            st[nm.lower() + "_freq"] = 1 / st[nm.lower() + "_per"]
    m = re.search(r'^\.temp\s+(' + NUM + ')', tb, re.M | re.I)
    if m: st["temp"] = float(m.group(1))
    R["setup"] = st

def do_func(R, warn):
    """Kiem tra bang chan ly va glitch tu data/wave_*.txt.
       Trang thai doi moi 1 ns: 00, 10, 01, 11. Tai 2 ns va 4 ns A, B doi cung luc."""
    spec = [("and", "wave_and.txt", {"v(y)": lambda a, b: a and b}),
            ("ha14", "wave_ha14.txt", {"v(carry)": lambda a, b: a and b, "v(sum)": lambda a, b: a != b}),
            ("ha18", "wave_ha18.txt", {"v(carry)": lambda a, b: a and b, "v(sum)": lambda a, b: a != b})]
    for c, fn, outs in spec:
        h, a = read_data(fn)
        if a is None: continue
        t = a[:, 0]; col = {n: a[:, i] for i, n in enumerate(h)}
        at = lambda n, tt: col[n][min(np.searchsorted(t, tt), len(t) - 1)]
        ok = True
        for k in range(8):                      # cuoi moi khoang 1 ns, 2 chu ky
            tt = (k + 0.9) * 1e-9
            A, B = at("v(a)", tt) > VDD / 2, at("v(b)", tt) > VDD / 2
            for o, f in outs.items():
                if (at(o, tt) > VDD / 2) != bool(f(A, B)):
                    ok = False; warn.append("%s: %s sai bang chan ly tai t = %.1f ns (A=%d, B=%d)" % (c, o, tt * 1e9, A, B))
        R[c]["func_ok"] = ok
        for o in outs:
            dev = 0.0                           # lech lon nhat khi dau ra dung ra phai dung yen
            for tc in (2e-9, 4e-9, 6e-9, 8e-9):
                v0, v1 = at(o, tc - 0.1e-9), at(o, tc + 0.9e-9)
                if (v0 > VDD / 2) != (v1 > VDD / 2): continue
                w = col[o][(t >= tc) & (t <= tc + 0.6e-9)]
                dev = max(dev, float(np.max(np.abs(w - v0))))
            R[c]["glitch_" + o[2:-1]] = dev

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--all"
    os.makedirs(D("figs"), exist_ok=True)
    rp = D("results.json")
    R = json.load(open(rp)) if os.path.exists(rp) else {}
    warn = []
    do_vtc(R, warn)
    if mode == "--all":
        do_iv(R, warn); do_tran(R, warn); do_setup(R, warn); do_func(R, warn)
    R["warnings"] = warn
    json.dump(R, open(rp, "w"), indent=2, ensure_ascii=False)
    rep = ["# Bao cao kiem tra mo phong", ""]
    rep += ["- " + w for w in warn] if warn else ["- Khong phat hien van de nao."]
    open(D("logs", "check_report.md"), "w").write("\n".join(rep) + "\n")
    print("\n".join(rep)); print("k da chon:", R.get("k"))

if __name__ == "__main__":
    main()
