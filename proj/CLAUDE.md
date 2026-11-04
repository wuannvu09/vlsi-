# Hướng dẫn cho Claude Code: BTL VLSI giữa kỳ (cổng AND và Half Adder mức transistor)

## Mục tiêu
Hoàn thiện slide `output/BTL_VLSI_AND_HalfAdder_HUST.pptx` bằng số liệu mô phỏng THẬT, đúng đề bài `docs/de_bai.pdf`:
khảo sát PDK và VTC inverter, tối ưu Boolean, sizing và schematic, Euler path và stick diagram, mô phỏng (chức năng, delay, công suất), nhận xét.

## Quy tắc bắt buộc
- KHÔNG bịa số liệu. Mọi con số trong slide phải lấy từ `results.json` (do `scripts/analyze.py` sinh từ log ngspice).
- Chỉ sửa slide qua `slides/build_slides.py`, rồi chạy lại nó. Không sửa tay file .pptx trong `output/`.
- Lý thuyết phải dựa trên bài giảng trong `docs/lectures/`. Trích dẫn theo dạng `(ECE4740 – Lecture X / page Y)`,
  với Y là số trang PDF (mỗi trang PDF có 2 slide). Kiểm tra bằng `pdftotext` trước khi thêm trích dẫn mới.
- Giữ template HUST (`slides/template/`), khổ 4:3.

## Quy trình
1. `./setup.sh`: cài ngspice, gói Python, PDK sky130 (tự tìm PDK có sẵn, nếu không có thì tải qua volare), ghi `sim/pdk.spice`.
2. `./run_all.sh`: chạy `sim/02_inv_vtc.spice` → `analyze.py --vtc` chọn k (VM gần VDD/2 nhất, ghi vào `sim/params.spice`)
   → chạy `01_iv`, `03_and`, `04_ha14`, `05_ha18` → `analyze.py --all` → `slides/build_slides.py`.
3. Đọc `logs/check_report.md` và từng `logs/*.log`. Sửa netlist nếu có lỗi, chạy lại tới khi báo cáo sạch.
4. Kiểm tra tính hợp lý (xem mục dưới). Nếu bất thường, tìm nguyên nhân trong netlist hoặc mệnh đề `meas`, không chỉnh số.
5. Cập nhật slide 21 (Nhận xét đạt / chưa đạt) trong `build_slides.py` theo kết quả thật: bỏ các ý trong ngoặc vuông,
   ghi rõ 14T so với 18T nhanh/chậm hơn bao nhiêu ps, công suất chênh bao nhiêu %, có glitch hay không.
6. Chạy lại `python3 slides/build_slides.py`. Nếu có LibreOffice: chuyển sang PDF, xem từng trang để kiểm tra chữ tràn, đè hình.

## Tiêu chí kiểm tra số liệu
- VTC: VOH ≈ 1,8 V, VOL ≈ 0 V; VM tăng khi k tăng; NML, NMH dương.
- I–V: VT của nfet_01v8 cỡ vài trăm mV; ID,n/ID,p > 1 (PMOS yếu hơn).
- Waveform khớp bảng chân lý: AND = A·B; Carry = A·B; Sum = A XOR B. Đầu ra full swing (VOH ≥ 95% VDD, VOL ≤ 5% VDD).
- Delay dương và cỡ chục tới vài trăm ps với CL = 10 fF. Sum (3 tầng) thường chậm hơn Carry (2 tầng).
- Pavg cỡ µW tới chục µW; Pstatic nhỏ hơn Pavg nhiều bậc.
- Nếu Sum có gai ở 2 ns hoặc 4 ns (A, B đổi cùng lúc): đó là glitch (Lecture 5 / page 4), ghi vào nhận xét.

## Lỗi ngspice thường gặp
- `could not find include file`: sai đường dẫn trong `sim/pdk.spice` → chạy lại `setup.sh` hoặc sửa tay.
- `unknown subckt sky130_fd_pr__nfet_01v8`: file .lib sai corner hoặc sai thư mục (cần `.../libs.tech/ngspice/sky130.lib.spice` hoặc `.../libs.tech/combined/sky130.lib.spice`, corner `tt`).
- `meas ... failed`: mệnh đề trig/targ không bắt được cạnh. Xem waveform trong `data/wave_*.txt`, chỉnh `rise=`/`fall=`/`td=`.
- `alterparam` không có: ngspice quá cũ (< 32), cần nâng cấp.

