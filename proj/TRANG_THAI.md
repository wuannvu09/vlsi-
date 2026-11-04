# Trạng thái công việc (cập nhật 04/11/2026, làm trên Windows)

Đọc file này cùng `CLAUDE.md` trước khi làm tiếp trên Ubuntu.

## Đã xong (mục 1–6 và tiêu chí kiểm tra trong CLAUDE.md)
- Mô phỏng đủ 5 netlist, `logs/check_report.md` sạch, mọi tiêu chí số liệu đạt. Chọn được k = 3 (VM = 0,893 V).
- Slide 21 đã ghi kết quả thật; mọi con số trong slide lấy từ `results.json`, kể cả thông số thiết kế ở `setup`.
- Toàn bộ trích dẫn (Lecture X / page Y) đã kiểm tra bằng `pdftotext`.
- Đã render 24 slide (bằng PowerPoint): không có chữ tràn hay đè hình.

## Những sửa đổi đã làm (đừng hoàn tác)
- `sim/02_inv_vtc.spice`: `echo KBLOCK` đặt trước `meas`; VOH/VOL đo bằng `max`/`min`; tên file wrdata dùng `{$kk}`.
- `sim/03_and`, `04_ha14`, `05_ha18`: Pstatic đo bằng `op` ở 4 tổ hợp đầu vào rồi lấy trung bình (cửa sổ trong tran
  dính dòng quá độ); thêm `tr_a`, `tf_a` để đo sườn vào thực tế.
- `scripts/analyze.py`: thêm `do_setup` (thông số thiết kế), `do_func` (kiểm bảng chân lý, đo glitch).
- `run_all.sh`: tương thích thêm Windows, trên Linux chạy như cũ.

## Việc cần làm trên Ubuntu
1. Chép cả thư mục `proj/`, bỏ `.venv/` (venv của Windows).
2. `./setup.sh` để ghi lại `sim/pdk.spice` (file hiện chứa đường dẫn Windows). Nên dùng
   `.../libs.tech/combined/sky130.lib.spice`: bản `ngspice/` in ra nhiều lỗi include của nfet_20v0 (vô hại nhưng log bẩn).
3. `./run_all.sh`, rồi so `results.json` với số liệu tham chiếu bên dưới (nếu cùng phiên bản PDK thì phải khớp).
4. Làm mục **"Vẽ schematic Xschem (slide 13)"** trong CLAUDE.md, các bước 1–9 (apt: `xschem`, `netgen-lvs`).
   Phiên bản PDK đang dùng (volare): sky130 `c6d73a35f524070e85faff4a6a9eef49553ebc2b`.
5. Phần người dùng tự làm: tên nhóm và GVHD (biến `lines` trong `build_slides.py`), stick diagram OAI21 (slide 16).

## Số liệu tham chiếu (bản chạy trên Windows, ngspice-42)
- VT ngoại suy: n 0,74 V, p 0,74 V; ID,n/ID,p = 2,59.
- tp xấu nhất: AND 56,6 ps; HA14 Sum 112,0 ps, Carry 79,4 ps; HA18 Sum 91,8 ps.
- Pavg: AND 19,06 µW; HA14 48,29 µW; HA18 60,47 µW. Pstatic: 1,23 / 2,60 / 2,99 nW.
- Glitch Sum: HA14 4 mV (không có); HA18 0,16 V (dưới VIL).
