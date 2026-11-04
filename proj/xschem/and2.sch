v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 0 -60 0 -40 {lab=vdd}
N 0 40 0 60 {lab=gnd}
N 160 -60 160 -40 {lab=vdd}
N 160 40 160 60 {lab=gnd}
N 60 0 110 0 {lab=nab}
N -140 -10 -60 -10 {lab=a}
N -140 10 -60 10 {lab=b}
N 210 0 290 0 {lab=y}
C {ipin.sym} -140 -10 0 0 {name=p5 lab=a}
C {ipin.sym} -140 10 0 0 {name=p6 lab=b}
C {opin.sym} 290 0 0 0 {name=p7 lab=y}
C {iopin.sym} -140 120 0 0 {name=p8 lab=vdd}
C {iopin.sym} -140 150 0 0 {name=p9 lab=gnd}
C {nand2.sym} 0 0 0 0 {name=X1}
C {inv.sym} 160 0 0 0 {name=X2}
C {lab_pin.sym} 0 -60 0 0 {name=l1 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 0 60 0 0 {name=l2 sig_type=std_logic lab=gnd}
C {lab_pin.sym} 160 -60 0 0 {name=l3 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 160 60 0 0 {name=l4 sig_type=std_logic lab=gnd}
T {nab} 72 -20 0 0 0.25 0.25 {}
T {AND2 = NAND2 + INV   (k = 3, Wn = 1u, L = 0.15u)} -140 -120 0 0 0.4 0.4 {}
