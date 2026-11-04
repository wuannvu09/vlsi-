#!/usr/bin/env python3
"""Sinh schematic Xschem (inv, nand2, oai21, and2, ha14) khop voi sim/cells_sky130.spice.

Kich thuoc lay tu results.json (setup.k, setup.wn, setup.l). Thu tu transistor theo Euler path
o slide 14 (NAND2: A -> B; OAI21: nAB -> A -> B). Chay lai sau khi doi k:
    python3 xschem/gen_sch.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SETUP = json.load(open(os.path.join(ROOT, "results.json")))["setup"]
K, WN, L = SETUP["k"], SETUP["wn"], SETUP["l"]
HEADER = "v {xschem version=3.4.4 file_version=1.2}\nG {}\nK {}\nV {}\nS {}\nE {}\n"


def fmt(v):
    return f"{v:g}"


class Sch:
    """Gom dau day, instance; tach day o moi diem noi chu T truoc khi ghi file."""

    def __init__(self, title):
        self.title = title
        self.wires = []   # (x1, y1, x2, y2, lab)
        self.insts = []   # dong 'C {...}'
        self.points = set()
        self.n = 0
        self.box = [1e9, 1e9, -1e9, -1e9]  # khung xuat anh (Xschem khong tinh chu khi zoom_full)

    def grow(self, x1, y1, x2, y2):
        b = self.box
        self.box = [min(b[0], x1), min(b[1], y1), max(b[2], x2), max(b[3], y2)]

    def _id(self, p):
        self.n += 1
        return f"{p}{self.n}"

    def wire(self, *pts, lab=None):
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            assert x1 == x2 or y1 == y2, "chi ve day ngang/doc"
            self.wires.append((x1, y1, x2, y2, lab))
            self.points |= {(x1, y1), (x2, y2)}
            self.grow(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))

    def inst(self, sym, x, y, props, rot=0, flip=0, pins=()):
        self.insts.append(f"C {{{sym}}} {x} {y} {rot} {flip} {{{props}}}")
        self.points |= set(pins)
        if sym.startswith("sky130_fd_pr/"):
            self.grow(x - 40, y - 45, x + 130, y + 45)        # chu model, W/L ben phai transistor
        else:
            for px, py in pins or [(x, y)]:
                self.grow(px - 60, py - 30, px + 90, py + 30)  # chu nhan/pin

    def label(self, x, y, lab, right=False):
        self.inst("lab_pin.sym", x, y, f"name={self._id('l')} sig_type=std_logic lab={lab}",
                  flip=1 if right else 0, pins=[(x, y)])

    def pin(self, kind, x, y, lab, flip=0):
        self.inst(f"{kind}.sym", x, y, f"name={self._id('p')} lab={lab}", flip=flip, pins=[(x, y)])

    def fet(self, kind, name, x, y, w, g, top, bot, body):
        """kind = nfet/pfet, symbol 3 chan cua PDK: than (body) noi qua thuoc tinh body= (vdd/gnd),
        Xschem dua vao netlist nen LVS van kiem tra. Chan (khong xoay): G(x-20,y), tren(x+20,y-30),
        duoi(x+20,y+30); nfet: tren = D, duoi = S; pfet: tren = S, duoi = D."""
        self.inst(f"sky130_fd_pr/{kind}3_01v8.sym", x, y,
                  f"name={name}\nL={fmt(L)}\nW={fmt(w)}\nbody={body}\nnf=1\nmult=1\nmodel={kind}_01v8\nspiceprefix=X",
                  pins=[(x - 20, y), (x + 20, y - 30), (x + 20, y + 30)])
        if g:
            self.wire((x - 20, y), (x - 40, y), lab=g)
            self.label(x - 40, y, g)
        return {"g": (x - 20, y), "t": (x + 20, y - 30), "b": (x + 20, y + 30)}

    def text(self, s, x, y, size=0.4):
        self.insts.append(f"T {{{s}}} {x} {y} 0 0 {size} {size} {{}}")
        self.grow(x, y - 5, x + 20 * size * len(s), y + 60 * size)

    def _split(self):
        out = []
        for x1, y1, x2, y2, lab in self.wires:
            if x1 == x2:
                lo, hi = sorted((y1, y2))
                cuts = sorted({y for (x, y) in self.points if x == x1 and lo < y < hi})
                ys = [lo] + cuts + [hi]
                out += [(x1, a, x1, b, lab) for a, b in zip(ys, ys[1:])]
            else:
                lo, hi = sorted((x1, x2))
                cuts = sorted({x for (x, y) in self.points if y == y1 and lo < x < hi})
                xs = [lo] + cuts + [hi]
                out += [(a, y1, b, y1, lab) for a, b in zip(xs, xs[1:])]
        return out

    def save(self, fname, ports):
        """ports: thu tu cong cua subckt (Xschem lay thu tu cong top-level theo thu tu pin trong file)."""
        lines = [HEADER.rstrip("\n")]
        for x1, y1, x2, y2, lab in self._split():
            lines.append(f"N {x1} {y1} {x2} {y2} {{lab={lab}}}" if lab else f"N {x1} {y1} {x2} {y2} {{}}")
        is_pin = lambda c: c.startswith(("C {ipin.sym}", "C {opin.sym}", "C {iopin.sym}"))
        pins = [c for c in self.insts if is_pin(c)]
        pins.sort(key=lambda c: ports.index(c.rsplit("lab=", 1)[1].rstrip("}")))
        assert len(pins) == len(ports), (fname, pins)
        lines += pins + [c for c in self.insts if not is_pin(c)]
        with open(os.path.join(HERE, fname), "w") as f:
            f.write("\n".join(lines) + "\n")
        bfile = os.path.join(HERE, "bbox.json")
        boxes = json.load(open(bfile)) if os.path.exists(bfile) else {}
        m = 20
        boxes[fname[:-4]] = [self.box[0] - m, self.box[1] - m, self.box[2] + m, self.box[3] + m]
        json.dump(boxes, open(bfile, "w"), indent=1)


def sym_file(fname, pins, body, symname):
    """pins: [(name, dir, x, y)] theo dung thu tu cong cua subckt trong cells_sky130.spice."""
    lines = ["v {xschem version=3.4.4 file_version=1.2}",
             'K {type=subcircuit\nformat="@name @pinlist @symname"\ntemplate="name=x1"\n}',
             "G {}", "V {}", "S {}", "E {}"]
    for name, d, x, y in pins:
        lines.append(f"B 5 {x - 2.5} {y - 2.5} {x + 2.5} {y + 2.5} {{name={name} dir={d}}}")
    lines += body
    lines.append("T {@name} -20 -48 0 0 0.2 0.2 {}")
    with open(os.path.join(HERE, fname), "w") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- transistor-level cells
def make_inv():
    s = Sch("INV")
    p = s.fet("pfet", "MP", 0, -100, K * WN, None, None, None, "vdd")
    n = s.fet("nfet", "MN", 0, 0, WN, None, None, None, "gnd")
    s.wire(p["t"], (20, -160), (-20, -160), lab="vdd"); s.label(-20, -160, "vdd")
    s.wire(n["b"], (20, 60), (-20, 60), lab="gnd"); s.label(-20, 60, "gnd")
    s.wire(p["b"], (20, -50), n["t"], lab="out")
    s.wire((20, -50), (100, -50), lab="out"); s.pin("opin", 100, -50, "out")
    s.wire(p["g"], (-40, -100), (-40, 0), n["g"], lab="in")
    s.wire((-100, -50), (-40, -50), lab="in"); s.pin("ipin", -100, -50, "in")
    s.pin("iopin", -100, -180, "vdd")
    s.pin("iopin", -100, 80, "gnd")
    s.text(f"INV: Wp = k*Wn = {fmt(K * WN)}u, Wn = {fmt(WN)}u, L = {fmt(L)}u", -100, -240)
    s.save("inv.sch", ["in", "out", "vdd", "gnd"])


def make_nand2():
    s = Sch("NAND2")
    pa = s.fet("pfet", "MPA", 0, -100, K * WN, "a", None, None, "vdd")
    pb = s.fet("pfet", "MPB", 140, -100, K * WN, "b", None, None, "vdd")
    na = s.fet("nfet", "MNA", 0, 20, 2 * WN, "a", None, None, "gnd")   # sat dau ra (Euler A -> B)
    nb = s.fet("nfet", "MNB", 0, 110, 2 * WN, "b", None, None, "gnd")
    s.wire(pa["t"], (20, -150), (160, -150), pb["t"], lab="vdd")
    s.wire((20, -150), (-20, -150), lab="vdd"); s.label(-20, -150, "vdd")
    s.wire(pa["b"], (20, -40), na["t"], lab="y")
    s.wire(pb["b"], (160, -40), (20, -40), lab="y")
    s.wire((160, -40), (240, -40), lab="y"); s.pin("opin", 240, -40, "y")
    s.wire(na["b"], nb["t"])                                           # nut n1
    s.wire(nb["b"], (20, 170), (-20, 170), lab="gnd"); s.label(-20, 170, "gnd")
    for i, (nm, kind) in enumerate([("a", "ipin"), ("b", "ipin"), ("vdd", "iopin"), ("gnd", "iopin")]):
        y = -200 + 30 * i
        s.pin(kind, -180, y, nm)
    s.text(f"NAND2: PMOS // {fmt(K * WN)}u, NMOS noi tiep {fmt(2 * WN)}u (Euler A -> B)", -180, -280)
    s.save("nand2.sch", ["a", "b", "y", "vdd", "gnd"])


def make_oai21():
    s = Sch("OAI21")
    pc = s.fet("pfet", "MPC", 0, -120, K * WN, "c", None, None, "vdd")
    pa = s.fet("pfet", "MPA", 140, -160, 2 * K * WN, "a", None, None, "vdd")
    pb = s.fet("pfet", "MPB", 140, -80, 2 * K * WN, "b", None, None, "vdd")
    nc = s.fet("nfet", "MNC", 0, 30, 2 * WN, "c", None, None, "gnd")   # nAB sat dau ra
    na = s.fet("nfet", "MNA", 0, 110, 2 * WN, "a", None, None, "gnd")
    nb = s.fet("nfet", "MNB", 140, 110, 2 * WN, "b", None, None, "gnd")
    s.wire(pc["t"], (20, -210), (160, -210), pa["t"], lab="vdd")
    s.wire((20, -210), (-20, -210), lab="vdd"); s.label(-20, -210, "vdd")
    s.wire(pa["b"], pb["t"])                                           # nut p1
    s.wire(pc["b"], (20, -20), nc["t"], lab="y")
    s.wire(pb["b"], (160, -20), (20, -20), lab="y")
    s.wire((160, -20), (260, -20), lab="y"); s.pin("opin", 260, -20, "y")
    s.wire(nc["b"], (20, 75), (160, 75), nb["t"])                      # nut n1 (cuc D chung A // B)
    s.wire((20, 75), na["t"])
    s.wire(na["b"], (20, 170), (160, 170), nb["b"], lab="gnd")
    s.wire((20, 170), (-20, 170), lab="gnd"); s.label(-20, 170, "gnd")
    for i, (nm, kind) in enumerate([("a", "ipin"), ("b", "ipin"), ("c", "ipin"), ("vdd", "iopin"), ("gnd", "iopin")]):
        y = -250 + 30 * i
        s.pin(kind, -200, y, nm)
    s.text(f"OAI21: Y = ((a+b)c)'  PMOS A,B {fmt(2 * K * WN)}u, C {fmt(K * WN)}u; NMOS {fmt(2 * WN)}u (Euler nAB -> A -> B)",
           -200, -330, 0.35)
    s.save("oai21.sch", ["a", "b", "c", "y", "vdd", "gnd"])


# ---------------------------------------------------------------- symbols
def make_syms():
    rail = [("vdd", "inout", 0, -40), ("gnd", "inout", 0, 40)]
    sym_file("inv.sym", [("in", "in", -50, 0), ("out", "out", 50, 0)] + rail, [
        "P 4 4 -20 -20 -20 20 14 0 -20 -20 {}", "A 4 17 0 3 0 360 {}",
        "L 4 -50 0 -20 0 {}", "L 4 20 0 50 0 {}", "L 4 0 -40 0 -9 {}", "L 4 0 9 0 40 {}",
        "T {in} -46 -14 0 0 0.15 0.15 {}", "T {out} 46 -14 0 1 0.15 0.15 {}",
        "T {@symname} 22 10 0 0 0.2 0.2 {}"], "inv")
    sym_file("nand2.sym", [("a", "in", -60, -10), ("b", "in", -60, 10), ("y", "out", 60, 0)] + rail, [
        "L 4 -30 -20 0 -20 {}", "L 4 -30 20 0 20 {}", "L 4 -30 -20 -30 20 {}", "A 4 0 0 20 270 180 {}",
        "A 4 23 0 3 0 360 {}", "L 4 26 0 60 0 {}", "L 4 -60 -10 -30 -10 {}", "L 4 -60 10 -30 10 {}",
        "L 4 0 -40 0 -20 {}", "L 4 0 20 0 40 {}",
        "T {a} -56 -24 0 0 0.15 0.15 {}", "T {b} -56 -4 0 0 0.15 0.15 {}", "T {y} 56 -14 0 1 0.15 0.15 {}",
        "T {@symname} 26 10 0 0 0.2 0.2 {}"], "nand2")
    sym_file("oai21.sym", [("a", "in", -70, -20), ("b", "in", -70, 0), ("c", "in", -70, 20),
                           ("y", "out", 70, 0)] + [("vdd", "inout", 0, -50), ("gnd", "inout", 0, 50)], [
        "L 4 -40 -30 40 -30 {}", "L 4 -40 30 40 30 {}", "L 4 -40 -30 -40 30 {}", "L 4 40 -30 40 30 {}",
        "A 4 43 0 3 0 360 {}", "L 4 46 0 70 0 {}",
        "L 4 -70 -20 -40 -20 {}", "L 4 -70 0 -40 0 {}", "L 4 -70 20 -40 20 {}",
        "L 4 0 -50 0 -30 {}", "L 4 0 30 0 50 {}",
        "T {a} -36 -26 0 0 0.15 0.15 {}", "T {b} -36 -6 0 0 0.15 0.15 {}", "T {c} -36 14 0 0 0.15 0.15 {}",
        "T {y} 66 -14 0 1 0.15 0.15 {}", "T {OAI21} -22 -10 0 0 0.25 0.25 {}"], "oai21")


def rails(s, x, y_top, y_bot, d_top=20, d_bot=20):
    s.wire((x, y_top), (x, y_top - d_top), lab="vdd"); s.label(x, y_top - d_top, "vdd")
    s.wire((x, y_bot), (x, y_bot + d_bot), lab="gnd"); s.label(x, y_bot + d_bot, "gnd")


def make_and2():
    s = Sch("AND2")
    s.inst("nand2.sym", 0, 0, "name=X1", pins=[(-60, -10), (-60, 10), (60, 0), (0, -40), (0, 40)])
    s.inst("inv.sym", 160, 0, "name=X2", pins=[(110, 0), (210, 0), (160, -40), (160, 40)])
    rails(s, 0, -40, 40); rails(s, 160, -40, 40)
    s.wire((60, 0), (110, 0), lab="nab"); s.text("nab", 72, -20, 0.25)
    s.pin("ipin", -140, -10, "a"); s.wire((-140, -10), (-60, -10), lab="a")
    s.pin("ipin", -140, 10, "b"); s.wire((-140, 10), (-60, 10), lab="b")
    s.pin("opin", 290, 0, "y"); s.wire((210, 0), (290, 0), lab="y")
    for i, nm in enumerate(["vdd", "gnd"]):
        y = 120 + 30 * i
        s.pin("iopin", -140, y, nm)
    s.text(f"AND2 = NAND2 + INV   (k = {fmt(K)}, Wn = {fmt(WN)}u, L = {fmt(L)}u)", -140, -120)
    s.save("and2.sch", ["a", "b", "y", "vdd", "gnd"])


def make_ha14():
    s = Sch("HA14")
    s.inst("nand2.sym", 0, -120, "name=X1", pins=[(-60, -130), (-60, -110), (60, -120), (0, -160), (0, -80)])
    s.inst("inv.sym", 200, -120, "name=X2", pins=[(150, -120), (250, -120), (200, -160), (200, -80)])
    s.inst("oai21.sym", 200, 60, "name=X3", pins=[(130, 40), (130, 60), (130, 80), (270, 60), (200, 10), (200, 110)])
    s.inst("inv.sym", 360, 60, "name=X4", pins=[(310, 60), (410, 60), (360, 20), (360, 100)])
    rails(s, 0, -160, -80); rails(s, 200, -160, -80); rails(s, 200, 10, 110); rails(s, 360, 20, 100)
    s.pin("ipin", -160, -130, "a"); s.wire((-160, -130), (-60, -130), lab="a")
    s.pin("ipin", -160, -110, "b"); s.wire((-160, -110), (-60, -110), lab="b")
    s.wire((-100, -130), (-100, 40), (130, 40), lab="a")     # a -> OAI21.a
    s.wire((-80, -110), (-80, 60), (130, 60), lab="b")       # b -> OAI21.b
    s.wire((60, -120), (150, -120), lab="nab")
    s.wire((100, -120), (100, 80), (130, 80), lab="nab")     # nAB -> OAI21.c
    s.text("nab", 110, -140, 0.25)
    s.wire((270, 60), (310, 60), lab="xnor"); s.text("xnor", 275, 40, 0.25)
    s.pin("opin", 480, -120, "carry"); s.wire((250, -120), (480, -120), lab="carry")
    s.pin("opin", 480, 60, "sum"); s.wire((410, 60), (480, 60), lab="sum")
    for i, nm in enumerate(["vdd", "gnd"]):
        y = 200 + 30 * i
        s.pin("iopin", -160, y, nm)
    s.text(f"Half Adder 14T: Carry = AB, Sum = (A+B)(AB)' = A xor B   (k = {fmt(K)}, Wn = {fmt(WN)}u)", -160, -240)
    s.save("ha14.sch", ["a", "b", "sum", "carry", "vdd", "gnd"])


if __name__ == "__main__":
    make_syms()
    make_inv(); make_nand2(); make_oai21(); make_and2(); make_ha14()
    print("Da sinh:", sorted(f for f in os.listdir(HERE) if f.endswith((".sch", ".sym"))))
