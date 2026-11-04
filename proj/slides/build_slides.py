import copy, os, json
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_LINE

HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
SRC=os.path.join(HERE,'template','hust_powerpoint_template_part05.pptx')
RES=json.load(open(os.path.join(ROOT,'results.json'))) if os.path.exists(os.path.join(ROOT,'results.json')) else {}
def G(path,default=None):
    d=RES
    for k in path.split('.'):
        if not isinstance(d,dict) or k not in d: return default
        d=d[k]
    return d
def F(path,scale=1,fmt='{:.1f}',unit=''):
    v=G(path)
    if v is None: return '[__]'
    return (fmt.format(v*scale)+unit).replace('.',',')
def FIG(name):
    p=os.path.join(ROOT,'figs',name); return p if os.path.exists(p) else None
prs=Presentation(SRC)
RED=RGBColor(0xBE,0x1E,0x2D); GOLD=RGBColor(0xE2,0xA3,0x0F); DARK=RGBColor(0x1E,0x1B,0x1B)
GREY=RGBColor(0x6B,0x64,0x61); LIGHT=RGBColor(0xF6,0xF2,0xEE); LINE=RGBColor(0xE2,0xDA,0xD4)
BLUE=RGBColor(0x1F,0x5F,0x9E); WHITE=RGBColor(0xFF,0xFF,0xFF); PINK=RGBColor(0xF8,0xE3,0xE1)
FONT='Arial'; MONO='Consolas'

slides=list(prs.slides)
title_slide, thanks_slide, content_tpl = slides[2], slides[12], slides[3]
sldnum_el = copy.deepcopy([sh for sh in content_tpl.shapes if sh.is_placeholder and sh.placeholder_format.type==13][0]._element)
LAY = prs.slide_layouts[3]      # red band + gold line + HUST footer
LAY_END = prs.slide_layouts[7]  # red side panel

# --- remove unused template slides
lst=prs.slides._sldIdLst
for i,sid in enumerate(list(lst)):
    if i not in (2,12):
        prs.part.drop_rel(sid.rId); lst.remove(sid)

def runs(p, text, size, color=DARK, bold=False, font=FONT, italic=False):
    parts=text.split('**')
    for i,seg in enumerate(parts):
        if not seg: continue
        r=p.add_run(); r.text=seg; f=r.font; f.size=Pt(size); f.name=font
        f.bold = bold or (i%2==1); f.italic=italic; f.color.rgb=color

def tb(s,x,y,w,h,paras,size=15,color=DARK,bold=False,align=PP_ALIGN.LEFT,font=FONT,space=6,anchor=MSO_ANCHOR.TOP):
    box=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=box.text_frame
    tf.word_wrap=True; tf.vertical_anchor=anchor
    for m in ('margin_left','margin_right','margin_top','margin_bottom'): setattr(tf,m,Inches(0.04))
    if isinstance(paras,str): paras=[paras]
    for i,pt in enumerate(paras):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.alignment=align; p.space_after=Pt(space)
        if isinstance(pt,tuple): t,kw=pt
        else: t,kw=pt,{}
        runs(p,t,kw.get('size',size),kw.get('color',color),kw.get('bold',bold),kw.get('font',font))
    return box

def rect(s,x,y,w,h,fill=WHITE,line=LINE,lw=1,shape=MSO_SHAPE.ROUNDED_RECTANGLE,dash=False):
    r=s.shapes.add_shape(shape,Inches(x),Inches(y),Inches(w),Inches(h))
    if shape==MSO_SHAPE.ROUNDED_RECTANGLE: r.adjustments[0]=0.06
    if fill is None: r.fill.background()
    else: r.fill.solid(); r.fill.fore_color.rgb=fill
    if line is None: r.line.fill.background()
    else:
        r.line.color.rgb=line; r.line.width=Pt(lw)
        if dash: r.line.dash_style=MSO_LINE.DASH
    r.shadow.inherit=False
    r.text_frame.text=''
    return r

def card(s,x,y,w,h,paras,size=13,accent=None,fill=LIGHT):
    rect(s,x,y,w,h,fill=fill,line=LINE)
    if accent: rect(s,x,y,0.08,h,fill=accent,line=None,shape=MSO_SHAPE.RECTANGLE)
    tb(s,x+0.18,y+0.1,w-0.3,h-0.2,paras,size=size)

def ph(s,x,y,w,h,text):
    rect(s,x,y,w,h,fill=LIGHT,line=RGBColor(0xB9,0xAF,0xA8),lw=1.5,dash=True)
    tb(s,x+0.2,y,w-0.4,h,[text],size=13,color=GREY,align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)

def img(s,x,y,w,h,fig,text):
    p=FIG(fig)
    if not p: return ph(s,x,y,w,h,text)
    iw,ih=Image.open(p).size; r=min(w/iw,h/ih); W,H=iw*r,ih*r
    s.shapes.add_picture(p,Inches(x+(w-W)/2),Inches(y+(h-H)/2),Inches(W),Inches(H))

def table(s,x,y,w,widths,rows,size=12,hl=None,center=False,rowh=0.36):
    t=s.shapes.add_table(len(rows),len(rows[0]),Inches(x),Inches(y),Inches(w),Inches(rowh*len(rows))).table
    tot=sum(widths)
    for j,wd in enumerate(widths): t.columns[j].width=Inches(w*wd/tot)
    for i,row in enumerate(rows):
        t.rows[i].height=Inches(rowh)
        for j,val in enumerate(row):
            c=t.cell(i,j); c.text=''; tf=c.text_frame; tf.word_wrap=True
            c.margin_left=c.margin_right=Inches(0.06); c.margin_top=c.margin_bottom=Inches(0.03)
            c.vertical_anchor=MSO_ANCHOR.MIDDLE
            p=tf.paragraphs[0]; p.alignment=PP_ALIGN.CENTER if center else PP_ALIGN.LEFT
            if i==0: runs(p,val,size,WHITE,True)
            else: runs(p,val,size,DARK)
            c.fill.solid()
            c.fill.fore_color.rgb = RED if i==0 else (PINK if hl==i else (WHITE if i%2 else LIGHT))
    return t

def F2(d,k):
    return ('{:.3f}'.format(d[k])).replace('.',',') if k in d else '[__]'

def cite(s,text,color=RED):
    tb(s,0.4,6.38,9.2,0.4,[text],size=10.5,color=color)

def new(title,notes=''):
    s=prs.slides.add_slide(LAY)
    for sh in list(s.placeholders):
        if sh.placeholder_format.idx!=0: sh._element.getparent().remove(sh._element)
    s.shapes.title.text=title
    for p in s.shapes.title.text_frame.paragraphs:
        for r in p.runs: r.font.size=Pt(24)
    s.shapes._spTree.append(copy.deepcopy(sldnum_el))
    if notes: s.notes_slide.notes_text_frame.text=notes
    return s

