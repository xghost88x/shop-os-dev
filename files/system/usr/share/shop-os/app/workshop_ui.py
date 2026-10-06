"""Native Qt workshop styling: scalable artwork and chamfered controls."""
import math
from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QFrame, QToolButton, QWidget


def chamfer(rect, cut=14):
    x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
    path = QPainterPath(QPointF(x + cut, y))
    for px, py in [(x+w-cut,y),(x+w,y+cut),(x+w,y+h-cut),
                   (x+w-cut,y+h),(x+cut,y+h),(x,y+h-cut),(x,y+cut)]:
        path.lineTo(px, py)
    path.closeSubpath()
    return path


def gradient(rect, colors):
    g = QLinearGradient(rect.topLeft(), rect.bottomLeft())
    for pos, color in colors:
        g.setColorAt(pos, QColor(color))
    return g


STEEL = [(0,'#f3f3ed'),(.25,'#b9bfc3'),(.48,'#545b60'),(.7,'#92999d'),(1,'#d8dcdd')]
ORANGE = [(0,'#ff9150'),(.2,'#ff4d17'),(.65,'#df300d'),(1,'#8a1c09')]


def texture(p, rect):
    p.save()
    p.setClipRect(rect)
    p.setPen(QPen(QColor(255,255,255,7), 1))
    for y in range(int(rect.top()), int(rect.bottom()), 5):
        p.drawLine(QPointF(rect.left(),y), QPointF(rect.right(),y))
    p.setPen(QPen(QColor(0,0,0,45), 1))
    for x in range(int(rect.left()), int(rect.right()), 9):
        p.drawLine(QPointF(x,rect.top()), QPointF(x+rect.height(),rect.bottom()))
    p.restore()


def metal_path(p, path, orange=False, width=1.6):
    p.setPen(QPen(QColor('#ff9a66' if orange else '#d1d6d8'), width))
    p.setBrush(gradient(QRectF(0,0,160,160), ORANGE if orange else STEEL))
    p.drawPath(path)


def wrench(p, x, y, angle=0, scale=1):
    p.save()
    p.translate(x,y)
    p.rotate(angle)
    p.scale(scale,scale)
    path=QPainterPath(QPointF(-8,16))
    path.lineTo(-8,83)
    path.cubicTo(-26,98,-10,117,4,107)
    path.cubicTo(16,100,11,88,5,83)
    path.lineTo(5,16)
    path.cubicTo(29,5,22,-23,10,-26)
    path.lineTo(12,-5)
    path.lineTo(-4,3)
    path.lineTo(-18,-8)
    path.lineTo(-15,-28)
    path.cubicTo(-39,-17,-32,8,-8,16)
    path.closeSubpath()
    metal_path(p,path)
    p.setBrush(QColor('#111518'))
    p.drawEllipse(QRectF(-7,92,9,9))
    p.restore()