## Ảnh do người dùng cung cấp
Ảnh chụp schematic Xschem đặt vào `figs/schematic_and.png` và `figs/schematic_ha.png`; builder tự chèn vào slide 13.

## Cấu trúc
- `sim/`: netlist ngspice (`cells_sky130.spice` là thư viện cell; `params.spice` là tham số; `pdk.spice` là đường dẫn PDK)
- `scripts/analyze.py`: đọc log và data → `results.json`, `figs/*.png`, `logs/check_report.md`
- `slides/build_slides.py`: sinh slide từ template HUST và `results.json`
- `docs/`: đề bài và bài giảng ECE4740

## Vẽ schematic Xschem (slide 13) — Claude Code tự làm
Mục tiêu: tạo schematic cho INV, NAND2, OAI21, AND2, HA14 và testbench, kích thước khớp `sim/cells_sky130.spice`
(W tính bằng µm, L = 0.15, k lấy từ `results.json`), rồi xuất ảnh `figs/schematic_and.png`, `figs/schematic_ha.png`.

1. Cài Xschem nếu chưa có: `sudo apt-get install -y xschem` (Ubuntu 23.04+), nếu không có gói thì build từ
   https://github.com/StefanSchippers/xschem (`./configure && make && sudo make install`). Cài thêm `netgen-lvs` để so netlist.
2. Trong `xschem/`: chép `xschemrc` từ `<PDK_ROOT>/sky130A/libs.tech/xschem/xschemrc` (PDK_ROOT suy ra từ `sim/pdk.spice`).
3. TRƯỚC khi viết .sch: đọc các file symbol thật để lấy toạ độ chân:
   `sky130_fd_pr/nfet_01v8.sym`, `sky130_fd_pr/pfet_01v8.sym` (thư mục xschem của PDK) và `devices/ipin.sym`, `opin.sym`,
   `iopin.sym`, `lab_pin.sym` (thư mục cài Xschem, ví dụ /usr/local/share/xschem/xschem_library/devices).
   Đọc một file .sch mẫu đi kèm Xschem/PDK để theo đúng cú pháp (dòng `v {xschem version=...}`, `C {sym} x y rot flip {props}`, `N x1 y1 x2 y2 {lab=...}`).
4. Viết `inv.sch`, `nand2.sch`, `oai21.sch`: đặt transistor theo thứ tự Euler của slide 14 (NAND2: A → B; OAI21: nAB → A → B),
   vẽ dây `N` nối đúng toạ độ chân; chân body nối vdd (PMOS) / gnd (NMOS). Bảng nối dây xem `sim/cells_sky130.spice`.
   Tạo symbol tương ứng (`.sym`) với các chân cùng tên: inv (in, out, vdd, gnd), nand2 (a, b, y, vdd, gnd),
   oai21 (a, b, c, y, vdd, gnd).
5. Viết `and2.sch` (nand2 + inv) và `ha14.sch` (nand2, inv, oai21, inv; nab nối chân c của oai21).
6. KIỂM TRA: xuất netlist bằng Xschem chế độ dòng lệnh (xem `xschem --help`, thường là `xschem -n -s -q <file>.sch`),
   rồi so với subckt tương ứng trong `sim/cells_sky130.spice` bằng netgen
   (`netgen -batch lvs "<netlist_xschem> ha14" "../sim/cells_sky130.spice HA14" <PDK_ROOT>/sky130A/libs.tech/netgen/sky130A_setup.tcl`).
   Chỉ dùng ảnh khi netgen báo khớp (hoặc khớp sau khi sửa). Ghi kết quả vào `logs/check_report.md`.
7. Mở thử `xschem ha14.sch` để chắc file đọc được và dây không chéo lung tung; chỉnh toạ độ cho gọn.
8. Xuất ảnh nền trắng: dùng tuỳ chọn xuất PNG/SVG dòng lệnh của Xschem (xem `xschem --help`) hoặc lệnh Tcl
   `xschem print png <file> <w> <h>`; nếu chỉ xuất được SVG thì đổi sang PNG bằng `rsvg-convert`/`cairosvg`.
   Lưu `figs/schematic_and.png` (từ and2.sch) và `figs/schematic_ha.png` (từ ha14.sch). Nên xuất thêm nand2, oai21 để nộp kèm.
9. Chạy `python3 slides/build_slides.py` để chèn ảnh vào slide 13.