# ---------- cover (template slide 3)
shp=[sh for sh in title_slide.shapes if sh.has_text_frame]
t,sub=shp[0],shp[1]
t.top=Inches(2.2); t.height=Inches(1.3)
p=t.text_frame.paragraphs[0]; r=p.runs[0]; r.text='THIẾT KẾ CỔNG AND VÀ BỘ CỘNG HALF ADDER MỨC TRANSISTOR'; r.font.size=Pt(30)
t.text_frame.word_wrap=True
sub.top=Inches(3.75); sub.height=Inches(1.6)
ps=sub.text_frame.paragraphs
lines=['Bài tập lớn giữa kỳ – Thiết kế VLSI','Nhóm [__]: [Họ tên 1], [Họ tên 2], [Họ tên 3]','Giảng viên hướng dẫn: [__]']
ps[0].runs[0].text=lines[0]; ps[0].runs[0].font.size=Pt(18)
for extra in ps[0].runs[1:]: extra._r.getparent().remove(extra._r)
tmpl_p=ps[0]._p
for q in ps[1:]: q._p.getparent().remove(q._p)
for ln in lines[1:]:
    np_=copy.deepcopy(tmpl_p); sub.text_frame._txBody.append(np_)
from pptx.text.text import _Paragraph
for i,q in enumerate(sub.text_frame.paragraphs):
    q.runs[0].text=lines[i]; q.runs[0].font.size=Pt(18 if i==0 else 15)
title_slide.notes_slide.notes_text_frame.text='Giới thiệu nhóm và tên đề tài: hai mạch cổng AND và Half Adder, thiết kế ở mức transistor.'

# ---------- 2 agenda
s=new('Nội dung trình bày','Trình bày theo đúng thứ tự yêu cầu của đề.')
items=[('01','Cơ sở lý thuyết','VTC, delay, công suất của mạch CMOS'),('02','Khảo sát PDK','Đặc tuyến I–V, VTC inverter tham chiếu'),
('03','Tối ưu Boolean','Giảm Half Adder từ 18 xuống 14 transistor'),('04','Sizing và schematic','Tính W/L theo inverter đơn vị'),
('05','Layout cơ bản','Euler path và stick diagram'),('06','Mô phỏng và đánh giá','Chức năng, delay, công suất, PDP')]
for k,(n,h,d) in enumerate(items):
    x=0.4+(k%2)*4.7; y=1.25+(k//2)*1.65
    card(s,x,y,4.5,1.45,[(n,{'size':22,'color':RED,'bold':True}),(h,{'size':16,'bold':True}),(d,{'size':13,'color':GREY})],accent=RED)

# ---------- 3 tools
s=new('Công cụ và PDK sử dụng','Nêu rõ PDK, VDD, L. Mọi kết quả phía sau phụ thuộc các thông số này.')
table(s,0.4,1.25,9.2,[40,60],[['Hạng mục','Lựa chọn của nhóm'],['Schematic','Xschem'],['Mô phỏng','ngspice'],['Layout, DRC / LVS','Magic / Netgen'],['PDK','SkyWater 130 nm (sky130A, open_pdks), corner tt'],['Thiết bị','sky130_fd_pr__nfet_01v8 / pfet_01v8'],['VDD, L, nhiệt độ',F('setup.vdd',1,'{:g}',' V')+'; '+F('setup.l',1,'{:g}',' µm')+'; '+F('setup.temp',1,'{:g}',' °C')],['Vẽ hình','draw.io']],size=14,rowh=0.38)
card(s,0.4,4.6,9.2,1.4,[('Lý do chọn PDK',{'size':15,'bold':True}),'Bộ công cụ và PDK mã nguồn mở, đủ cả luồng schematic → mô phỏng → layout → LVS. Quy trình tham khảo repo [3] trong tài liệu tham khảo.'],size=14,accent=RED)
cite(s,'Ghi rõ nhiệt độ vì dòng rò tăng theo hàm mũ của nhiệt độ (ECE4740 – Lecture 8 / page 3)')

# ---------- 4 VTC
s=new('Đặc tuyến truyền đạt điện áp (VTC) của inverter',
 'VM: L4 slide 143 (trang 13). r = 1 cho VM = 0,5VDD: slide 145 (trang 14). Cầu chia trở: slide 147 (trang 15). VIL, VIH: slide 151 (trang 17). Noise margin: slide 152 (trang 18). Hình VTC là sơ đồ minh họa nhóm tự vẽ.')
tb(s,0.4,1.25,5.1,4.9,[
 '**VM** (ngưỡng chuyển mạch): điểm Vin = Vout, khi đó cả NMOS và PMOS đều bão hòa và IDn = IDp.',
 '**VIL, VIH**: hai điểm trên VTC có độ dốc bằng −1; VOH, VOL là mức ra cao và thấp.',
 '**Lề nhiễu**: NMH = VOH − VIH và NML = VIL − VOL, càng lớn càng tốt.',
 'Muốn VM = 0,5·VDD cần cân bằng NMOS và PMOS. Tăng Wp (hoặc giảm Wn) làm RONp giảm, VM tăng.'],size=15,space=12)
ox,oy,W,H=5.95,1.35,3.55,3.6
rect(s,ox-0.15,oy-0.15,W+0.3,H+0.55,fill=WHITE,line=LINE)
def L(x1,y1,x2,y2,color=DARK,w=1.5,dash=False):
    c=s.shapes.add_connector(1,Inches(x1),Inches(y1),Inches(x2),Inches(y2)); c.line.color.rgb=color; c.line.width=Pt(w)
    if dash: c.line.dash_style=MSO_LINE.DASH
X0,Y0=ox+0.3,oy+H-0.1
L(X0,Y0,ox+W,Y0); L(X0,Y0,X0,oy+0.05)
L(X0,Y0,ox+W-0.5,oy+0.25,GREY,1,True)
import math
pts=[]
for i in range(41):
    u=i/40; vin=u
    vout=1/(1+math.exp((vin-0.5)*18))
    pts.append((X0+u*(W-0.4), Y0-0.15-vout*(H-0.55)))
ff=s.shapes.build_freeform(Inches(pts[0][0]),Inches(pts[0][1]),scale=1.0)
ff.add_line_segments([(Inches(a),Inches(b)) for a,b in pts[1:]],close=False)
cur=ff.convert_to_shape(); cur.fill.background(); cur.line.color.rgb=RED; cur.line.width=Pt(3)
mx,my=X0+0.5*(W-0.4), Y0-0.15-0.5*(H-0.55)
d=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(mx-0.07),Inches(my-0.07),Inches(0.14),Inches(0.14)); d.fill.solid(); d.fill.fore_color.rgb=BLUE; d.line.fill.background()
tb(s,mx+0.1,my-0.35,0.5,0.3,['VM'],size=13,color=BLUE,bold=True)
tb(s,ox+W-0.5,Y0+0.02,0.6,0.3,['Vin'],size=12)
tb(s,X0+0.05,oy-0.1,0.7,0.3,['Vout'],size=12)
tb(s,ox+W-0.75,oy+0.25,0.6,0.3,['y = x'],size=11,color=GREY)
cite(s,'(ECE4740 – Lecture 4 / page 13, 14, 15, 17, 18)')

