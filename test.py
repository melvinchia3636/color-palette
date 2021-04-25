from PIL import Image

im= Image.new("RGB", (256, 256), "#000000")
pixels = im.load()

r, g, b = 0, 255, 0

h_x = 0
v_y = 0
for r in range(255, -1, -1):
	for b in range(256):
		pixels[h_x, v_y] = (r, g, b)
		h_x += 1
	h_x = 0
	v_y += 1

im = im.resize((360, 360))
im.save('g.png')

im= Image.new("RGB", (256, 256), "#000000")
pixels = im.load()

r, g, b = 255, 0, 0

h_x = 0
v_y = 0
for g in range(255, -1, -1):
	for b in range(256):
		pixels[h_x, v_y] = (r, g, b)
		h_x += 1
	h_x = 0
	v_y += 1

im = im.resize((360, 360))
im.save('r.png')

im= Image.new("RGB", (256, 256), "#000000")
pixels = im.load()

r, g, b = 0, 0, 255

h_x = 0
v_y = 0
for r in range(255, -1, -1):
	for g in range(256):
		pixels[h_x, v_y] = (r, g, b)
		h_x += 1
	h_x = 0
	v_y += 1

im = im.resize((360, 360))
im.save('b.png')