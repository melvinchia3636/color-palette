#TODO: crosshair light dark
#TODO: HSV auto adjust
#TODO: color picker auto adjust

from tkinter import *
import tkinter.ttk as ttk
from tkinter.font import Font
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
import colorsys
import math

#convert RGB to HEX 
def rgb_to_hex(rgb):
    return '#%02X%02X%02X' % (int(rgb[0]), int(rgb[1]), int(rgb[2]))

#convert HSV to RGB
def hsv_to_rgb(h, s, v):
        if s == 0.0: v*=255; return (v, v, v)
        i = int(h*6.)
        f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
        if i == 0: return (v, t, p)
        if i == 1: return (q, v, p)
        if i == 2: return (p, v, t)
        if i == 3: return (p, q, v)
        if i == 4: return (t, p, v)
        if i == 5: return (v, p, q)

def rgb_to_hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df/mx)*100
    v = mx*100
    return h/360, s/100, v/100

class ColorPalette(ThemedTk):
    def __init__(self):
        #parent initialize
        super(ColorPalette, self).__init__(theme='breeze', background='#f0f0f0')

        #window configurations
        self.geometry('630x430')
        self.title('Color Picker')
        self.resizable(False, False)

        #non-widget variables initialization
        self.curr_hue = 0
        self.current_corr = [359, 1]
        self.current_hsv = [DoubleVar(value=i) for i in (0, 1, 1)]
        self.current_rgb = [IntVar(value=i) for i in hsv_to_rgb(*(i.get() for i in self.current_hsv))]
        self.current_cross = []
        self.before_delete_value = ''

        #widgets initialization
        self.hue_picker_frame = Frame(self, background='#f0f0f0')
        self.saturation_value_picker = Canvas(self, width=360, height=360, border=0, background='black', highlightthickness=1, highlightbackground='#B4B4B4')
        self.hue_picker = Canvas(self.hue_picker_frame, width=10, height=360, border=0, background='black', highlightthickness=1, highlightbackground='#B4B4B4')
        self.hue_picker_arrow = Canvas(self.hue_picker_frame, width=10, height=376, background='#f0f0f0', highlightthickness=0)
        self.property_frame = Frame(self, background='#f0f0f0')
        self.color_showcase = Canvas(self.property_frame, width=101, height=101, highlightbackground='#B4B4B4', highlightthickness=1)
        self.current_arrow = self.hue_picker_arrow.create_polygon(1, 7, 8, 0, 8, 14, fill='#343434')

        self.r_label = ttk.Label(self.property_frame, text='R:', background='#f0f0f0')
        self.g_label = ttk.Label(self.property_frame, text='G:', background='#f0f0f0')
        self.b_label = ttk.Label(self.property_frame, text='B:', background='#f0f0f0')
        self.h_label = ttk.Label(self.property_frame, text='H:', background='#f0f0f0')
        self.s_label = ttk.Label(self.property_frame, text='S:', background='#f0f0f0')
        self.v_label = ttk.Label(self.property_frame, text='V:', background='#f0f0f0')
        self.hex_label = ttk.Label(self.property_frame, text='# ', background='#f0f0f0')

        rgb_validator = (self.register(self.onRGBValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        hsv_validator = (self.register(self.onHSVValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.r_input = ttk.Spinbox(self.property_frame, width=7, from_=0, to=255, validate="key", validatecommand=rgb_validator, name='rgb0')
        self.g_input = ttk.Spinbox(self.property_frame, width=7, from_=0, to=255, validate="key", validatecommand=rgb_validator, name='rgb1')
        self.b_input = ttk.Spinbox(self.property_frame, width=7, from_=0, to=255, validate="key", validatecommand=rgb_validator, name='rgb2')
        self.h_input = ttk.Spinbox(self.property_frame, width=7, from_=0, to=360, validate="key", validatecommand=hsv_validator, name='hsv0')
        self.s_input = ttk.Spinbox(self.property_frame, width=7, from_=0, to=255, validate="key", validatecommand=hsv_validator, name='hsv1')
        self.v_input = ttk.Spinbox(self.property_frame, width=7, from_=0, to=255, validate="key", validatecommand=hsv_validator, name='hsv2')
        self.hex_input = ttk.Entry(self.property_frame, width=8, font=Font(size=9))

        #draw hue picker
        [self.hue_picker.create_line(0, i, 12, i, width=1, fill=rgb_to_hex(hsv_to_rgb(i/360, 1, 1))) for i in range(361)]

        #widget placing
        self.saturation_value_picker.grid(row=0, column=1)
        self.hue_picker_frame.grid(row=0, column=2, padx=(10, 0))
        self.property_frame.grid(row=0, column=3, pady=(3, 0), padx=(20, 0))
        self.hue_picker.grid(row=0, column=0)
        self.hue_picker_arrow.grid(row=0, column=1)
        self.color_showcase.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        self.r_label.grid(row=1, column=0, pady=(0, 1))
        self.g_label.grid(row=2, column=0, pady=(0, 1))
        self.b_label.grid(row=3, column=0, pady=(0, 6))
        self.h_label.grid(row=4, column=0, pady=(0, 1))
        self.s_label.grid(row=5, column=0, pady=(0, 1))
        self.v_label.grid(row=6, column=0, pady=(0, 6))
        self.hex_label.grid(row=7, column=0, pady=(0, 3))

        self.r_input.grid(row=1, column=1, pady=(0, 1))
        self.g_input.grid(row=2, column=1, pady=(0, 1))
        self.b_input.grid(row=3, column=1, pady=(0, 6))
        self.h_input.grid(row=4, column=1, pady=(0, 1))
        self.s_input.grid(row=5, column=1, pady=(0, 1))
        self.v_input.grid(row=6, column=1, pady=(0, 6))
        self.hex_input.grid(row=7, column=1, ipadx=1)

        #alignment configurations
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(4, weight=1)

        #key binding
        self.hue_picker.bind('<B1-Motion>', self.pick_hue)
        self.hue_picker.bind('<Button-1>', self.pick_hue)
        self.saturation_value_picker.bind('<B1-Motion>', self.pick_saturation_value)
        self.saturation_value_picker.bind('<Button-1>', self.pick_saturation_value)
        
        #post initialization
        self.update_property()
        self.generate_saturation_value()
        self.update_cross()

    def format_rgb_hsv(self):
        self.current_hsv[0].set(self.current_hsv[0].get()/360)
        [self.current_hsv[i].set(self.current_hsv[i].get()/255) for i in range(1, 3)]
        [self.current_rgb[i].set(v) for i, v in enumerate([round(i*255) for i in colorsys.hsv_to_rgb(*[i.get() for i in self.current_hsv])])]

    def onHSVValidate(self, d, i, P, s, S, v, V, W):
        try:
            if self.nametowidget(W).selection_get() == self.nametowidget(W).get():
                if d=='1' and S.isdigit(): 
                    self.nametowidget(W).delete(0, 'end')
                    self.nametowidget(W).insert(0, S)
                    return True
                elif d=='0':
                    self.nametowidget(W).set(0)
                    return False
                else: 
                    self.bell()
                    return False
            if self.nametowidget(W).selection_get():
                if d=='0':
                    self.before_delete_value = self.nametowidget(W).get()
                    return True
        except: pass
        if P=='': return False
        if int(P.replace('.', ''))==0 or (P!='' and S.isdigit() and float(P)):
            if int(W.split('.hsv')[-1]) == 0: 
                if not 0<=float(P)<=360: return False
                self.current_hsv[int(W.split('.hsv')[-1])].set(float(P)/360)
            else:
                if not 0<=float(P)<=100: return False
                self.current_hsv[int(W.split('.hsv')[-1])].set(float(P)/100)
            
            [self.current_rgb[i].set(round(v)) for i, v in enumerate(hsv_to_rgb(self.current_hsv[0].get(), self.current_hsv[1].get(), self.current_hsv[2].get()))]
            
            self.update_property(hsv=False)
            return True
        return False

    def onRGBValidate(self, d, i, P, s, S, v, V, W):
        try:
            if self.nametowidget(W).selection_get() == self.nametowidget(W).get():
                if d=='1' and S.isdigit(): 
                    self.nametowidget(W).delete(0, 'end')
                    self.nametowidget(W).insert(0, S)
                    self.update_rgb(W, P)
                    return True
                elif d=='0':
                    self.nametowidget(W).set(0)
                    self.update_rgb(W, '0')
                    return False
                else: 
                    self.bell()
                    return False
            if self.nametowidget(W).selection_get():
                if d=='0':
                    self.before_delete_value = self.nametowidget(W).get()
                    self.update_rgb(W, P)
                    return True
        except: pass

        if P=='':
            self.nametowidget(W).set(0)
            self.update_rgb(W, '0')
            self.bell() 
            return False

        if S.isdigit():
            if not 0<=int(P)<=255:
                self.bell()
                return False
            if s=='0' or (s.isdigit() and not int(s) and not i):
                self.nametowidget(W).set(S)
                self.update_rgb(W, P)
                return False
            if P.startswith('0'):
                self.nametowidget(W).set(int(self.nametowidget(W).get()))
                self.bell() 
                return False
        else:
            if d=='1':
                self.bell()
                if self.before_delete_value:
                    self.nametowidget(W).delete(0, 'end')
                    self.nametowidget(W).insert(0, self.before_delete_value)
                    self.before_delete_value = ''
                return False
        self.update_rgb(W, P)
        return True

    def update_rgb(self, W, P): 
        self.current_rgb[int(W.split('.rgb')[-1])].set(int(P))
        [self.current_hsv[i].set(v) for i, v in enumerate(rgb_to_hsv(*(i.get() for i in self.current_rgb)))]
        
        self.update_property(rgb=False)

    #update values in property section
    def update_property(self, rgb=True, hsv=True, is_generating_hue=False):
        if rgb:
            self.r_input.set(round(self.current_rgb[0].get()))
            self.g_input.set(round(self.current_rgb[1].get()))
            self.b_input.set(round(self.current_rgb[2].get()))
        if hsv:
            self.h_input.set(round(self.current_hsv[0].get()*360, 1))
            self.s_input.set(round(self.current_hsv[1].get()*100, 1))
            self.v_input.set(round(self.current_hsv[2].get()*100, 1))
            
        if not(rgb==True and hsv==True):
            self.update_hue_picker_arrow(self.current_hsv[0].get())
            self.curr_hue = self.current_hsv[0].get()*360
            self.generate_saturation_value()
            self.current_corr = (self.current_hsv[1].get()*360, 360-self.current_hsv[2].get()*360)
            self.update_cross()

        self.hex_input.delete(0, 'end')
        self.hex_input.insert(0, rgb_to_hex([i.get() for i in self.current_rgb])[1:])
        self.color_showcase.delete('all')
        self.color_showcase.create_rectangle(2, 2, 101, 101, fill=rgb_to_hex([i.get() for i in self.current_rgb]), width=0)
        

    #things to do when user pick a new hue value in the colorful line
    def pick_hue(self, e):
        #prevent mouse coordinates out of range
        if e.y < 0: e.y = 0
        if e.y > 360: e.y = 360

        self.curr_hue = e.y

        self.update_hue_picker_arrow(e.y/360)
        
        self.generate_saturation_value()

        self.current_hsv[0].set(self.curr_hue)
        [self.current_hsv[i].set(self.current_hsv[i].get()*255) for i in range(1, 3)]

        self.format_rgb_hsv()
        self.update_property(is_generating_hue=True)
        self.update_cross()

    #things to do when user click on a new place on the big saturationn and value palette
    def pick_saturation_value(self, e):
        #prevent mouse coordinates out of range
        if e.x<0: e.x = 0
        if e.y<0: e.y = 0
        if e.x>360: e.x = 360
        if e.y>360: e.y = 360

        self.current_corr = [e.x, e.y]
        sv = [e.x, (360-e.y)]
        [self.current_hsv[i].set(v) for i, v in enumerate((self.curr_hue, *[i/360*255 for i in sv]))]
        self.format_rgb_hsv()
        self.update_property()
        self.update_cross()

    #makes the crosshair to follow user's mouse pointer on saturationn and value palette
    def update_cross(self):
        [self.saturation_value_picker.delete(i) for i in self.current_cross]
        self.current_cross = [
            self.saturation_value_picker.create_line(self.current_corr[0]+3, self.current_corr[1], self.current_corr[0]+8, self.current_corr[1], width=2, fill='black'),
            self.saturation_value_picker.create_line(self.current_corr[0]-3, self.current_corr[1], self.current_corr[0]-8, self.current_corr[1], width=2, fill='black'), 
            self.saturation_value_picker.create_line(self.current_corr[0], self.current_corr[1]+3, self.current_corr[0], self.current_corr[1]+8, width=2, fill='black'),
            self.saturation_value_picker.create_line(self.current_corr[0], self.current_corr[1]-3, self.current_corr[0], self.current_corr[1]-8, width=2, fill='black')
        ]

    def update_hue_picker_arrow(self, y):
        y = y * 360
        self.hue_picker_arrow.delete(self.current_arrow)
        self.current_arrow = self.hue_picker_arrow.create_polygon(1, y+7, 8, y, 8, y+14, fill='#343434')

    #generate a new saturationn and value palette when user pick a new hue
    def generate_saturation_value(self):
        self.saturation_value_picker.delete('all')
        im= Image.new("RGB", (256, 256), "#000000")
        pixels = im.load()

        v = 0
        h = self.curr_hue
        s = 0

        h_x = 0
        v_y = 0
        for v in range(255, -1, -1):
            for s in range(256):
                pixels[h_x, v_y] = tuple(int(i) for i in hsv_to_rgb(h/360, s/255, v/255))
                h_x += 1
            h_x = 0
            v_y += 1

        self.im = im.resize((360, 360))
        self.pixels = self.im.convert('HSV').load()
        self.img = ImageTk.PhotoImage(self.im)
        self.saturation_value_picker.create_image(1, 1, image=self.img, anchor=NW)
        self.update_cross()

if __name__ == '__main__':
    root = ColorPalette()
    root.mainloop()