# ---------- 5 delay
s=new('Các tham số thời gian: delay, rise và fall time','L5 slide 165, 166 trang 3; slide 180 trang 10. L6 slide 204 trang 6.')
card(s,0.4,1.25,4.5,4.9,[('Định nghĩa đo',{'size':16,'bold':True}),'**tr, tf**: từ 10% đến 90% biên độ, luôn đo tại đầu ra.',
 '**tpHL, tpLH**: từ mốc 50% của đầu vào đến mốc 50% của đầu ra.',('tp = 0,5·(tpHL + tpLH)',{'font':MONO,'color':RED,'size':16}),('(Lecture 5 / page 3)',{'color':RED,'size':11})],size=14)
card(s,5.1,1.25,4.5,4.9,[('Mô hình RC bậc một',{'size':16,'bold':True}),('tp = ln2·Req·CL ≈ 0,69·Req·CL',{'font':MONO,'color':RED,'size':14}),
 'Thời gian xả tụ từ 100% xuống 50% VDD qua điện trở tương đương Req.',('(Lecture 5 / page 10)',{'color':RED,'size':11}),
 ('tp ≈ 0,69·Rref·Cref·(1 + Cext/(S·Cref))',{'font':MONO,'color':RED,'size':12}),'Tăng hệ số sizing S giảm ảnh hưởng của tải, nhưng tăng tải cho tầng trước.',('(Lecture 6 / page 6)',{'color':RED,'size':11})],size=14)
cite(s,'Các định nghĩa này dùng trực tiếp cho lệnh đo delay ở phần mô phỏng',GREY)

# ---------- 6 power
s=new('Ba nguồn tiêu thụ công suất','L7 slide 237 trang 7; slide 234 trang 6; slide 244–247 trang 11–12. L8 slide 253 trang 2; slide 255 trang 3.')
rowsP=[('Công suất động','P = VDD²·fclk·Σ(αk/2)·Ck','Nạp và xả điện dung các nút. Mỗi chu kỳ 0→1→0 tiêu tốn CL·VDD², không phụ thuộc kích thước transistor.','(Lecture 7 / page 6, 7)'),
('Dòng ngắn mạch','Isc khi NMOS và PMOS cùng dẫn','Sườn vào có độ dốc hữu hạn tạo đường VDD → GND trong thời gian ngắn. Giảm bằng sườn nhanh, giảm W/L, giảm VDD.','(Lecture 7 / page 11, 12)'),
('Công suất tĩnh','Pstatic = Ileak·VDD','Rò dưới ngưỡng, rò cổng, rò tiếp giáp drain. Cả ba tăng theo hàm mũ của nhiệt độ.','(Lecture 8 / page 2, 3)')]
for k,(h,f,d,c) in enumerate(rowsP):
    y=1.2+k*1.68
    card(s,0.4,y,9.2,1.52,[(h+'   ',{'size':15,'bold':True}),(f,{'font':MONO,'color':RED,'size':14}),(d,{'size':13}),(c,{'color':RED,'size':10.5})],accent=RED,size=13)
cite(s,'Chỉ số tổng hợp nhóm dùng: PDP = Pavg · tp (kết hợp tp của Lecture 5 và công suất của Lecture 7)',GREY)

# ---------- 7 pdk-iv
s=new('Khảo sát PDK: đặc tuyến I–V của NMOS và PMOS','VT: L2 slide 59 trang 11. Vùng làm việc: slide 64 trang 13. Bão hòa: slide 70 trang 16. λ và I–V kênh dài: slide 73–74 trang 18.')
img(s,0.4,1.25,4.8,4.9,'iv.png','[Chèn đồ thị ID–VDS (quét VDS, tham số VGS) và ID–VGS của NMOS, PMOS cùng W/L]')
table(s,5.4,1.25,4.2,[46,27,27],[['Thông số','NMOS','PMOS'],['VT (ngoại suy)',F('iv.vtn',1,'{:.2f}',' V'),F('iv.vtp',1,'{:.2f}',' V')],['ID,sat ('+F('setup.wn',1,'{:g}')+'/'+F('setup.l',1,'{:g}')+' µm)',F('iv.idsat_n',1e6,'{:.0f}',' µA'),F('iv.idsat_p',1e6,'{:.0f}',' µA')]],size=12,rowh=0.45)
card(s,5.4,2.8,4.2,3.35,['Mô hình lý thuyết, vùng bão hòa:',('ID = ½µCox(W/L)(VGS−VT)²(1+λVDS)',{'font':MONO,'color':RED,'size':11}),
 'Chỉ chính xác khi L > 0,25 µm; với PDK nanomet cần lấy số liệu từ mô phỏng.','Tỉ số ID,n / ID,p = '+F('iv.ratio',1,'{:.2f}')+' → gợi ý k ≈ tỉ số này để PMOS dẫn bằng NMOS.'],size=13,accent=RED)
cite(s,'(ECE4740 – Lecture 2 / page 11, 13, 16, 18)')

# ---------- 8 vtc-result
s=new('VTC inverter tham chiếu và chọn tỉ lệ k = Wp/Wn','Tỉ lệ 2–3: L5 slide 188 trang 14. β tối ưu cho tp: slide 191 trang 16.')
img(s,0.4,1.25,4.6,4.9,'vtc.png','[Chèn họ đường VTC khi quét k; DC sweep Vin 0 → VDD, bước 1 mV]')
table(s,5.2,1.25,4.4,[22,26,26,26],[['k','VM (V)','NML (V)','NMH (V)']]+([[(('**%g**' if b['k']==G('k') else '%g')%b['k']).replace('.',','),F2(b,'vm'),F2(b,'nml'),F2(b,'nmh')] for b in G('vtc')] if G('vtc') else [[k,'[__]','[__]','[__]'] for k in ['1','1,5','2','2,5','3']]),size=12,center=True,rowh=0.4)
card(s,5.2,3.85,4.4,2.3,['Tỉ lệ PMOS/NMOS khoảng 2–3 cho VTC đối xứng, lề nhiễu tối ưu và tpHL ≈ tpLH; PMOS nhỏ hơn giảm tp nhưng mất đối xứng.','Nhóm chọn **k = '+F('k',1,'{:g}')+'** (VM gần VDD/2 = '+F('setup.vdd',0.5,'{:g}',' V')+' nhất); Wn = '+F('setup.wn',1,'{:g}',' µm')+', Wp = '+('{:g}'.format(G('k')*G('setup.wn')).replace('.',',') if G('k') and G('setup.wn') else '[__]')+' µm, L = '+F('setup.l',1,'{:g}',' µm')+'. (Repo [3]: k = 2 cho ngưỡng 0,87 V.)'],size=13,accent=RED)
cite(s,'(ECE4740 – Lecture 4 / page 14); (Lecture 5 / page 14, 16)')

