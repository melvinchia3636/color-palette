from tkinter import *
import tkinter.ttk as ttk
from tkinter.font import Font
from ttkthemes import ThemedTk
from PIL import Image, ImageTk, ImageColor, ImageDraw
import colorsys
import math
from itertools import count
from functools import partial

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

def rgb_to_cmyk(r, g, b):
    if (r, g, b) == (0, 0, 0):
        return 0, 0, 0, 100

    c = 1 - r / 255
    m = 1 - g / 255
    y = 1 - b / 255

    min_cmy = min(c, m, y)
    c = (c - min_cmy) / (1 - min_cmy)
    m = (m - min_cmy) / (1 - min_cmy)
    y = (y - min_cmy) / (1 - min_cmy)
    k = min_cmy

    return c * 100, m * 100, y * 100, k * 100

def cmyk_to_rgb(c, m, y, k, cmyk_scale=100, rgb_scale=255):
    r = rgb_scale * (1.0 - c / float(cmyk_scale)) * (1.0 - k / float(cmyk_scale))
    g = rgb_scale * (1.0 - m / float(cmyk_scale)) * (1.0 - k / float(cmyk_scale))
    b = rgb_scale * (1.0 - y / float(cmyk_scale)) * (1.0 - k / float(cmyk_scale))
    return r, g, b

def isDark(color):
	r, g, b = ImageColor.getrgb(color)
	
	hsp = math.sqrt(
		0.299 * (r * r) +
		0.587 * (g * g) +
		0.114 * (b * b)
	)

	return not hsp > 90

