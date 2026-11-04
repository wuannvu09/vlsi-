v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 0 -180 0 -160 {lab=vdd}
N 0 -80 0 -60 {lab=gnd}
N 200 -180 200 -160 {lab=vdd}
N 200 -80 200 -60 {lab=gnd}
N 200 -10 200 10 {lab=vdd}
N 200 110 200 130 {lab=gnd}
N 360 0 360 20 {lab=vdd}
N 360 100 360 120 {lab=gnd}
N -160 -130 -100 -130 {lab=a}
N -100 -130 -60 -130 {lab=a}
N -160 -110 -80 -110 {lab=b}
N -80 -110 -60 -110 {lab=b}
N -100 -130 -100 40 {lab=a}
N -100 40 130 40 {lab=a}
N -80 -110 -80 60 {lab=b}
N -80 60 130 60 {lab=b}
N 60 -120 100 -120 {lab=nab}
N 100 -120 150 -120 {lab=nab}
N 100 -120 100 80 {lab=nab}
N 100 80 130 80 {lab=nab}
N 270 60 310 60 {lab=xnor}
N 250 -120 480 -120 {lab=carry}
N 410 60 480 60 {lab=sum}
C {ipin.sym} -160 -130 0 0 {name=p9 lab=a}
C {ipin.sym} -160 -110 0 0 {name=p10 lab=b}
C {opin.sym} 480 60 0 0 {name=p12 lab=sum}
C {opin.sym} 480 -120 0 0 {name=p11 lab=carry}
C {iopin.sym} -160 200 0 0 {name=p13 lab=vdd}
C {iopin.sym} -160 230 0 0 {name=p14 lab=gnd}
C {nand2.sym} 0 -120 0 0 {name=X1}
C {inv.sym} 200 -120 0 0 {name=X2}
C {oai21.sym} 200 60 0 0 {name=X3}
C {inv.sym} 360 60 0 0 {name=X4}
C {lab_pin.sym} 0 -180 0 0 {name=l1 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 0 -60 0 0 {name=l2 sig_type=std_logic lab=gnd}
C {lab_pin.sym} 200 -180 0 0 {name=l3 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 200 -60 0 0 {name=l4 sig_type=std_logic lab=gnd}
C {lab_pin.sym} 200 -10 0 0 {name=l5 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 200 130 0 0 {name=l6 sig_type=std_logic lab=gnd}
C {lab_pin.sym} 360 0 0 0 {name=l7 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 360 120 0 0 {name=l8 sig_type=std_logic lab=gnd}
T {nab} 110 -140 0 0 0.25 0.25 {}
T {xnor} 275 40 0 0 0.25 0.25 {}
T {Half Adder 14T: Carry = AB, Sum = (A+B)(AB)' = A xor B   (k = 3, Wn = 1u)} -160 -240 0 0 0.4 0.4 {}