# ---------- 9 boolean
s=new('Tối ưu Boolean: biến đổi biểu thức Half Adder',"(A+B)(A'+B') = AB' + A'B. De Morgan: L10 slide 406 trang 26.")
table(s,0.4,1.3,3.6,[25,25,25,25],[['A','B','Carry','Sum'],['0','0','0','0'],['0','1','0','1'],['1','0','0','1'],['1','1','1','0']],size=15,center=True,rowh=0.5)
tb(s,4.4,1.25,5.2,2.2,[('Carry = A·B',{'font':MONO,'size':18}),("Sum = A'B + AB'",{'font':MONO,'size':18}),("    = (A + B)·(A' + B')",{'font':MONO,'size':16,'color':GREY})],space=10)
card(s,4.4,3.4,5.2,2.6,[("Sum = (A + B)·(A·B)'",{'font':MONO,'size':18,'color':RED,'bold':True}),
 "Bước cuối dùng De Morgan: A' + B' = (A·B)'. Tín hiệu nAB = (A·B)' đã có sẵn trong cổng AND."],size=14,accent=RED)
cite(s,'(ECE4740 – Lecture 10 / page 26: định lý De Morgan)')

# ---------- 10 options
s=new('So sánh ba phương án hiện thực Half Adder','Không dùng pass transistor vì NMOS kéo lên kém: L2 slide 56 trang 9; L10 slide 402 trang 24.')
table(s,0.4,1.2,9.2,[15,47,9,29],[['Phương án','Cấu trúc','Số T','Đặc điểm'],['Cơ bản','AND (NAND2 + INV) và XOR (2 INV + AOI22)','18','Nhiều transistor nhất'],
 ['Dùng NOR','NAND2 + INV; NOR2(A,B); NOR2(Carry, NOR)','14','Sum do NOR2 kéo'],['**Đề xuất**','**NAND2 + INV; OAI21(A, B, nAB) + INV**','**14**','**Cả hai đầu ra có INV đệm**']],size=12,hl=3,rowh=0.5)
cc=[('Cổng CMOS luôn đảo: AND = NAND + INV; cổng N đầu vào cần ít nhất 2N transistor.','(Lecture 10 / page 27)'),
('Static CMOS: full swing, lề nhiễu cao, gần như không có đường VDD–GND khi tĩnh.','(Lecture 11 / page 4)'),
('XOR 2 đầu vào có logical effort g = 4, so với NAND2 là 4/3.','(Lecture 12 / page 8)')]
for k,(a,b) in enumerate(cc):
    card(s,0.4+k*3.1,3.55,2.95,2.55,[a,(b,{'color':RED,'size':11})],size=13)
cite(s,'Phương án đề xuất giảm 4 transistor (≈ 22%) so với cách cơ bản',GREY)

