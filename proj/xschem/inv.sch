v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 20 -160 20 -130 {lab=vdd}
N -20 -160 20 -160 {lab=vdd}
N 20 30 20 60 {lab=gnd}
N -20 60 20 60 {lab=gnd}
N 20 -70 20 -50 {lab=out}
N 20 -50 20 -30 {lab=out}
N 20 -50 100 -50 {lab=out}
N -40 -100 -20 -100 {lab=in}
N -40 -100 -40 -50 {lab=in}
N -40 -50 -40 0 {lab=in}
N -40 0 -20 0 {lab=in}
N -100 -50 -40 -50 {lab=in}
C {ipin.sym} -100 -50 0 0 {name=p4 lab=in}
C {opin.sym} 100 -50 0 0 {name=p3 lab=out}
C {iopin.sym} -100 -180 0 0 {name=p5 lab=vdd}
C {iopin.sym} -100 80 0 0 {name=p6 lab=gnd}
C {sky130_fd_pr/pfet3_01v8.sym} 0 -100 0 0 {name=MP
L=0.15
W=3
body=vdd
nf=1
mult=1
model=pfet_01v8
spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 0 0 0 0 {name=MN
L=0.15
W=1
body=gnd
nf=1
mult=1
model=nfet_01v8
spiceprefix=X}
C {lab_pin.sym} -20 -160 0 0 {name=l1 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -20 60 0 0 {name=l2 sig_type=std_logic lab=gnd}
T {INV: Wp = k*Wn = 3u, Wn = 1u, L = 0.15u} -100 -240 0 0 0.4 0.4 {}
