# Trạng thái công việc (cập nhật 04/11/2026)

Đọc file này cùng `CLAUDE.md` trước khi làm tiếp.

## Đã làm trên Ubuntu 24.04 (04/11/2026)
- Môi trường: ngspice-45.2, xschem 3.4.4, netgen-lvs 1.5.133 (apt); PDK sky130 `c6d73a35…` qua volare ở `~/.volare`.
  `sim/pdk.spice` trỏ tới `~/.volare/sky130A/libs.tech/combined/sky130.lib.spice`.
- `./run_all.sh`: `check_report.md` sạch; `results.json` khớp bản Windows ở cả 133 giá trị (sai lệch < 0,1 %).
- Schematic Xschem (mục "Vẽ schematic Xschem", bước 1–9) đã xong, chạy lại bằng `./xschem/build.sh`:
  - `gen_sch.py` sinh .sch/.sym (dùng symbol 3 chân `nfet3/pfet3_01v8`, body = vdd/gnd qua thuộc tính `body=`,
    vẫn vào netlist). `xschemrc` chép từ PDK, đã thêm lại đường dẫn `libs.tech/xschem` của PDK.
  - LVS netgen: inv, nand2, oai21, and2, ha14 đều khớp topology và W/L (đã thử cố ý sai W → netgen báo property error).
  - Ảnh `figs/schematic_*.png` đã chèn vào slide 13; đã render PDF bằng LibreOffice, slide 13 không tràn chữ.
- `setup.sh`: ghim phiên bản PDK, ưu tiên `combined/`.
- Slide 16: stick diagram OAI21 vẽ bằng shape trong `build_slides.py` (poly nAB → A → B; pdiff Y|nAB|VDD|A|p1|B|Y;
  ndiff Y|nAB|n1|A|GND|B|n1), bố cục 4 cell thu gọn phía trên.

## Còn lại (người dùng tự làm)
- Tên nhóm và GVHD (biến `lines` trong `build_slides.py`).
- Testbench Xschem (tb_*.sch) chưa vẽ: mô phỏng vẫn dùng `sim/*.spice`; nếu cần nộp thì thêm sau.

---
Phần dưới là ghi chú từ lần làm trên Windows.

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
