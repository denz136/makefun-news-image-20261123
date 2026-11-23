#!/usr/bin/env python3
"""One-image summary of Monday 23 November 2026's world news -> /output/entry.png.

Pure stdlib.   MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import math, os, struct, zlib

W = H = 1024
BG=(11,16,26); CARD=(21,29,44); EDGE=(40,52,74); INK=(240,246,252); DIM=(172,188,208)
RED=(232,72,66); ORANGE=(242,148,58); BLUE=(72,146,238); GREEN=(76,192,128)
YELLOW=(240,208,90); SLATE=(96,104,120); WATER=(52,84,136)

pix = bytearray()
row0 = bytearray(BG) * W
for _ in range(H): pix += row0
CLIP = None

def px(x,y,c):
    if 0<=x<W and 0<=y<H:
        if CLIP and not (CLIP[0]<=x<CLIP[2] and CLIP[1]<=y<CLIP[3]): return
        i=(y*W+x)*3; pix[i]=c[0]; pix[i+1]=c[1]; pix[i+2]=c[2]

def box(x0,y0,x1,y1,c):
    x0=max(0,int(x0)); y0=max(0,int(y0)); x1=min(W,int(x1)); y1=min(H,int(y1))
    if x1<=x0 or y1<=y0: return
    r=bytearray(c)*(x1-x0)
    for y in range(y0,y1): pix[(y*W+x0)*3:(y*W+x0)*3+len(r)]=r

def seg(x0,y0,x1,y1,c,w=2):
    x0,y0,x1,y1=map(int,(x0,y0,x1,y1))
    n=max(abs(x1-x0),abs(y1-y0)) or 1; h=w//2
    for i in range(n+1):
        x=x0+(x1-x0)*i//n; y=y0+(y1-y0)*i//n
        for oy in range(-h,h+1):
            for ox in range(-h,h+1): px(x+ox,y+oy,c)

def blend(a,b,t):
    return tuple(int(a[k]+(b[k]-a[k])*t) for k in range(3))

def ring(cx,cy,r,c,w=2):
    steps=max(12,int(r*2.5))
    for i in range(steps):
        a=6.2832*i/steps
        for t in range(w):
            rr=r+t-w/2
            px(int(cx+rr*math.cos(a)),int(cy+rr*math.sin(a)),c)

def blob(cx,cy,r,c):
    for y in range(int(cy-r),int(cy+r)+1):
        for x in range(int(cx-r),int(cx+r)+1):
            if (x-cx)**2+(y-cy)**2<=r*r: px(x,y,c)

def vec(x0,y0,x1,y1,c,w=2):
    seg(x0,y0,x1,y1,c,w)
    ang=math.atan2(y1-y0,x1-x0)
    for s in (2.6,-2.6):
        seg(x1,y1,x1-9*math.cos(ang+s/2.4),y1-9*math.sin(ang+s/2.4),c,w)

# ---- 5x7 glyphs -----------------------------------------------------------
G={
'0':("111","101","101","101","111"),'1':("010","110","010","010","111"),
'2':("111","001","111","100","111"),'3':("111","001","111","001","111"),
'4':("101","101","111","001","001"),'5':("111","100","111","001","111"),
'6':("111","100","111","101","111"),'7':("111","001","010","010","010"),
'8':("111","101","111","101","111"),'9':("111","101","111","001","111"),
'A':("111","101","111","101","101"),'B':("110","101","110","101","110"),
'C':("111","100","100","100","111"),'D':("110","101","101","101","110"),
'E':("111","100","111","100","111"),'F':("111","100","111","100","100"),
'G':("111","100","101","101","111"),'H':("101","101","111","101","101"),
'I':("111","010","010","010","111"),'J':("001","001","001","101","111"),
'K':("101","101","110","101","101"),'L':("100","100","100","100","111"),
'M':("101","111","111","101","101"),'N':("110","101","101","101","101"),
'O':("111","101","101","101","111"),'P':("111","101","111","100","100"),
'Q':("111","101","101","111","011"),'R':("111","101","110","101","101"),
'S':("111","100","111","001","111"),'T':("111","010","010","010","010"),
'U':("101","101","101","101","111"),'V':("101","101","101","101","010"),
'W':("101","101","111","111","101"),'X':("101","101","010","101","101"),
'Y':("101","101","010","010","010"),'Z':("111","001","010","100","111"),
' ':("000","000","000","000","000"),'.':("000","000","000","000","010"),
',':("000","000","000","010","100"),':':("000","010","000","010","000"),
'-':("000","000","111","000","000"),'/':("001","001","010","100","100"),
'!':("010","010","010","000","010"),"'":("010","010","000","000","000"),
'%':("101","001","010","100","101"),'+':("000","010","111","010","000"),
'$':("111","110","111","011","111"),'"':("101","101","000","000","000"),
'(':("010","100","100","100","010"),')':("010","001","001","001","010"),
}

def tw(s,sc): return len(s)*6*sc

def txt(s,x,y,c,sc=2):
    cx=x
    for ch in s.upper():
        g=G.get(ch,G[' '])
        for gy,rw in enumerate(g):
            for gx,v in enumerate(rw):
                if v=='1': box(cx+gx*sc,y+gy*sc,cx+gx*sc+sc,y+gy*sc+sc,c)
        cx+=6*sc

def fit(s,mw,p):
    sc=p
    while sc>1 and tw(s,sc)>mw: sc-=1
    return sc

# ---- masthead -------------------------------------------------------------
box(0,0,W,124,(8,12,20)); box(0,124,W,127,RED)
txt('WORLD NEWS',44,22,INK,7)
txt('MONDAY 23 NOVEMBER 2026',46,78,(150,186,232),4)

# ---- lead panels ----------------------------------------------------------
PX,PY,PW,PH,GX,GY=36,140,464,340,24,14
LEADS=[
 ('MIDDLE EAST',RED,"GULF WAR ESCALATES",
  ["HOUTHIS CLAIM HIT ON SAUDI RABIGH","REFINERY; IRGC STRIKES US RADARS",
   "IN BAHRAIN, DOWNS A PREDATOR OVER","HORMUZ; TRUMP THREATENS NEW YEAR"]),
 ('UKRAINE',ORANGE,"DYMER TOLL RISES TO NINE",
  ["RUSSIAN DRONE FLATTENS FLATS NEAR","KYIV; 12 DEAD IN REGION OVERNIGHT;",
   "A CHILD PULLED OUT ALIVE; MERKURY","CORVETTE SUNK OFF BENGHAZI"]),
 ('MARKETS',BLUE,"AI ROUT SHAKES ASIA",
  ["KOSPI -5 PCT: SEOUL SWITCHES ON ITS","STABILISATION FUND; TOKYO CLOSED",
   "FOR LABOR THANKSGIVING; NASDAQ","LOST 10 PCT LAST WEEK; OIL $92"]),
 ('CLIMATE',GREEN,"COP31 ENDS WITH NO PACT",
  ["ANTALYA TALKS COLLAPSE OVER FOSSIL","FUEL PHASE-OUT WORDING; LONGEST",
   "COP EVER CLOSES EMPTY-HANDED;","GUTERRES: SCIENCE HAS NO AMBIGUITY"]),
# rev2: briefs extended, COP headline tightened
]
arts=[]
for i,(kick,col,head,body) in enumerate(LEADS):
    x=PX+(i%2)*(PW+GX); y=PY+(i//2)*(PH+GY)
    box(x,y,x+PW,y+PH,CARD); box(x,y,x+PW,y+3,EDGE); box(x,y,x+3,y+PH,EDGE)
    kw=tw(kick,2)+20
    box(x+16,y+12,x+16+kw,y+30,col); txt(kick,x+26,y+18,(14,18,28),2)
    hy=y+42
    for ln in [head][:1]:
        hs=fit(ln,PW-40,3)
        txt(ln,x+18,hy,INK,hs); hy+=7*hs+8
    box(x+18,hy,x+PW-20,hy+2,(50,64,90)); hy+=10
    for ln in body:
        txt(ln,x+18,hy,DIM,2); hy+=19
    arts.append((i,x,y))

AZ=196

# P1 gulf map
i,x,y=arts[0]; CLIP=(x+4,y+AZ,x+PW-4,y+PH-4)
gx,gy=x+222,y+AZ
box(gx,gy,gx+232,gy+150,(26,36,54))
for k in range(58): box(gx+18+k,gy+26+k,gx+28+k,gy+126-k,WATER)
txt('GULF',gx+28,gy+66,(150,190,240),2)
box(gx+146,gy+12,gx+224,gy+142,(42,50,42)); txt('IRAN',gx+156,gy+62,(168,180,150),2)
blob(gx+156,gy+30,7,RED); txt('QESHM',gx+166,gy+22,RED,1)
blob(gx+48,gy+40,7,RED); txt('BAHRAIN',gx-6,gy+52,RED,1)
blob(gx+36,gy+102,8,ORANGE); txt('RABIGH',gx-8,gy+114,ORANGE,1)
vec(gx+138,gy+34,gx+56,gy+42,RED,3); vec(gx+130,gy+44,gx+50,gy+100,RED,3)
txt('REFINERY + RADARS HIT',gx+26,gy+130,YELLOW,1)

# P2 collapsed block
i,x,y=arts[1]; CLIP=(x+4,y+AZ,x+PW-4,y+PH-4)
bx,by=x+20,y+AZ+2
box(bx,by+10,bx+176,by+134,(62,70,86))
for r in range(5):
    box(bx+8,by+20+r*20,bx+168,by+26+r*20,(32,40,56))
    for wq in range(0,150,24): box(bx+14+wq,by+20+r*20,bx+30+wq,by+26+r*20,YELLOW)
for k in range(64):
    box(bx+186+k,by+134-int(k*0.85),bx+424,by+134,blend((100,88,74),(38,34,30),k/64))
box(bx+186,by+86,bx+424,by+134,(52,46,42))
for rx in (bx+216,bx+256,bx+306):
    box(rx,by+114,rx+10,by+130,ORANGE); blob(rx+5,by+110,7,ORANGE)
txt('DYMER, KYIV REGION',bx+228,by+2,(238,132,98),2)
txt('RESCUE ONGOING',bx+240,by+138,DIM,1)

# P3 markets chart
i,x,y=arts[2]; CLIP=(x+4,y+AZ,x+PW-4,y+PH-4)
cx,cy=x+28,y+AZ+6
box(cx,cy,cx+408,cy+140,(22,28,42))
pts=[(0,20),(56,38),(112,32),(168,60),(224,68),(280,104),(336,124),(404,118)]
for k in range(len(pts)-1):
    seg(cx+pts[k][0],cy+pts[k][1],cx+pts[k+1][0],cy+pts[k+1][1],RED,3)
txt('KOSPI -5 PCT',cx+12,cy+6,INK,3)
txt('STABILISATION FUND ON',cx+12,cy+94,BLUE,2)
txt('NASDAQ -10 PCT WK',cx+268,cy+62,ORANGE,2)

# P4 COP31
i,x,y=arts[3]; CLIP=(x+4,y+AZ,x+PW-4,y+PH-4)
gx,gy=x+330,y+AZ+68
ring(gx,gy,54,GREEN,4); ring(gx,gy,34,(46,92,72),2)
box(gx-20,gy-26,gx-2,gy-12,(52,110,84)); box(gx+2,gy-30,gx+22,gy-18,(52,110,84))
box(gx-12,gy+4,gx+8,gy+18,(52,110,84)); box(gx+12,gy+10,gx+24,gy+24,(52,110,84))
txt('COP31',x+44,gy+10,GREEN,3)

seg(gx-60,gy-40,gx-20,gy-6,RED,4); seg(gx-16,gy+2,gx-40,gy+28,RED,4)
txt('NO DEAL',x+48,gy-46,RED,4)
txt('FOSSIL FUEL DEADLOCKED',x+36,gy+58,DIM,2)
txt('LONGEST COP ON RECORD',x+40,gy+74,(112,128,152),1)

# ---- briefs ---------------------------------------------------------------
CLIP=None
BRIEFS=[
 ('ME','IRGC DOWNS US PREDATOR, HORMUZ',RED),
 ('ME','UKMTO FLAGS TANKER INCIDENT, OMAN',RED),
 ('ME','EGYPT: SUEZ LOST $20BN TO WAR',RED),
 ('UA','CORVETTE SUNK OFF BENGHAZI',ORANGE),
 ('AS','AI-CHIP CURBS HIT CHINA STOCKS',BLUE),
 ('AS','KOSPI BREAKS BELOW 5,000',BLUE),
 ('AS','TAIWAN TIGHTENS SHORT-SELLING',BLUE),
 ('AF','THAILAND TO BAN RARE-EARTH EXPORTS',YELLOW),
   ('AM','PELTOLA FLIPS ALASKA SENATE SEAT',BLUE),
]
BY0=PY+2*PH+GY+12
for i,(tag,t,col) in enumerate(BRIEFS):
    bxx=36+(i%2)*472; byy=BY0+(i//2)*24
    box(bxx,byy,bxx+448,byy+1,(44,56,76))
    txt(tag,bxx+6,byy+7,col,2); txt(t,bxx+42,byy+7,DIM,2)

# ---- ticker ---------------------------------------------------------------
FY=BY0+5*24+10
box(36,FY,988,FY+46,CARD); box(36,FY,988,FY+3,RED)
txt('GULF WAR: SHIPS HIT NEAR HORMUZ, BRENT HOLDS $92.29',52,FY+13,YELLOW,2)
txt('SOURCES: REUTERS AP AFP BBC GUARDIAN | AI AGENT FOR MAKE.FUN',52,FY+32,(120,134,156),1)
txt('GULF WAR: SHIPS HIT NEAR HORMUZ, BRENT HOLDS $92.29',52,FY+13,YELLOW,2)


# ---- encode ---------------------------------------------------------------
def chunk(tag,data):
    body=tag+data
    return struct.pack('>I',len(data))+body+struct.pack('>I',zlib.crc32(body)&0xFFFFFFFF)

raw=bytearray()
for y in range(H):
    raw.append(0); raw+=pix[y*W*3:(y+1)*W*3]
png=b'\x89PNG\r\n\x1a\n'
png+=chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))
png+=chunk(b'IDAT',zlib.compress(bytes(raw),9))
png+=chunk(b'IEND',b'')

od=os.environ.get('MAKEFUN_OUTPUT_DIR','/output')
os.makedirs(od,exist_ok=True)
open(os.path.join(od,'entry.png'),'wb').write(png)
