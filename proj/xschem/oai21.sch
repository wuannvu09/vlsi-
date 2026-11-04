v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N -40 -120 -20 -120 {lab=c}
N 100 -160 120 -160 {lab=a}
N 100 -80 120 -80 {lab=b}
N -40 30 -20 30 {lab=c}
N -40 110 -20 110 {lab=a}
N 100 110 120 110 {lab=b}
N 20 -210 20 -150 {lab=vdd}
N 20 -210 160 -210 {lab=vdd}
N 160 -210 160 -190 {lab=vdd}
N -20 -210 20 -210 {lab=vdd}
N 160 -130 160 -110 {}
N 20 -90 20 -20 {lab=y}
N 20 -20 20 0 {lab=y}
N 160 -50 160 -20 {lab=y}
N 20 -20 160 -20 {lab=y}
N 160 -20 260 -20 {lab=y}
N 20 60 20 75 {}
N 20 75 160 75 {}
N 160 75 160 80 {}
N 20 75 20 80 {}
N 20 140 20 170 {lab=gnd}
N 20 170 160 170 {lab=gnd}
N 160 140 160 170 {lab=gnd}
N -20 170 20 170 {lab=gnd}
C {ipin.sym} -200 -250 0 0 {name=p10 lab=a}
C {ipin.sym} -200 -220 0 0 {name=p11 lab=b}
C {ipin.sym} -200 -190 0 0 {name=p12 lab=c}
C {opin.sym} 260 -20 0 0 {name=p8 lab=y}
C {iopin.sym} -200 -160 0 0 {name=p13 lab=vdd}
C {iopin.sym} -200 -130 0 0 {name=p14 lab=gnd}
C {sky130_fd_pr/pfet3_01v8.sym} 0 -120 0 0 {name=MPC
L=0.15
W=3
body=vdd
nf=1
mult=1
model=pfet_01v8
spiceprefix=X}
C {lab_pin.sym} -40 -120 0 0 {name=l1 sig_type=std_logic lab=c}
C {sky130_fd_pr/pfet3_01v8.sym} 140 -160 0 0 {name=MPA
L=0.15
W=6
body=vdd
nf=1
mult=1
model=pfet_01v8
spiceprefix=X}
C {lab_pin.sym} 100 -160 0 0 {name=l2 sig_type=std_logic lab=a}
C {sky130_fd_pr/pfet3_01v8.sym} 140 -80 0 0 {name=MPB
L=0.15
W=6
body=vdd
nf=1
mult=1
model=pfet_01v8
spiceprefix=X}
C {lab_pin.sym} 100 -80 0 0 {name=l3 sig_type=std_logic lab=b}
C {sky130_fd_pr/nfet3_01v8.sym} 0 30 0 0 {name=MNC
L=0.15
W=2
body=gnd
nf=1
mult=1
model=nfet_01v8
spiceprefix=X}
C {lab_pin.sym} -40 30 0 0 {name=l4 sig_type=std_logic lab=c}
C {sky130_fd_pr/nfet3_01v8.sym} 0 110 0 0 {name=MNA
L=0.15
W=2
body=gnd
nf=1
mult=1
model=nfet_01v8
spiceprefix=X}
C {lab_pin.sym} -40 110 0 0 {name=l5 sig_type=std_logic lab=a}
C {sky130_fd_pr/nfet3_01v8.sym} 140 110 0 0 {name=MNB
L=0.15
W=2
body=gnd
nf=1
mult=1
model=nfet_01v8
spiceprefix=X}
C {lab_pin.sym} 100 110 0 0 {name=l6 sig_type=std_logic lab=b}
C {lab_pin.sym} -20 -210 0 0 {name=l7 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -20 170 0 0 {name=l9 sig_type=std_logic lab=gnd}
T {OAI21: Y = ((a+b)c)'  PMOS A,B 6u, C 3u; NMOS 2u (Euler nAB -> A -> B)} -200 -330 0 0 0.35 0.35 {}
