v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N -40 -100 -20 -100 {lab=a}
N 100 -100 120 -100 {lab=b}
N -40 20 -20 20 {lab=a}
N -40 110 -20 110 {lab=b}
N 20 -150 20 -130 {lab=vdd}
N 20 -150 160 -150 {lab=vdd}
N 160 -150 160 -130 {lab=vdd}
N -20 -150 20 -150 {lab=vdd}
N 20 -70 20 -40 {lab=y}
N 20 -40 20 -10 {lab=y}
N 160 -70 160 -40 {lab=y}
N 20 -40 160 -40 {lab=y}
N 160 -40 240 -40 {lab=y}
N 20 50 20 80 {}
N 20 140 20 170 {lab=gnd}
N -20 170 20 170 {lab=gnd}
C {ipin.sym} -180 -200 0 0 {name=p8 lab=a}
C {ipin.sym} -180 -170 0 0 {name=p9 lab=b}
C {opin.sym} 240 -40 0 0 {name=p6 lab=y}
C {iopin.sym} -180 -140 0 0 {name=p10 lab=vdd}
C {iopin.sym} -180 -110 0 0 {name=p11 lab=gnd}
C {sky130_fd_pr/pfet3_01v8.sym} 0 -100 0 0 {name=MPA
L=0.15
W=3
body=vdd
nf=1
mult=1
model=pfet_01v8
spiceprefix=X}
C {lab_pin.sym} -40 -100 0 0 {name=l1 sig_type=std_logic lab=a}
C {sky130_fd_pr/pfet3_01v8.sym} 140 -100 0 0 {name=MPB
L=0.15
W=3
body=vdd
nf=1
mult=1
model=pfet_01v8
spiceprefix=X}
C {lab_pin.sym} 100 -100 0 0 {name=l2 sig_type=std_logic lab=b}
C {sky130_fd_pr/nfet3_01v8.sym} 0 20 0 0 {name=MNA
L=0.15
W=2
body=gnd
nf=1
mult=1
model=nfet_01v8
spiceprefix=X}
C {lab_pin.sym} -40 20 0 0 {name=l3 sig_type=std_logic lab=a}
C {sky130_fd_pr/nfet3_01v8.sym} 0 110 0 0 {name=MNB
L=0.15
W=2
body=gnd
nf=1
mult=1
model=nfet_01v8
spiceprefix=X}
C {lab_pin.sym} -40 110 0 0 {name=l4 sig_type=std_logic lab=b}
C {lab_pin.sym} -20 -150 0 0 {name=l5 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -20 170 0 0 {name=l7 sig_type=std_logic lab=gnd}
T {NAND2: PMOS // 3u, NMOS noi tiep 2u (Euler A -> B)} -180 -280 0 0 0.4 0.4 {}