# ---------- 11 arch
s=new('Kiến trúc Half Adder 14 transistor được chọn','OAI21 với đầu vào A, B, nAB cho ra XNOR; đảo thêm một lần thành Sum. Cổng AND trong đề chính là nhánh Carry.')
def blk(x,y,w,text,border=BLUE):
    rect(s,x,y,w,0.55,fill=WHITE,line=border,lw=2); tb(s,x,y,w,0.55,[text],size=14,bold=True,align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
def lbl(x,y,w,text,color=DARK,bold=False,font=FONT):
    tb(s,x,y,w,0.55,[text],size=14,color=color,bold=bold,font=font,align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
for y,inp,g1,mid,g2,out in [(1.35,'A, B','NAND2 · 4T','nAB','INV · 2T','Carry = A·B'),(2.25,'A, B, nAB','OAI21 · 6T','XNOR','INV · 2T','Sum = A XOR B')]:
    lbl(0.3,y,1.2,inp,bold=True); lbl(1.45,y,0.35,'→',GREY); blk(1.8,y,1.6,g1); lbl(3.4,y,0.35,'→',GREY)
    lbl(3.75,y,0.9,mid,font=MONO); lbl(4.65,y,0.35,'→',GREY); blk(5.0,y,1.3,g2); lbl(6.3,y,0.35,'→',GREY); lbl(6.65,y,1.6,out,RED,True)
table(s,0.4,3.25,9.2,[14,14,16,36,20],[['A B','nAB','A + B',"XNOR = ((A+B)·nAB)'",'Sum'],['0 0','1','0','1','0'],['0 1','1','1','0','1'],['1 0','1','1','0','1'],['1 1','0','1','1','0']],size=13,center=True,rowh=0.45)
cite(s,'Tổng: 4 + 2 + 6 + 2 = 14 transistor · CMOS NAND, NOR: (ECE4740 – Lecture 10 / page 27, 28)')

# ---------- 12 sizing
s=new('Tính kích thước transistor theo inverter đơn vị','Sizing NAND/NOR: L11 slide 425 trang 8. Nhiều lời giải: slide 426–427 trang 9. Hệ số S: L6 slide 203 trang 6.')
tb(s,0.4,1.2,9.2,0.9,['Đường dẫn xấu nhất của mỗi mạng kéo lên và kéo xuống phải có điện trở bằng inverter đơn vị (Wn = W, Wp = kW). **n transistor nối tiếp → mỗi transistor rộng gấp n lần.**'],size=15)
table(s,0.4,2.15,9.2,[14,43,43],[['Cổng','NMOS (mạng kéo xuống)','PMOS (mạng kéo lên)'],['INV','W','kW'],['NAND2','A, B nối tiếp → mỗi cái 2W','A, B song song → mỗi cái kW'],['OAI21','nAB nối tiếp (A ∥ B) → tất cả 2W','nAB ∥ (A nối tiếp B) → A, B: 2kW; nAB: kW']],size=13,rowh=0.5)
card(s,0.4,4.4,4.5,1.75,['W = **'+F('setup.wn',1,'{:g}',' µm')+'**, k = **'+F('k',1,'{:g}')+'** (từ khảo sát VTC), L = **'+F('setup.l',1,'{:g}',' µm')+'**'],size=14,accent=RED)
card(s,5.1,4.4,4.5,1.75,['Ví dụ trong bài giảng với Wp = 2Wn: NAND2 có NMOS 2, PMOS 2; NOR2 có NMOS 1, PMOS 4.'],size=14,accent=RED)
cite(s,'(ECE4740 – Lecture 11 / page 8, 9); (Lecture 6 / page 6)')

# ---------- 13 schematic
s=new('Schematic trên công cụ','Vẽ theo kiểu phân cấp giúp kiểm tra từng khối độc lập trước khi ghép.')
img(s,0.4,1.25,4.5,4.5,'schematic_and.png','[Chèn schematic cổng AND: NAND2 + INV, ghi W/L trên từng transistor]')
img(s,5.1,1.25,4.5,4.5,'schematic_ha.png','[Chèn schematic Half Adder phân cấp: symbol NAND2, INV, OAI21]')
tb(s,0.4,5.8,4.5,0.4,['Cổng AND · 6 transistor'],size=13,color=GREY); tb(s,5.1,5.8,4.5,0.4,['Half Adder · 14 transistor'],size=13,color=GREY)
cite(s,'Xuất từ Xschem, PDK sky130; LVS (netgen) khớp với netlist mô phỏng sim/cells_sky130.spice',GREY)

# ---------- 14 euler
s=new('Euler path chung cho mạng kéo lên và kéo xuống',"Logic graph, Euler path: L11 slide 411–412 trang 1–2; ví dụ x = (a + b·c)' slide 414–415 trang 3. Sắp xếp lại đầu vào: slide 434 trang 13.")
tb(s,0.4,1.2,9.2,0.8,['Tìm một thứ tự đầu vào là Euler path trên cả đồ thị PUN và PDN. Khi đó poly xếp theo thứ tự này và diffusion liền mạch.'],size=15)
table(s,0.4,2.05,9.2,[13,32,32,23],[['Cổng','PUN (PMOS)','PDN (NMOS)','Thứ tự chung'],['NAND2','A ∥ B giữa VDD và Y','Y – A – n1 – B – GND','**A → B**'],['OAI21','nAB ∥ (VDD – A – p1 – B – Y)','nAB giữa Y và n1; A ∥ B giữa n1 và GND','**nAB → A → B**']],size=13,rowh=0.6)
card(s,0.4,4.1,9.2,2.05,['nAB đến muộn nhất (phải qua NAND2), nên đặt sát đầu ra: tín hiệu đến muộn nhất đặt gần đầu ra nhất.',
 ('PDN: Y –nAB→ n1 –A→ GND –B→ n1.   PUN: Y –nAB→ VDD –A→ p1 –B→ Y.',{'font':MONO,'size':12})],size=14,accent=RED)
cite(s,'(ECE4740 – Lecture 11 / page 1, 2, 3, 13)')

# ---------- 15 stick diagram (native shapes)
s=new('Stick diagram cổng AND (NAND2 + INV)','NAND2: hai PMOS song song chung contact nAB ở giữa; hai NMOS nối tiếp nên nút n1 không cần contact. Nên vẽ lại hình trên draw.io theo đúng bố cục.')
sc=0.0058; X0,Y0=0.4,1.3
METAL=RGBColor(0x3B,0x6F,0xB6); POLY=RGBColor(0xC8,0x32,0x3B); PD=RGBColor(0xE8,0xB0,0x4B); ND=RGBColor(0x5F,0xA3,0x5A)
def R(x,y,w,h,col):
    rect(s,X0+x*sc,Y0+y*sc,w*sc,h*sc,fill=col,line=None,shape=MSO_SHAPE.RECTANGLE)
rect(s,X0,Y0,1000*sc,560*sc,fill=WHITE,line=LINE,shape=MSO_SHAPE.RECTANGLE)
for spec in [(20,20,960,40,METAL),(20,500,960,40,METAL),(80,120,420,90,PD),(640,120,260,90,PD),(80,350,420,90,ND),(640,350,260,90,ND),
 (195,95,20,370,POLY),(350,95,20,370,POLY),(760,95,20,370,POLY),
 (120,60,20,105,METAL),(430,60,20,105,METAL),(680,60,20,105,METAL),(120,395,20,105,METAL),(680,395,20,105,METAL),
 (270,165,20,125,METAL),(270,280,510,20,METAL),(430,280,20,115,METAL),(840,165,20,230,METAL),(840,280,140,20,METAL)]:
    R(*spec)
for cx,cy in [(130,165),(280,165),(440,165),(690,165),(850,165),(130,395),(440,395),(690,395),(850,395),(770,290)]:
    R(cx-12,cy-12,24,24,DARK)
def lab(x,y,t,col,w=0.6): tb(s,X0+x*sc,Y0+y*sc,w,0.3,[t],size=12,color=col,bold=True)
lab(28,22,'VDD',WHITE); lab(28,502,'GND',WHITE); lab(158,225,'A',POLY,0.3); lab(313,225,'B',POLY,0.3); lab(675,232,'nAB',BLUE); lab(872,232,'Y',BLUE,0.3)
lx=6.35
for k,(col,name) in enumerate([(METAL,'Metal 1'),(POLY,'Poly (cổng)'),(PD,'p-diffusion (PMOS)'),(ND,'n-diffusion (NMOS)'),(DARK,'Contact')]):
    rect(s,lx,1.35+k*0.42,0.28,0.28,fill=col,line=None,shape=MSO_SHAPE.RECTANGLE); tb(s,lx+0.4,1.33+k*0.42,2.8,0.32,[name],size=13)
card(s,lx,3.55,3.25,2.6,['Poly xếp theo Euler path A → B.','pdiff: VDD | A | nAB | B | VDD','ndiff: GND | A | n1 | B | nAB','Inverter dùng dải diffusion riêng.'],size=12,accent=RED)
cite(s,'Hình do nhóm vẽ theo quy ước stick diagram (ECE4740 – Lecture 11 / page 2, 3)')

# ---------- 16 floorplan
s=new('Bố cục Half Adder và stick diagram OAI21',
 'Trên: bốn cell một hàng, độ rộng ô tỉ lệ số transistor theo chiều ngang. Dưới: stick diagram OAI21, poly theo Euler path nAB → A → B (slide 14). '
 'PUN: Y –nAB→ VDD –A→ p1 –B→ Y, nút p1 nối tiếp nên không cần contact. PDN: Y –nAB→ n1 –A→ GND –B→ n1, hai đầu n1 nối bằng metal đi phía trên ndiff '
 'để không cắt dây GND. Hình do nhóm vẽ.')
# --- floorplan (thu gon)
rect(s,0.4,1.22,9.2,0.3,fill=METAL,line=None,shape=MSO_SHAPE.RECTANGLE); tb(s,0.5,1.22,8,0.3,['VDD (metal, dùng chung cho cả 4 cell)'],size=11,color=WHITE,bold=True,anchor=MSO_ANCHOR.MIDDLE)
x=0.4
for f,n,o in [(4,'NAND2','A → B'),(2,'INV','nAB'),(5,'OAI21','nAB → A → B'),(2,'INV','XNOR')]:
    w=f/13*(9.2-0.45)
    rect(s,x,1.58,w,0.72,fill=PINK if n=='OAI21' else WHITE,line=BLUE,lw=2)
    tb(s,x+0.08,1.6,w-0.16,0.68,[(n,{'size':13,'bold':True}),('Poly: '+o,{'size':11})],space=0)
    x+=w+0.15
rect(s,0.4,2.36,9.2,0.3,fill=METAL,line=None,shape=MSO_SHAPE.RECTANGLE); tb(s,0.5,2.36,8,0.3,['GND (metal, dùng chung) · diffusion liền mạch trong mỗi cell, có khe ngắt giữa các cell'],size=11,color=WHITE,bold=True,anchor=MSO_ANCHOR.MIDDLE)
# --- stick diagram OAI21: poly nAB (x=200), A (420), B (660); contact o x = 100, 300, 540, 760
sc=0.0057; X0,Y0=0.4,2.85
rect(s,X0,Y0,1000*sc,580*sc,fill=WHITE,line=LINE,shape=MSO_SHAPE.RECTANGLE)
for spec in [(20,20,960,40,METAL),(20,520,960,40,METAL),       # ray VDD, GND
 (70,120,720,90,PD),(70,360,720,90,ND),                        # pdiff, ndiff (mot dai lien)
 (190,95,20,380,POLY),(410,95,20,380,POLY),(650,95,20,380,POLY),
 (290,60,20,105,METAL),                                        # VDD -> contact pdiff giua nAB va A
 (90,165,20,240,METAL),(750,165,20,90,METAL),(90,245,810,20,METAL),  # Y: pdiff trai + pdiff phai + ndiff trai -> dau ra
 (290,315,20,90,METAL),(750,315,20,90,METAL),(290,305,480,20,METAL), # n1: noi hai dau ndiff, di tren ndiff
 (530,405,20,115,METAL)]:                                      # GND <- contact ndiff giua A va B
    R(*spec)
for cx,cy in [(100,165),(300,165),(760,165),(100,405),(300,405),(540,405),(760,405)]:
    R(cx-12,cy-12,24,24,DARK)
lab(28,22,'VDD',WHITE); lab(28,522,'GND',WHITE)
lab(212,455,'nAB',POLY); lab(432,455,'A',POLY,0.3); lab(672,455,'B',POLY,0.3)
lab(905,232,'Y',BLUE,0.3); lab(785,318,'n1',BLUE,0.4); lab(520,128,'p1',DARK,0.4)
lx=6.3
for k,(col,name) in enumerate([(METAL,'Metal 1'),(POLY,'Poly (cổng)'),(PD,'p-diffusion (PMOS)'),(ND,'n-diffusion (NMOS)'),(DARK,'Contact')]):
    rect(s,lx,2.9+k*0.32,0.22,0.22,fill=col,line=None,shape=MSO_SHAPE.RECTANGLE); tb(s,lx+0.32,2.86+k*0.32,2.9,0.3,[name],size=12)
card(s,lx,4.55,3.3,1.6,['Poly theo Euler path **nAB → A → B**.',
 ('pdiff: Y|nAB|VDD|A|p1|B|Y',{'font':MONO,'size':10.5}),('ndiff: Y|nAB|n1|A|GND|B|n1',{'font':MONO,'size':10.5}),
 'p1 không cần contact; n1 nối bằng metal phía trên ndiff.'],size=11.5,accent=RED)
cite(s,'Hình do nhóm vẽ theo quy ước stick diagram (ECE4740 – Lecture 11 / page 2, 3)')

# ---------- 17 testbench
s=new('Thiết lập testbench','Mốc 50% và 10–90%: L5 trang 3. Delay theo mẫu đầu vào: L11 slide 422–423 trang 7. Sườn vào qua INV đệm: L7 slide 247–249 trang 12–13. Ghi nhiệt độ: L8 slide 255 trang 3.')
table(s,0.4,1.2,4.3,[34,66],[['Thành phần','Thiết lập'],['Nguồn A','PULSE, chu kỳ T = '+F('setup.va_per',1e9,'{:g}',' ns')],['Nguồn B','PULSE, chu kỳ 2T = '+F('setup.vb_per',1e9,'{:g}',' ns')],
 ['Sườn vào','Nguồn '+F('setup.src_tr',1e12,'{:.0f}',' ps')+' qua 2 INV đệm; tr/tf tại A: '+F('and.tr_a',1e12,'{:.0f}')+'/'+F('and.tf_a',1e12,'{:.0f}')+' ps (AND), '+F('ha14.tr_a',1e12,'{:.0f}')+'/'+F('ha14.tf_a',1e12,'{:.0f}')+' ps (HA)'],
 ['Tải đầu ra','CL = '+F('setup.cl',1e15,'{:g}',' fF')],['Nhiệt độ',F('setup.temp',1,'{:g}',' °C')+', corner tt']],size=12,rowh=0.5)
rect(s,4.9,1.2,4.7,3.0,fill=DARK,line=None)
tb(s,5.05,1.3,4.45,2.85,[('Đo tự động bằng meas (ngspice)',{'size':12,'bold':True,'color':RGBColor(0xE8,0xA0,0x9A)}),
 ('meas tran tplh_c trig v(a) val=0.9 rise=2\n+ targ v(carry) val=0.9 rise=1\nmeas tran tplh_s trig v(a) val=0.9 rise=1\n+ targ v(sum) val=0.9 rise=1\nmeas tran iavg avg i(Vdd) from=4n to=8n\nlet pavg = -iavg*1.8',{'font':MONO,'size':10,'color':RGBColor(0xF1,0xEC,0xE6)})],space=4)
card(s,0.4,4.45,9.2,1.7,['Delay phụ thuộc mẫu đầu vào (bài giảng: NAND2 có tpHL từ 45 ps đến 81 ps tùy mẫu), nên đo nhiều chuyển trạng thái và lấy giá trị xấu nhất.',
 'Chuỗi kích thích 00 → 10 → 01 → 11 → 00 đi qua cả 4 tổ hợp; delay lấy giá trị xấu nhất trong các chuyển trạng thái làm đổi đầu ra.'],size=14,accent=RED)
cite(s,'(ECE4740 – Lecture 5 / page 3); (Lecture 11 / page 7); (Lecture 7 / page 12); (Lecture 8 / page 3)')

# ---------- 18 waveform
s=new('Kiểm chứng chức năng bằng dạng sóng','Chỉ ra trên hình bốn khoảng thời gian ứng với 00, 10, 01, 11 và đầu ra tương ứng.')
img(s,0.4,1.25,4.5,4.5,'wave_and.png','[Chèn waveform cổng AND: A, B, Y]'); img(s,5.1,1.25,4.5,4.5,'wave_ha14.png','[Chèn waveform Half Adder: A, B, Carry, Sum]')
tb(s,0.4,5.8,4.5,0.4,['Cổng AND: Y = 1 chỉ khi A = B = 1'],size=13,color=GREY); tb(s,5.1,5.8,4.5,0.4,['Half Adder: khớp bảng chân lý ở cả 4 tổ hợp'],size=13,color=GREY)
cite(s,'Đo bằng meas: VOH = '+F('and.voh',1,'{:.3f}',' V')+', VOL = '+F('and.vol',1e6,'{:.2f}',' µV')+' (AND); VOH = '+F('ha14.voh_s',1,'{:.3f}',' V')+', VOL = '+F('ha14.vol_s',1e6,'{:.2f}',' µV')+' (Sum 14T) → full swing',GREY)

# ---------- 19 results
s=new('Kết quả mô phỏng delay và công suất','Pstatic đo bằng phân tích op (điểm làm việc DC) ở từng tổ hợp đầu vào đứng yên, rồi lấy trung bình.')
table(s,0.4,1.2,9.2,[34,22,22,22],[['Chỉ số','AND: Y','HA: Carry','HA: Sum'],
 ['tpHL (ps)',F('and.tphl',1e12),F('ha14.tphl_c',1e12),F('ha14.tphl_s',1e12)],
 ['tpLH (ps)',F('and.tplh',1e12),F('ha14.tplh_c',1e12),F('ha14.tplh_s',1e12)],
 ['tp xấu nhất (ps)',F('and.tpmax',1e12),F('ha14.tpmax_c',1e12),F('ha14.tpmax_s',1e12)],
 ['tr / tf (ps)',F('and.tr',1e12)+' / '+F('and.tf',1e12),F('ha14.tr_c',1e12)+' / '+F('ha14.tf_c',1e12),F('ha14.tr_s',1e12)+' / '+F('ha14.tf_s',1e12)],
 ['VOH / VOL (V)',F('and.voh',1,'{:.3f}')+' / '+F('and.vol',1,'{:.3f}'),F('ha14.voh_c',1,'{:.3f}')+' / '+F('ha14.vol_c',1,'{:.3f}'),F('ha14.voh_s',1,'{:.3f}')+' / '+F('ha14.vol_s',1,'{:.3f}')]],size=13,rowh=0.42)
table(s,0.4,4.0,9.2,[34,33,33],[['Công suất','Cổng AND','Half Adder 14T'],['Pavg (µW), A: '+F('setup.va_freq',1e-6,'{:g}',' MHz')+', B: '+F('setup.vb_freq',1e-6,'{:g}',' MHz'),F('and.pavg',1e6,'{:.2f}'),F('ha14.pavg',1e6,'{:.2f}')],
 ['Pstatic (nW), TB 4 tổ hợp, '+F('setup.temp',1,'{:g}',' °C'),F('and.pstatic',1e9,'{:.2f}'),F('ha14.pstatic',1e9,'{:.2f}')],['PDP = Pavg · tp xấu nhất (fJ)',F('and.pdp',1e15,'{:.3f}'),F('ha14.pdp',1e15,'{:.3f}')]],size=13,rowh=0.42)
cite(s,'Số liệu từ meas và op của ngspice; VOH ≈ VDD, VOL ≈ 0: full swing của static CMOS (ECE4740 – Lecture 10 / page 23)')

# ---------- 20 compare
s=new('So sánh Half Adder 14T với cách cơ bản 18T','Đây là đánh đổi số transistor và công suất với delay.')
table(s,0.4,1.2,9.2,[40,30,30],[['Tiêu chí','Cơ bản 18T','Đề xuất 14T'],['Số transistor','18','14 (−22%)'],['Số tầng trên đường Sum','2 (INV → AOI22)','3 (NAND2 → OAI21 → INV)'],['tp Sum xấu nhất (ps)',F('ha18.tpmax_s',1e12),F('ha14.tpmax_s',1e12)],['Pavg (µW)',F('ha18.pavg',1e6,'{:.2f}'),F('ha14.pavg',1e6,'{:.2f}')],['PDP (fJ)',F('ha18.pdp',1e15,'{:.3f}'),F('ha14.pdp',1e15,'{:.3f}')]],size=13,rowh=0.45)
cmp_txt=['Kỳ vọng: 14T có ít điện dung chuyển mạch hơn nên công suất động thấp hơn, vì P tỉ lệ với Σ αk·Ck. Đường Sum dài hơn một tầng nên delay cần được kiểm chứng bằng mô phỏng.']
if G('ha14.pavg') and G('ha18.pavg') and G('ha14.tpmax_s') and G('ha18.tpmax_s'):
    dp=(G('ha14.pavg')/G('ha18.pavg')-1)*100; dt=(G('ha14.tpmax_s')-G('ha18.tpmax_s'))*1e12
    cmp_txt.append(('Kết quả mô phỏng: Pavg của 14T %s %.1f%% so với 18T; tp Sum xấu nhất %s %.1f ps'%('thấp hơn' if dp<0 else 'cao hơn',abs(dp),'chậm hơn' if dt>0 else 'nhanh hơn',abs(dt))).replace('.',',')+'.')
card(s,0.4,4.2,9.2,1.95,cmp_txt,size=14,accent=RED)
cite(s,'(ECE4740 – Lecture 7 / page 7)')

# ---------- 21 evaluation
s=new('Nhận xét các điểm đạt và chưa đạt','tp phụ thuộc VDD: L5 slide 182 trang 11. Glitch: L5 slide 168 trang 4. Rò theo nhiệt độ: L8 slide 255 trang 3. Logical effort: L12 slide 443–454. Mọi số liệu lấy từ results.json.')
def pct(a,b):
    return None if G(a) is None or G(b) is None else (G(a)/G(b)-1)*100
def num(v,fmt):
    return '[__]' if v is None else fmt.format(v).replace('.',',')
def glitch_txt(c):
    g=G(c+'.glitch_sum'); vil=next((b.get('vil') for b in (G('vtc') or []) if b.get('k')==G('k')),None)
    if g is None: return '[__]'
    if g<0.05*1.8: return 'không có glitch (lệch tối đa '+num(g*1e3,'{:.0f}')+' mV)'
    if vil is not None and g<vil: return 'có gai '+num(g,'{:.2f}')+' V, dưới VIL = '+num(vil,'{:.2f}')+' V nên không gây lỗi logic'
    return 'có glitch '+num(g,'{:.2f}')+' V'
dP=pct('ha14.pavg','ha18.pavg'); dPDP=pct('ha14.pdp','ha18.pdp')
dT=None if G('ha14.tpmax_s') is None or G('ha18.tpmax_s') is None else (G('ha14.tpmax_s')-G('ha18.tpmax_s'))*1e12
func=all(G(c+'.func_ok') for c in ('and','ha14','ha18'))
ok_items=['Giảm Half Adder từ 18 xuống 14 transistor; Pavg '+('thấp' if (dP or 0)<0 else 'cao')+' hơn 18T '+num(abs(dP) if dP is not None else None,'{:.1f}')+'% ('+F('ha14.pavg',1e6,'{:.2f}')+' so với '+F('ha18.pavg',1e6,'{:.2f}')+' µW), PDP '+('thấp' if (dPDP or 0)<0 else 'cao')+' hơn '+num(abs(dPDP) if dPDP is not None else None,'{:.1f}')+'%.',
 ('Waveform khớp bảng chân lý ở cả 4 tổ hợp' if func else '[Chức năng chưa khớp bảng chân lý, xem logs/check_report.md]')+'; full swing, VOH = '+F('ha14.voh_s',1,'{:.3f}')+' V, VOL ≈ 0 V (L10 p.23).',
 'A, B đổi cùng lúc (2 ns, 4 ns): Sum 14T '+glitch_txt('ha14')+'; 18T '+glitch_txt('ha18')+' (L5 p.4).',
 'Mọi cell có Euler path chung, diffusion liền mạch (L11 p.2).']
bad_items=['tp Sum xấu nhất của 14T là '+F('ha14.tpmax_s',1e12)+' ps, '+('chậm' if (dT or 0)>0 else 'nhanh')+' hơn 18T ('+F('ha18.tpmax_s',1e12)+' ps) '+num(abs(dT) if dT is not None else None,'{:.1f}')+' ps; Sum qua 3 tầng nên chậm hơn Carry ('+F('ha14.tpmax_c',1e12)+' ps).',
 'Mới dừng ở stick diagram, chưa có layout thật, DRC và LVS.',
 'Chuỗi kích thích chỉ có 4 trong 12 chuyển trạng thái; chưa khảo sát theo VDD và nhiệt độ (L5 p.11; L8 p.3).',
 'Sizing theo quy tắc tay, chưa tối ưu bằng logical effort (L12).']
card(s,0.4,1.2,4.5,4.95,[('Đạt',{'size':17,'bold':True,'color':BLUE})]+ok_items,size=13,accent=BLUE)
card(s,5.1,1.2,4.5,4.95,[('Chưa đạt / hạn chế',{'size':17,'bold':True,'color':RED})]+bad_items,size=13,accent=RED)
cite(s,'(ECE4740 – Lecture 5 / page 4, 11); (Lecture 8 / page 3); (Lecture 10 / page 23); (Lecture 11 / page 2)')

# ---------- 22 conclusion (red side-panel layout)
s=prs.slides.add_slide(LAY_END)
for sh in list(s.placeholders):
    if sh.placeholder_format.idx==0: sh.text='KẾT LUẬN'
    elif sh.placeholder_format.idx==13:
        tf=sh.text_frame; tf.text=''
        items=[('Half Adder static CMOS 14 transistor: ít hơn 22% so với cách cơ bản, full swing, layout liền diffusion.',True),
               ('Hướng phát triển 1: vẽ layout thật, chạy DRC và LVS.',False),('Hướng phát triển 2: sizing lại bằng logical effort cho đường Sum.',False),
               ('Hướng phát triển 3: khảo sát theo VDD, nhiệt độ và process corner.',False)]
        for i,(t,b) in enumerate(items):
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph(); p.space_after=Pt(14)
            runs(p,t,18 if b else 15,RED if b else DARK,b)
s.shapes._spTree.append(copy.deepcopy(sldnum_el))
s.notes_slide.notes_text_frame.text='Tóm tắt một câu cho hội đồng, sau đó nêu ba hướng phát triển.'

# ---------- 23 references
s=new('Tài liệu tham khảo','Số trang trích dẫn đã đối chiếu với file PDF bài giảng: mỗi trang PDF chứa hai slide.')
tb(s,0.4,1.25,9.2,4.9,['**[1]** ECE4740 Digital VLSI Design, Cornell University, slide bài giảng (6/8/2018):',
 '      Lecture 2: Diodes and MOSFET · Lecture 4: The CMOS inverter','      Lecture 5: Dynamic behavior of inverter · Lecture 6: Inverter sizing',
 '      Lecture 7: Power consumption · Lecture 8: Static power consumption and CMOS fabrication','      Lecture 10: Static CMOS design · Lecture 11: More CMOS logic · Lecture 12: CMOS logic sizing',
 '**[2]** SkyWater SKY130 PDK, cài qua open_pdks (R. T. Edwards): github.com/RTimothyEdwards/open_pdks', '**[3]** D-curs-D, Inverter design and analysis using sky130 PDK: github.com/D-curs-D/Inverter-design-and-analysis-using-sky130pdk','Hình VTC, stick diagram, sơ đồ khối và floorplan: nhóm tự vẽ.'],size=14,space=10)
cite(s,'Trích dẫn trong slide theo dạng (ECE4740 – Lecture X / page Y), số trang là trang PDF của file bài giảng',GREY)

# ---------- order: cover, content..., thank you last
ids=list(lst)
cover=[i for i in ids if prs.part.related_part(i.rId) is title_slide.part][0]
thanks=[i for i in ids if prs.part.related_part(i.rId) is thanks_slide.part][0]
lst.remove(cover); lst.insert(0,cover); lst.remove(thanks); lst.append(thanks)
from pptx.opc.packuri import PackURI
for k,sid in enumerate(lst):
    prs.part.related_part(sid.rId).partname=PackURI(f'/ppt/slides/slide{k+1}.xml')
os.makedirs(os.path.join(ROOT,'output'),exist_ok=True); OUT=os.path.join(ROOT,'output','BTL_VLSI_AND_HalfAdder_HUST.pptx'); prs.save(OUT); print('Da ghi',OUT); 