def module_art(p, number):
    """All artwork is code-native and independent of the desktop icon theme."""
    p.save()
    p.setRenderHint(QPainter.Antialiasing)
    if number == 1:
        pages=QPainterPath()
        pages.moveTo(29,37); pages.lineTo(112,20); pages.lineTo(140,114)
        pages.lineTo(56,141); pages.lineTo(22,119); pages.closeSubpath()
        metal_path(p,pages)
        cover=QPainterPath()
        cover.moveTo(24,28); cover.lineTo(109,12); cover.lineTo(140,105)
        cover.lineTo(53,129); cover.lineTo(20,108); cover.closeSubpath()
        p.setPen(QPen(QColor('#ff5b23'),3)); p.setBrush(QColor('#1e252a')); p.drawPath(cover)
        p.setPen(QPen(QColor('#afbabf'),1.5))
        for y in [117,121,125]: p.drawLine(QPointF(57,y),QPointF(131,y-23))
        stripe=QPainterPath(QPointF(97,16)); stripe.lineTo(110,14); stripe.lineTo(137,103)
        stripe.lineTo(123,108); stripe.closeSubpath(); metal_path(p,stripe,True)
        wrench(p,78,51,-40,.47)
    elif number == 2:
        gear=QPainterPath()
        for i in range(80):
            a=i*math.tau/80
            r=62 if i%8 in [0,1,2,3] else 49
            point=QPointF(77+math.cos(a)*r,74+math.sin(a)*r)
            if i==0: gear.moveTo(point)
            else: gear.lineTo(point)
        gear.closeSubpath(); metal_path(p,gear)
        p.setBrush(QColor('#11171b')); p.setPen(QPen(QColor('#373f44'),2)); p.drawEllipse(QRectF(43,40,68,68))
        p.setBrush(Qt.NoBrush); p.setPen(QPen(QColor('#ff4c16'),10)); p.drawEllipse(QRectF(49,46,56,56))
        p.setPen(QPen(QColor('#f2f4f5'),2)); p.drawEllipse(QRectF(44,41,66,66))
        p.setPen(QPen(QColor('#737c82'),12,Qt.SolidLine,Qt.RoundCap)); p.drawLine(QPointF(105,105),QPointF(132,132))
        p.setPen(QPen(QColor('#ff4b18'),8,Qt.SolidLine,Qt.RoundCap)); p.drawLine(QPointF(116,116),QPointF(138,138))
    elif number == 3:
        screen=QPainterPath(); screen.addRoundedRect(QRectF(17,22,126,92),8,8); metal_path(p,screen)
        p.setPen(QPen(QColor('#50595f'),2)); p.setBrush(QColor('#101619')); p.drawRoundedRect(QRectF(24,29,112,77),3,3)
        base=QPainterPath(QPointF(18,117)); base.lineTo(142,117); base.lineTo(158,132)
        base.lineTo(2,132); base.closeSubpath(); metal_path(p,base)
        p.setBrush(Qt.NoBrush); p.setPen(QPen(QColor('#ff501c'),8,Qt.SolidLine,Qt.RoundCap))
        for r in [29,47]: p.drawArc(QRectF(80-r,83-r,2*r,2*r),40*16,100*16)
        p.setBrush(QColor('#ff511b')); p.setPen(QPen(QColor('#ff9865'),1)); p.drawEllipse(QRectF(73,79,14,12))
    elif number == 4:
        frame=QPainterPath(); frame.addRoundedRect(QRectF(16,16,128,125),9,9); metal_path(p,frame)
        p.setBrush(QColor('#11191e')); p.setPen(QPen(QColor('#56616a'),2)); p.drawRoundedRect(QRectF(23,23,114,111),4,4)
        p.setPen(QPen(QColor('#39444c'),1))
        for x in range(35,137,17): p.drawLine(QPointF(x,24),QPointF(x,133))
        for y in range(36,134,17): p.drawLine(QPointF(24,y),QPointF(136,y))
        pulse=QPainterPath(QPointF(27,85))
        for x,y in [(47,85),(56,63),(67,109),(82,38),(98,121),(109,70),(117,85),(134,85)]: pulse.lineTo(x,y)
        p.setBrush(Qt.NoBrush); p.setPen(QPen(QColor('#7c220d'),8)); p.drawPath(pulse)
        p.setPen(QPen(QColor('#ff641f'),4,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin)); p.drawPath(pulse)
    elif number == 5:
        p.setBrush(Qt.NoBrush)
        for color,start in [('#ff511b',25),('#c9cfd3',205)]:
            p.setPen(QPen(QColor('#070a0b'),23)); p.drawArc(QRectF(26,25,108,108),start*16,135*16)
            p.setPen(QPen(QColor(color),17)); p.drawArc(QRectF(26,21,108,108),start*16,135*16)
        a=QPainterPath(QPointF(124,24)); a.lineTo(146,61); a.lineTo(105,64); a.closeSubpath(); metal_path(p,a,True)
        a=QPainterPath(QPointF(36,135)); a.lineTo(14,98); a.lineTo(55,95); a.closeSubpath(); metal_path(p,a)
    elif number == 6:
        wrench(p,104,35,42,.9)
        p.save(); p.translate(42,126); p.rotate(-42)
        shaft=QPainterPath(); shaft.addRect(QRectF(-4,-99,8,66)); metal_path(p,shaft)
        tip=QPainterPath(QPointF(-4,-99)); tip.lineTo(-8,-111); tip.lineTo(5,-124); tip.lineTo(11,-113); tip.lineTo(4,-99); tip.closeSubpath(); metal_path(p,tip)
        handle=QPainterPath(); handle.addRoundedRect(QRectF(-12,-36,24,53),6,6); metal_path(p,handle,True)
        p.setPen(QPen(QColor('#7b200d'),3)); p.drawLine(QPointF(-5,-24),QPointF(-5,7)); p.drawLine(QPointF(5,-24),QPointF(5,7))
        p.restore()
    p.restore()