class ColorPicker(ThemedTk):
    def __init__(self):
        #parent initialize
        super(ColorPicker, self).__init__(theme='breeze', background='#f0f0f0')

        #window configurations
        self.geometry('880x480')
        self.title('Color Picker')
        self.resizable(False, False)

        #non-widget variables initialization
        self.curr_hue = 0
        self.current_corr = [360, 0]
        self.current_hsv = [DoubleVar(value=i) for i in (0, 1, 1)]
        self.current_rgb = [IntVar(value=i) for i in hsv_to_rgb(*(i.get() for i in self.current_hsv))]
        self.current_cmyk = [IntVar(value=i) for i in rgb_to_cmyk(*(i.get() for i in self.current_rgb))]
        self.current_cross = []
        self.before_delete_value = ''
        self.current_hex = StringVar()

        validator = {
            'rgb': (self.register(lambda *args, max_val=255: self.onRGBCMYKValidate(*args, max_val=max_val)), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'),
            'cmyk': (self.register(lambda *args, max_val=100: self.onRGBCMYKValidate(*args, max_val=max_val)), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'),
            'hsv': (self.register(self.onHSVValidate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'),
            'hex': (self.register(self.onHexValidate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        }

        label_content = ['Red', 'Green', 'Blue', 'Hue', 'Saturation', 'Value', 'Cyan', 'Magenta', 'Yellow', 'BlacK']
        input_maxval_increment = [(255, 1), (255, 1), (255, 1), (360, 0.1), (255, 0.1), (255, 0.1), (100, 1), (100, 1), (100, 1), (100, 1)]

        #widgets initialization
        self.saturation_value_picker = Canvas(self, width=360, height=360, border=0, background='black', highlightthickness=1, highlightbackground='#B4B4B4')
        self.property_frame = Frame(self, background='#f0f0f0', name='property')
        self.color_showcase = Canvas(self.property_frame, width=101, height=101, highlightbackground='#B4B4B4', highlightthickness=1)

        self.widgets = {
            **{f'{i}_preview': Canvas(self.property_frame, highlightthickness=1, highlightbackground='#B4B4B4', width=15, height=15, name=f'preview_{i}') for i in 'rgbhsvcmyk'},
            **{f'{i}_label': ttk.Label(self.property_frame, text=label_content[c], background='#f0f0f0', justify=LEFT, anchor=W, name=f'label_{i}') for c, i in enumerate('rgbhsvcmyk')},
            **{f'{v[c]}_input': ((n:=next(t)), ttk.Spinbox(
                self.property_frame, 
                width=7, 
                from_=0, 
                to=input_maxval_increment[n][0], 
                increment=input_maxval_increment[n][1], 
                validate="key", 
                validatecommand=validator[v], 
                name=f'{v}{c}', 
                command=partial(self.increment_callback, v, c)
            ))[1] for _, v in enumerate(('rgb', 'hsv', 'cmyk')) for c in range(len(v))},
            **{f'{i}_slider': Canvas(self.property_frame, height=28, width=265, highlightthickness=1, highlightbackground='#B4B4B4', cursor="tcross", name=f'slider_{i}') for i in 'rgbhsvcmyk'},
        } if (t:=count()) else 0

        self.__dict__.update(self.widgets)

        #self.hex_label = ttk.Label(self.property_frame, text='HTML', background='#f0f0f0', justify=LEFT, anchor=W)
        #self.hex_input = ttk.Entry(self.property_frame, width=8, font=Font(size=9), validate="key", validatecommand=hex_validator, textvariable=self.current_hex)

        #widget placing
        self.saturation_value_picker.grid(row=0, column=1)
        self.property_frame.grid(row=0, column=3, pady=(3, 0), padx=(20, 0))
        #self.color_showcase.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        [self.nametowidget(f'.property.preview_{v}').grid(row=i+1, column=0, pady=(0, 1), padx=(0, 5)) for i, v in enumerate('rgbhsvcmyk')]
        [self.nametowidget(f'.property.label_{v}').grid(row=i+1, column=1, pady=(0, 1), padx=(0, 5), sticky='W') for i, v in enumerate('rgbhsvcmyk')]
        [self.nametowidget(f'.property.{v}{c}').grid(row=next(t)+1, column=2, pady=(0, 1), padx=(0, 5)) for _, v in enumerate(('rgb', 'hsv', 'cmyk')) for c in range(len(v))] if (t:=count()) else 0
        [self.nametowidget(f'.property.slider_{v}').grid(row=i+1, column=3, pady=(0, 1), padx=(5, 0)) for i, v in enumerate('rgbhsvcmyk')]

        #self.hex_label.grid(row=7, column=1, pady=(0, 1), padx=(0, 10), sticky = W)
        #self.hex_input.grid(row=7, column=2, ipadx=1)

        #alignment configurations
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(4, weight=1)

        #key binding
        self.saturation_value_picker.bind('<B1-Motion>', self.pick_saturation_value)
        self.saturation_value_picker.bind('<Button-1>', self.pick_saturation_value)
  
        [self.nametowidget(f'.property.slider_{v}').bind(j, partial(self.pick_rgb, v, f'rgb{i}')) for j in ['<B1-Motion>', '<Button-1>'] for i, v in enumerate('rgb')]
        [self.nametowidget(f'.property.slider_{v}').bind(j, partial(self.pick_hsv, v, f'hsv{i}')) for j in ['<B1-Motion>', '<Button-1>'] for i, v in enumerate('hsv')]
        [self.nametowidget(f'.property.slider_{v}').bind(j, partial(self.pick_cmyk, v, f'cmyk{i}')) for j in ['<B1-Motion>', '<Button-1>'] for i, v in enumerate('cmyk')]
        
        #post initialization

        self.generate_slider()
        self.sliders = {
            **{
                v: [
                    self.nametowidget(f'.property.slider_{v}').create_rectangle(self.current_rgb[i].get()+2, 1, self.current_rgb[i].get()+10, 28, outline='black', width=1),
                    self.nametowidget(f'.property.slider_{v}').create_rectangle(self.current_rgb[i].get()+3, 2, self.current_rgb[i].get()+9, 27, outline='white', width=1)
                ] for i, v in enumerate('rgb')
            }, 
            **{
                v: [
                    self.nametowidget(f'.property.slider_{v}').create_rectangle(self.current_hsv[i].get()*255+1, 1, self.current_hsv[i].get()*255+10, 28, outline='black', width=1),
                    self.nametowidget(f'.property.slider_{v}').create_rectangle(self.current_hsv[i].get()*255+2, 2, self.current_hsv[i].get()*255+9, 27, outline='white', width=1)
                ] for i, v in enumerate('hsv')
            }, 
            **{
                v: [
                    self.nametowidget(f'.property.slider_{v}').create_rectangle(self.current_cmyk[i].get()/100*255+1, 1, self.current_cmyk[i].get()/100*255+10, 28, outline='black', width=1),
                    self.nametowidget(f'.property.slider_{v}').create_rectangle(self.current_cmyk[i].get()/100*255+2, 2, self.current_cmyk[i].get()/100*255+9, 27, outline='white', width=1)
                ] for i, v in enumerate('cmyk')
            }, 
        }

        self.update_property()
        self.generate_saturation_value()
        self.update_cross()

    def increment_callback(self, cat, i):
        if cat=='rgb':
            self.current_rgb[i].set(self.nametowidget(f'.property.rgb{i}').get())
            [self.current_hsv[i].set(v) for i, v in enumerate(rgb_to_hsv(*(i.get() for i in self.current_rgb)))]
            [self.current_cmyk[i].set(v) for i, v in enumerate(rgb_to_cmyk(*(i.get() for i in self.current_rgb)))]
        if cat=='hsv':
            self.current_hsv[i].set(float(self.nametowidget(f'.property.hsv{i}').get())/(360 if not i else 100))
            [self.current_rgb[i].set(round(v)) for i, v in enumerate(hsv_to_rgb(*(i.get() for i in self.current_hsv)))]
            [self.current_cmyk[i].set(v) for i, v in enumerate(rgb_to_cmyk(*(i.get() for i in self.current_rgb)))]
        if cat=='cmyk':
            self.current_cmyk[i].set(float(self.nametowidget(f'.property.cmyk{i}').get()))
            [self.current_rgb[i].set(v) for i, v, in enumerate(cmyk_to_rgb(*(i.get() for i in self.current_cmyk)))]
            [self.current_hsv[i].set(v) for i, v in enumerate(rgb_to_hsv(*(i.get() for i in self.current_rgb)))]
        self.update_property()
        
    def generate_slider(self):
        rgb_canvas = Image.new("RGB", (266, 28), "#000000")
        cmyk_sv_canvas = Image.new("RGB", (111, 28), "#FFFFFF")
        h_canvas = Image.new("RGB", (371, 28), "#000000")

        rgb_draw = ImageDraw.Draw(rgb_canvas)
        cmyk_sv_draw = ImageDraw.Draw(cmyk_sv_canvas)
        h_draw = ImageDraw.Draw(h_canvas)
        
        rgb_img = {f'{v}_img': [rgb_draw.line((s, 0, s, 28), fill=tuple(0 if i!=c else s-5 for i in range(3))) for s in range(266)] and ImageTk.PhotoImage(rgb_canvas.resize((265, 28))) for c, v in enumerate('rgb')}
        cmyk_img = {f'{v}_img': [cmyk_sv_draw.line((s, 0, s, 28), fill=tuple(map(int, cmyk_to_rgb(*(0 if i!=c else s-5 for i in range(4)))))) for s in range(5, 111)] and ImageTk.PhotoImage(cmyk_sv_canvas.resize((265, 28))) for c, v in enumerate('cmyk')}
        sv_img = {f'{v}_img': [cmyk_sv_draw.line((s, 0, s, 28), fill=tuple(map(int, hsv_to_rgb(self.current_hsv[0].get(), 1 if c else (s-5)/100, (s-5)/100 if c else 1)))) for s in range(111)] and ImageTk.PhotoImage(cmyk_sv_canvas.resize((265, 28))) for c, v in enumerate('sv')}
        for s in range(371): h_draw.line((s, 0, s, 28), fill=tuple(map(int, hsv_to_rgb((s-5)/360, 1, 1))))

        self.__dict__.update(cmyk_img)
        self.__dict__.update(rgb_img)
        self.__dict__.update(sv_img)
        self.h_img = ImageTk.PhotoImage(h_canvas.resize((265, 28)))

        [self.nametowidget(f'.property.slider_{i}').create_image(1, 1, image=eval(f'self.{i}_img'), anchor=NW) for i in 'rgbhsvcmyk']

    def update_slider(self):
        [self.nametowidget(f'.property.slider_{v}').delete('all') for v in 'sv']
        sv_canvas = Image.new("RGB", (111, 28), "#FFFFFF")
        sv_draw = ImageDraw.Draw(sv_canvas)
        sv_img = {f'{v}_img': [sv_draw.line((s, 0, s, 28), fill=tuple(map(int, hsv_to_rgb(self.current_hsv[0].get(), 1 if c else (s-5)/100, (s-5)/100 if c else 1)))) for s in range(111)] and ImageTk.PhotoImage(sv_canvas.resize((265, 28))) for c, v in enumerate('sv')}
        self.__dict__.update(sv_img)
        [self.nametowidget(f'.property.slider_{i}').create_image(1, 1, image=eval(f'self.{i}_img'), anchor=NW) for i in 'sv']

        for i, v in enumerate('rgb'):
            [self.nametowidget(f'.property.slider_{v}').delete(i) for i in self.sliders[v]]
            self.sliders[v] = [
                self.nametowidget(f'.property.slider_{v}').create_rectangle(self.current_rgb[i].get()+1, 1, self.current_rgb[i].get()+10, 28, outline='black', width=1),
                self.nametowidget(f'.property.slider_{v}').create_rectangle(self.current_rgb[i].get()+2, 2, self.current_rgb[i].get()+9, 27, outline='white', width=1)
            ]
        for i, v in enumerate('hsv'):
            [self.nametowidget(f'.property.slider_{v}').delete(i) for i in self.sliders[v]]
            self.sliders[v] = [
                self.nametowidget(f'.property.slider_{v}').create_rectangle(self.current_hsv[i].get()*255+1, 1, self.current_hsv[i].get()*255+10, 28, outline='black', width=1),
                self.nametowidget(f'.property.slider_{v}').create_rectangle(self.current_hsv[i].get()*255+2, 2, self.current_hsv[i].get()*255+9, 27, outline='white', width=1)
            ]
        for i, v in enumerate('cmyk'):
            [self.nametowidget(f'.property.slider_{v}').delete(i) for i in self.sliders[v]]
            self.sliders[v] = [
                self.nametowidget(f'.property.slider_{v}').create_rectangle(self.current_cmyk[i].get()/100*255+1, 1, self.current_cmyk[i].get()/100*255+10, 28, outline='black', width=1),
                self.nametowidget(f'.property.slider_{v}').create_rectangle(self.current_cmyk[i].get()/100*255+2, 2, self.current_cmyk[i].get()/100*255+9, 27, outline='white', width=1)
            ]

    def pick_rgb(self, t, n, e):
        if e.x < 5: e.x = 5
        if e.x > 260: e.x = 260

        slider = self.nametowidget(f'.property.slider_{t}')
        [slider.delete(i) for i in self.sliders[t]]
        self.sliders[t] = [
            slider.create_rectangle(e.x-5, 1, e.x+5, 28, outline='black', width=1),
            slider.create_rectangle(e.x-4, 2, e.x+4, 27, outline='white', width=1)
        ]
        self.nametowidget(f'.property.{n}').set(e.x-5)
        self.update_rgb(f'.property.{n}', e.x-5)
        self.update_slider()

    #things to do when user pick a new hue value in the colorful line
    def pick_hsv(self, t, n, e):
        #prevent mouse coordinates out of range
        if e.x < 5: e.x = 5
        if e.x > 260: e.x = 260

        if t=='h':
            self.curr_hue = (e.x-5)/255*360
            self.generate_saturation_value()

        slider = self.nametowidget(f'.property.slider_{t}')
        [slider.delete(i) for i in self.sliders[t]]
        self.sliders[t] = [
            slider.create_rectangle(e.x-5, 1, e.x+5, 28, outline='black', width=1),
            slider.create_rectangle(e.x-4, 2, e.x+4, 27, outline='white', width=1)
        ]
        #self.nametowidget(f'.property.{n}').set((e.x-5)/255*360 if t=='h' else (e.x-5)/255*100)
        self.update_hsv(f'.property.{n}', (e.x-5)/255*360 if t=='h' else (e.x-5)/255*100)
        self.update_slider()

    def pick_cmyk(self, t, n, e):
        if e.x < 5: e.x = 5
        if e.x > 260: e.x = 260

        slider = self.nametowidget(f'.property.slider_{t}')
        [slider.delete(i) for i in self.sliders[t]]
        self.sliders[t] = [
            slider.create_rectangle(e.x-5, 1, e.x+5, 28, outline='black', width=1),
            slider.create_rectangle(e.x-4, 2, e.x+4, 27, outline='white', width=1)
        ]
        self.nametowidget(f'.property.{n}').set(e.x-5)
        self.update_cmyk(f'.property.{n}', (e.x-5)/255*100)
        self.update_slider()

    def onHexValidate(self, d, i, P, s, S, v, V, W):
        if all(i in '0123456789ABCDEFabcdef' for i in S) and len(P) <= 6:
            if len(P) == 6:
                self.update_hex(P)
            return True
        return False

    def onHSVValidate(self, d, i, P, s, S, v, V, W):
        def insert_before_val(self, W):
            self.nametowidget(W).delete(0, 'end')
            self.nametowidget(W).insert(0, self.before_delete_value)
            self.update_hsv(W, self.before_delete_value)
            self.before_delete_value = ''
        try:
            if self.nametowidget(W).selection_get() == self.nametowidget(W).get():
                if d=='1' and S.isdigit(): 
                    self.nametowidget(W).delete(0, 'end')
                    self.nametowidget(W).insert(0, float(S))
                    self.update_hsv(W, float(S))
                    return True
                elif not(int(d)):
                    self.nametowidget(W).set(0.0)
                    self.update_hsv(W, '0')
                    return False
                else: 
                    return False
            if self.nametowidget(W).selection_get():
                if not int(d):
                    if S=='.': return False
                    self.before_delete_value = self.nametowidget(W).get()
                    self.update_rgb(W, P)
        except: pass

        if P=='':
            self.nametowidget(W).set(0)
            self.update_hsv(W, '0')
            return False

        if S.isdigit():
            if not int(W.split('.hsv')[-1]) and not 0<=float(P)<=360:
                return False
            if int(W.split('.hsv')[-1]) and not 0<=float(P)<=100:
                if self.before_delete_value:
                    self.nametowidget(W).delete(0, 'end')
                    self.nametowidget(W).insert(0, self.before_delete_value)
                    self.update_hsv(W, self.before_delete_value)
                    self.before_delete_value = ''
                return False
            if (len(P.split('.'))!=2 and not i):
                return False
            if not(float(s)) and not i:
                self.nametowidget(W).set(float(S))
                self.update_hsv(W, P)
                return False
        else:
            if int(d):
                if self.before_delete_value:
                    insert_before_val(self, W)
                return False
        self.nametowidget(W).set(float(P))
        self.nametowidget(W).icursor(int(i)+1)
        self.update_hsv(W, P)
        return True

    def onRGBCMYKValidate(self, d, i, P, s, S, v, V, W, max_val=255):
        try:
            if self.nametowidget(W).selection_get() == self.nametowidget(W).get():
                if d=='1' and S.isdigit(): 
                    self.nametowidget(W).delete(0, 'end')
                    self.nametowidget(W).insert(0, S)
                    self.update_rgb(W, S) if max_val==255 else self.update_cmyk(W, S)
                    return True
                elif not(int(d)):
                    self.nametowidget(W).set(0)
                    self.update_rgb(W, '0') if max_val==255 else self.update_cmyk(W, '0')
                    return False
                else: 
                    return False
            if self.nametowidget(W).selection_get():
                if not(int(d)):
                    self.before_delete_value = self.nametowidget(W).get()
                    self.update_rgb(W, P) if max_val==255 else self.update_cmyk(W, P)
                    self.nametowidget(W).set(int(P))
                    return True
        except: pass

        if P=='':
            self.nametowidget(W).set(0)
            self.update_rgb(W, '0') if max_val==255 else self.update_cmyk(W, '0')
            return False

        if S.isdigit():
            if not 0<=int(P)<=max_val:
                return False
            if not int(s) and not int(i):
                self.update_rgb(W, P) if max_val==255 else self.update_cmyk(W, P)
                return True
            if (not(int(s)) and not int(i)) or (not int(s) and int(i)):
                self.nametowidget(W).set(S)
                self.update_rgb(W, P) if max_val==255 else self.update_cmyk(W, P)
                return False
        else:
            if int(d):
                if self.before_delete_value:
                    self.nametowidget(W).delete(0, 'end')
                    self.nametowidget(W).insert(0, self.before_delete_value)
                    self.before_delete_value = ''
                return False
        self.nametowidget(W).set(int(P))
        self.update_rgb(W, P) if max_val==255 else self.update_cmyk(W, P)
        return True

    def update_rgb(self, W, P): 
        self.current_rgb[int(W.split('.rgb')[-1])].set(int(P))
        [self.current_hsv[i].set(v) for i, v in enumerate(rgb_to_hsv(*(i.get() for i in self.current_rgb)))]
        [self.current_cmyk[i].set(v) for i, v in enumerate(rgb_to_cmyk(*(i.get() for i in self.current_rgb)))]
        self.update_property()

    def update_cmyk(self, W, P): 
        self.current_cmyk[int(W.split('.cmyk')[-1])].set(int(P))
        [self.current_rgb[i].set(v) for i, v, in enumerate(cmyk_to_rgb(*(i.get() for i in self.current_cmyk)))]
        [self.current_hsv[i].set(v) for i, v in enumerate(rgb_to_hsv(*(i.get() for i in self.current_rgb)))]
        self.update_property()

    def update_hex(self, P):
        self.current_hex.set(P)
        rgb = ImageColor.getrgb('#'+P)
        [self.current_rgb[i].set(v) for i, v in enumerate(rgb)]
        [self.current_hsv[i].set(v) for i, v in enumerate(rgb_to_hsv(*(i.get() for i in self.current_rgb)))]
        [self.current_cmyk[i].set(v) for i, v in enumerate(rgb_to_cmyk(*(i.get() for i in self.current_rgb)))]
        self.update_property()

    def update_hsv(self, W, P):
        if not int(W.split('.hsv')[-1]): 
            if not 0<=float(P)<=360: return False
            self.current_hsv[int(W.split('.hsv')[-1])].set(float(P)/360)
        else:
            if not 0<=float(P)<=100: return False
            self.current_hsv[int(W.split('.hsv')[-1])].set(float(P)/100)
        
        [self.current_rgb[i].set(round(v)) for i, v in enumerate(hsv_to_rgb(*(i.get() for i in self.current_hsv)))]
        [self.current_cmyk[i].set(v) for i, v in enumerate(rgb_to_cmyk(*(i.get() for i in self.current_rgb)))]
        
        self.update_property()

    #update values in property section
    def update_property(self, color_field=False):
        [self.nametowidget(f'.property.rgb{i}').set(round(self.current_rgb[i].get())) for i in range(3)]
        [self.nametowidget(f'.property.hsv{i}').set(round(self.current_hsv[i].get()*(100 if i else 360), 1)) for i in range(3)]
        [self.nametowidget(f'.property.cmyk{i}').set(round(self.current_cmyk[i].get(), 1)) for i in range(4)]
        self.current_hex.set(rgb_to_hex([i.get() for i in self.current_rgb])[1:])
        self.update_slider()
            
        if not color_field:
            self.curr_hue = self.current_hsv[0].get()*360
            self.current_corr = (self.current_hsv[1].get()*360, 360-self.current_hsv[2].get()*360)

            self.generate_saturation_value()
            self.update_cross()

        [self.nametowidget(f'.property.preview_{i}').delete('all') for i in 'rgbhsvcmyk']

        self.r_preview.create_rectangle(0, 0, 16, 16, fill=rgb_to_hex((self.current_rgb[0].get(), 0, 0)),  width=0)
        self.g_preview.create_rectangle(0, 0, 16, 16, fill=rgb_to_hex((0, self.current_rgb[1].get(), 0)),  width=0)
        self.b_preview.create_rectangle(0, 0, 16, 16, fill=rgb_to_hex((0, 0, self.current_rgb[2].get())),  width=0)
        self.h_preview.create_rectangle(0, 0, 16, 16, fill=rgb_to_hex(hsv_to_rgb(self.current_hsv[0].get(), 1, 1)),  width=0)
        self.s_preview.create_rectangle(0, 0, 16, 16, fill=rgb_to_hex(hsv_to_rgb(self.current_hsv[0].get(), self.current_hsv[1].get(), 1)),  width=0)
        self.v_preview.create_rectangle(0, 0, 16, 16, fill=rgb_to_hex(hsv_to_rgb(self.current_hsv[0].get(), 1, self.current_hsv[2].get())),  width=0)
        self.c_preview.create_rectangle(0, 0, 16, 16, fill=rgb_to_hex(cmyk_to_rgb(self.current_cmyk[0].get(), 0, 0, 0 )),  width=0)
        self.m_preview.create_rectangle(0, 0, 16, 16, fill=rgb_to_hex(cmyk_to_rgb(0, self.current_cmyk[1].get(), 0, 0)),  width=0)
        self.y_preview.create_rectangle(0, 0, 16, 16, fill=rgb_to_hex(cmyk_to_rgb(0, 0, self.current_cmyk[2].get(), 0)),  width=0)
        self.k_preview.create_rectangle(0, 0, 16, 16, fill=rgb_to_hex(cmyk_to_rgb(0, 0, 0, self.current_cmyk[3].get())),  width=0)

        self.color_showcase.delete('all')
        self.color_showcase.create_rectangle(2, 2, 101, 101, fill=rgb_to_hex([i.get() for i in self.current_rgb]), width=0)

    #things to do when user click on a new place on the big saturationn and value palette
    def pick_saturation_value(self, e):
        #prevent mouse coordinates out of range
        if e.x<0: e.x = 0
        if e.y<0: e.y = 0
        if e.x>360: e.x = 360
        if e.y>360: e.y = 360

        self.current_corr = [e.x, e.y]
        sv = [e.x, (360-e.y)]
        [self.current_hsv[i].set(v) for i, v in enumerate((self.curr_hue/360, *[i/360 for i in sv]))]
        [self.current_rgb[i].set(v) for i, v in enumerate([round(i*255) for i in colorsys.hsv_to_rgb(*[i.get() for i in self.current_hsv])])]
        [self.current_cmyk[i].set(v) for i, v in enumerate(rgb_to_cmyk(*(i.get() for i in self.current_rgb)))]
        self.update_property(color_field=True)
        self.update_cross()

    #makes the crosshair to follow user's mouse pointer on saturationn and value palette
    def update_cross(self):
        [self.saturation_value_picker.delete(i) for i in self.current_cross]
        color = 'white' if isDark('#'+self.current_hex.get()) else 'black'
        self.current_cross = [
            self.saturation_value_picker.create_line(self.current_corr[0]+3, self.current_corr[1], self.current_corr[0]+8, self.current_corr[1], width=2, fill=color),
            self.saturation_value_picker.create_line(self.current_corr[0]-3, self.current_corr[1], self.current_corr[0]-8, self.current_corr[1], width=2, fill=color), 
            self.saturation_value_picker.create_line(self.current_corr[0], self.current_corr[1]+3, self.current_corr[0], self.current_corr[1]+8, width=2, fill=color),
            self.saturation_value_picker.create_line(self.current_corr[0], self.current_corr[1]-3, self.current_corr[0], self.current_corr[1]-8, width=2, fill=color)
        ]

    #generate a new saturationn and value palette when user pick a new hue
    def generate_saturation_value(self):
        self.saturation_value_picker.delete('all')
        im= Image.new("HSV", (256, 256), "#000000")
        self.pixels = im.load()

        v = 0
        h = self.curr_hue
        s = 0

        h_x = 0
        v_y = 0
        for v in range(255, -1, -1):
            for s in range(256):
                self.pixels[h_x, v_y] = tuple(int(i) for i in (h/360*255, s, v))
                h_x += 1
            h_x = 0
            v_y += 1

        self.im = im.resize((360, 360))
        self.img = ImageTk.PhotoImage(self.im)
        self.saturation_value_picker.create_image(1, 1, image=self.img, anchor=NW)
        self.update_cross()

if __name__ == '__main__':
    root = ColorPicker()
    root.mainloop()
