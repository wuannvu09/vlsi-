# BTL VLSI: cổng AND và Half Adder mức transistor (sky130 + ngspice)

## Yêu cầu
Ubuntu hoặc WSL (Windows), có mạng. VS Code mở thư mục này (với WSL: dùng extension "WSL", mở thư mục bên trong WSL).

## Chạy
1. Terminal → Run Task → **1. Cai dat (ngspice + sky130)** (hoặc `./setup.sh`)
2. Terminal → Run Task → **2. Chay mo phong + sinh slide** (hoặc `./run_all.sh`, phím tắt Ctrl+Shift+B)
3. Mở `logs/check_report.md` để xem cảnh báo; slide ở `output/BTL_VLSI_AND_HalfAdder_HUST.pptx`.

Nếu dùng Claude Code trong VS Code: chỉ cần nhắn *"Làm theo CLAUDE.md"*.

## Phần cần tự làm bằng giao diện
- Vẽ schematic trên Xschem, chụp lưu thành `figs/schematic_and.png`, `figs/schematic_ha.png`, rồi chạy task 3.
- Điền tên nhóm, GVHD ở slide bìa (sửa trong `slides/build_slides.py`, biến `lines`).