class WorkshopTile(QToolButton):
    def __init__(self, title, number, parent=None):
        super().__init__(parent)
        self.title, self.number = title, number
        self.setText(title)
        self.setAccessibleName(f'{number:02d} {title}')
        self.setMinimumSize(245,190)
        self.setMouseTracking(True)

    def sizeHint(self):
        return QSize(340,235)

    def enterEvent(self,event):
        super().enterEvent(event); self.update()

    def leaveEvent(self,event):
        super().leaveEvent(event); self.update()

    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        r=QRectF(self.rect()).adjusted(4,4,-4,-7)
        p.setBrush(QColor('#08090a')); p.setPen(Qt.NoPen); p.drawPath(chamfer(r.translated(0,4)))
        p.setPen(QPen(QColor('#ff6327' if self.underMouse() or self.hasFocus() else '#85311b'),2))
        p.setBrush(gradient(r,[(0,'#777f84'),(.09,'#252b2f'),(.8,'#111619'),(1,'#42494d')]))
        p.drawPath(chamfer(r,17))
        inside=r.adjusted(6,6,-6,-6)
        p.setPen(QPen(QColor('#687278'),1)); p.setBrush(gradient(inside,[(0,'#1c2327'),(1,'#0b0f11')]))
        p.drawPath(chamfer(inside,13))
        p.save(); p.setClipPath(chamfer(inside,13)); texture(p,inside); p.restore()
        tab=QPainterPath(QPointF(r.left()+17,r.top()+3))
        for x,y in [(r.left()+91,r.top()+3),(r.left()+72,r.top()+44),(r.left()+5,r.top()+44),(r.left()+5,r.top()+17)]: tab.lineTo(x,y)
        tab.closeSubpath(); p.setPen(QPen(QColor('#ffad76'),1)); p.setBrush(gradient(r,ORANGE)); p.drawPath(tab)
        p.setFont(QFont('DejaVu Sans',21,QFont.Black,True)); p.setPen(QColor('#090b0d'))
        p.drawText(QRectF(r.left()+12,r.top()+4,65,37),Qt.AlignCenter,f'{self.number:02d}')
        art_size=min(self.height()-76,self.width()*.53,164)
        p.save(); p.translate((self.width()-art_size)/2, max(24,(self.height()-art_size-48)/2))
        if self.isDown(): p.translate(0,2)
        p.scale(art_size/160,art_size/160); module_art(p,self.number); p.restore()
        font=QFont('DejaVu Sans',21,QFont.Black)
        font.setStretch(QFont.Condensed)
        p.setFont(font)
        while p.fontMetrics().horizontalAdvance(self.title)>self.width()-30 and font.pointSize()>10:
            font.setPointSize(font.pointSize()-1); p.setFont(font)
        label=QRectF(12,self.height()-49,self.width()-24,36)
        p.setPen(QColor('#000000')); p.drawText(label.translated(1,2),Qt.AlignCenter,self.title)
        p.setPen(QColor('#f1f1ec')); p.drawText(label,Qt.AlignCenter,self.title)
        if self.hasFocus():
            p.setPen(QPen(QColor('#ff9c62'),2,Qt.DashLine)); p.setBrush(Qt.NoBrush)
            p.drawPath(chamfer(r.adjusted(10,10,-10,-10)))


class WorkshopPanel(QFrame):
    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        r=QRectF(self.rect()).adjusted(1,1,-1,-1)
        p.setPen(QPen(QColor('#5b3325'),2)); p.setBrush(gradient(r,[(0,'#202326'),(1,'#101315')]))
        p.drawPath(chamfer(r,18)); texture(p,r.adjusted(4,4,-4,-4))
        for x in [12,self.width()-12]:
            for y in [12,self.height()-12]:
                p.setBrush(QColor('#080b0c')); p.setPen(QPen(QColor('#41484b'),1))
                p.drawEllipse(QPointF(x,y),3,3)


class BrandTitle(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent); self.setMinimumSize(330,116)
        self.setAccessibleName("John's Garage")

    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        font=QFont('DejaVu Sans',48,QFont.Black,True)
        font.setStretch(QFont.Condensed)
        p.setFont(font)
        while p.fontMetrics().horizontalAdvance("GARAGE")>self.width()-8 and font.pointSize()>20:
            font.setPointSize(font.pointSize()-1); p.setFont(font)
        h=self.height()/2
        for text,y,colors in [("JOHN'S",0,STEEL),("GARAGE",h,ORANGE)]:
            path=QPainterPath(); path.addText(QPointF(4,y+h-6),font,text)
            p.setPen(QPen(QColor('#07090a'),4)); p.setBrush(QColor('#07090a')); p.drawPath(path.translated(2,3))
            p.setPen(QPen(QColor('#f3b491' if y else '#dbe0e1'),.7))
            p.setBrush(gradient(QRectF(0,y,self.width(),h),colors)); p.drawPath(path)
