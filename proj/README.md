# BTL VLSI: cổng AND và Half Adder mức transistor (sky130 + ngspice)

## Yêu cầu
Ubuntu hoặc WSL (Windows), có mạng. VS Code mở thư mục này (với WSL: dùng extension "WSL", mở thư mục bên trong WSL).

## Chạy
1. Terminal → Run Task → **1. Cai dat (ngspice + sky130)** (hoặc `./setup.sh`)
2. Terminal → Run Task → **2. Chay mo phong + sinh slide** (hoặc `./run_all.sh`, phím tắt Ctrl+Shift+B)
3. Mở `logs/check_report.md` để xem cảnh báo; slide ở `output/BTL_VLSI_AND_HalfAdder_HUST.pptx`.

Nếu dùng Claude Code trong VS Code: chỉ cần nhắn *"Làm theo CLAUDE.md"*.

## Schematic Xschem (slide 13)
Cần thêm `sudo apt-get install -y xschem netgen-lvs librsvg2-bin`. Chạy task **4. Schematic Xschem + LVS + anh slide 13**
(hoặc `./xschem/build.sh` rồi task 3):
- `xschem/gen_sch.py` sinh `inv/nand2/oai21.sch` (mức transistor, thứ tự Euler của slide 14), symbol `.sym`,
  `and2.sch`, `ha14.sch`; kích thước lấy từ `results.json`.
- `xschem/lvs.sh` xuất netlist từ Xschem và so với `sim/cells_sky130.spice` bằng netgen (topology + W/L),
  ghi kết quả vào `logs/check_report.md`. Ảnh chỉ được xuất khi cả 5 cell khớp.
- Ảnh: `figs/schematic_and.png`, `figs/schematic_ha.png` (slide 13), kèm `schematic_inv/nand2/oai21.png` để nộp.
- Mở xem/sửa: `cd xschem && xschem ha14.sch` (PDK_ROOT tự suy ra nếu PDK nằm ở `~/.volare`).

## Phần cần tự làm
- Điền tên nhóm, GVHD ở slide bìa (sửa trong `slides/build_slides.py`, biến `lines`).
