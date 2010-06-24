#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import array, cairo, pango, pangocairo, json, re
import xml
from xml.dom import minidom

class Assembler:
	name = '' # automatically set in factory initialization
	
	def is_editable(self):
		return False
	
	def assemble(self, slide, **kwargs):
		raise NotImplementedError
	
	def rasterize(self, slide, src, size):
		raise NotImplementedError
	
	def default_size(self, slide, src, width=None):
		raise NotImplementedError
	
	def raster_is_valid(**kwargs):
		return True

class ImageAssembler(Assembler):
	def is_editable(self):
		return False
	
	def assemble(self, slide, filename):
		dst = open(slide.src_path(filename.filename), 'wb')
		
		while True:
			chunk = filename.file.read(8192)
			if not chunk:
				break
			dst.write(chunk)
		
		return {'filename': filename.filename}
	
	def rasterize(self, slide, filename, size):
		src = filename
		retcode = subprocess.call([
			"convert", slide.src_path(src),
			'-resize', '%dx%d' % size,
			'-background', 'black',
			'-gravity', 'center',
			'-extent', '%dx%d' % size,
			slide.raster_path(size)
		])
		if retcode != 0:
			raise ValueError, 'failed to resample %s' % (self.raster_path(size))
	
	def default_size(self, slide, src, width=None):
		if width:
			raise NotImplementedError
		else:
			return (1024, 768)

def decode_color(str):
	if str[0] == '#':
		str = str[1:]
	
	n = len(str)
	fmt = {
		3: '([0-9A-Fa-f]{1})' * 3, # shorthand RGB
		4: '([0-9A-Fa-f]{1})' * 4, # shorthand RGBA
		6: '([0-9A-Fa-f]{2})' * 3, # RGB
		8: '([0-9A-Fa-f]{2})' * 3 # RGBA
	}
	
	match = re.match(fmt[n], str)
	
	if match:
		color = match.groups()
		if len(color) == 3:
			color += ('ff',) # force RGBA
		
		color = tuple([int(x,16)/255.0 for x in color])
		
		return color
	else:
		return None

def decode_position(str, size):
	"""
	Decode a position string to a tuple with the element sizes
	Accepts either absolute positions or as a percentage of the full size.
	Negative positions are subtracted from the size.
	
	'-50 50%' -> (750, 300) (given that size is (800,600))
	"""
	
	if str == '':
		return None
	
	# parse an element
	# x is element
	# s is the total dimension
	def f(x,s):
		if x[-1] == '%':
			v = float(x[:-1]) / 100.0 * s
		else:
			v = float(x)
		
		if v < 0.0:
			v = s + v
		
		return v
	
	# split into pieces 'x y' -> [x, y]
	p = str.split(' ')
	
	# parse each element
	p = [f(x,s) for x,s in zip(p, size)]
	
	# create tuple
	return tuple(p)
	
class Template:
	def __init__(self, filename):
		self._filename = filename
	
	def rasterize(self, dst, size, params):
		doc = minidom.parse(self._filename)
		template = doc.getElementsByTagName('template')[0]
		
		resolution = list(params['resolution'])
		aspect = float(resolution[0]) / resolution[1]
		
		# fit resolution in size by scaling
		w = int(size[1] * aspect)
		h = size[1]
		realsize = (w,h)
		
		# scale constant
		scale = float(w) / resolution[0]
		
		data = array.array('c', chr(0) * w * h * 4)
		surface = cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, w, h, w*4)
		cr = cairo.Context(surface)
		
		cr.save()
		cr.set_source_rgba(0,0,0,1)
		cr.set_operator(cairo.OPERATOR_SOURCE)
		cr.paint()
		cr.restore()
		
		for item in template.childNodes:
			if not isinstance(item, minidom.Element):
				continue
			
			cr.save()
			try:
				if item.tagName == 'text':
					self._text(size, realsize, scale, cr, item, params[item.getAttribute('name')])
				elif item.tagName == 'textarea':
					self._textarea(size, realsize, scale, cr, item, params[item.getAttribute('name')])
			finally:
				cr.restore()
			
		surface.write_to_png(dst)
	
	@staticmethod
	def _text(size, realsize, scale, cr, item, text):
		font = item.getAttribute('font') or 'Sans'
		fontsize = float(item.getAttribute('size') or '36.0')
		r,g,b,a = decode_color(item.getAttribute('color')) or (0,0,0,1)
		x,y = decode_position(item.getAttribute('position'), realsize) or (0,0)
		alignment = item.getAttribute('align')
		
		fontsize *= scale
		
		cr.select_font_face (font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
		cr.set_font_size(fontsize)
		cr.set_source_rgba(r,g,b,a)
		
		extents = cr.text_extents(text)
		
		offset = 0
		if alignment == "center":
			x -= extents[4] / 2
		elif alignment == "right":
			x -= extents[4]
		
		cr.move_to(x, y)
		cr.show_text(text)
	
	@staticmethod
	def _textarea(size, realsize, scale, cr, item, text):
		#realsize = (size[0] * scale, size[1] * scale)
		font = item.getAttribute('font') or 'Sans'
		fontsize = float(item.getAttribute('size') or '36.0')
		r,g,b,a = decode_color(item.getAttribute('color')) or (0,0,0,1)
		x,y = decode_position(item.getAttribute('position'), realsize) or (0,0)
		w,h = decode_position(item.getAttribute('boxsize'), realsize) or size
		alignment = item.getAttribute('align')
		
		fontsize *= scale
		
		cr.set_source_rgba(r,g,b,a)
		cr.move_to(x-w/2.0, y-h/2.0)
		
		ctx = pangocairo.CairoContext(cr)
		layout = ctx.create_layout()
		layout.set_font_description(pango.FontDescription('%s %f' % (font, fontsize)))
		layout.set_width(int(w * pango.SCALE))
		
		if alignment == 'center':
			layout.set_alignment(pango.ALIGN_CENTER)
		elif alignment == 'right':
			layout.set_alignment(pango.ALIGN_RIGHT)
		elif alignment == 'justify':
			layout.set_justify(True)
		
		layout.set_text(text);
		ctx.show_layout(layout)

class TextAssembler(Assembler):
	def is_editable(self):
		return True
	
	def assemble(self, slide, **kwargs):
		return kwargs
	
	def rasterize(self, size, slide=None, file=None, **kwargs):
		dst = slide and slide.raster_path(size) or file
		template = Template('nitroxy.xml')
		template.rasterize(dst=dst, size=size, params=kwargs)
	
	def raster_is_valid(reference, resolution, **kwargs):
		return reference == resolution

_assemblers = {
	'text': TextAssembler(),
	'image': ImageAssembler()
}

# setup reverse names
for k,v in _assemblers.items():
	v.name = k

def get(name):
	return _assemblers[name]
