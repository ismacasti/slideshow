#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, os.path, json
import assembler as asm
import shutil, uuid
from settings import Settings

image_path = os.path.expanduser('~/slideshow/image')

class InvalidSlide(Exception):
	pass

class Slide:
	def __init__(self, id, queue, path, active, assembler, data, stub=False):
		self.id = id
		self._queue = queue
		self._path = path
		self.active = active
		self.assembler = asm.get(assembler)
		self._data = data and json.loads(data) or None
		
		# Tells if this is a full slide (which database entry) or if it is being
		# constructed or is otherwise not complete.
		self._stub = stub
		
		if not os.path.exists(path):
			raise ValueError, "could not locate '{path}' in '{root}'".format(path=path, root=image_path)
	
	def assemble(self, params):
		return json.dumps(self.assembler.assemble(self, **params))
	
	def default_size(self, width=None):
		return self.assembler.default_size(slide=self, src=self._data, width=width)
	
	def raster_path(self, size):
		return os.path.join(image_path, self._path, 'raster', '%dx%d.png' % size)
	
	def src_path(self, item):
		return os.path.join(image_path, self._path, 'src', item)
	
	def _has_raster(self, size):
		return os.path.exists(self.raster_path(size))
	
	def rasterize(self, size, reference):
		"""
		Rasterizes the slide for the given resolution, if needed.
		:param size: Size of the raster
		:param reference: The current resolution (some slides are only valid at
		                  a single resolution, eg text slides, and must be
		                  re-rasterized if the resolution is changed.
		"""
		if not self._raster_is_valid(size, reference):
			self.assembler.rasterize(slide=self, size=size, resolution=reference, **self._data)
	
	def _raster_is_valid(self, size, reference):
		has_raster = self._has_raster(size)
		is_valid = self.assembler.raster_is_valid(slide=self, size=size, reference=reference, **self._data)
		return has_raster and is_valid

def from_id(c, id):
	row = c.execute("""
		SELECT
			id,
			path,
			active,
			assembler,
			data
		FROM
			slide
		WHERE
			id = :id
		LIMIT 1
	""", {'id': id}).fetchone()
	
	if not row:
		raise InvalidSlide, "No slide with id ':id'".format(id=id)
	
	return Slide(queue=None, stub=False, **row)

def create(c, assembler, params):
	settings = Settings('settings.xml', 'settings.json')
	name = '{uuid}.slide'.format(uuid=uuid.uuid1().hex)
	dst = os.path.join(image_path, name)
	
	os.mkdir(dst)
	os.mkdir(os.path.join(dst, 'raster'))
	os.mkdir(os.path.join(dst, 'src'))
	
	# reference resolution
	params['resolution'] = settings.resolution()
	
	slide = Slide(id=None, queue=None, path=dst, active=False, assembler=assembler, data=None, stub=True)
	slide._data = json.loads(slide.assemble(params))
	
	slide.rasterize((200,200)) # thumbnail
	slide.rasterize((800,600)) # windowed mode (debug)
	slide.rasterize(settings.resolution())
	
	c.execute("""
		INSERT INTO slide (
			queue_id,
			path,
			assembler,
			data
		) VALUES (
			1,
			:path,
			:assembler,
			:data
		)
	""", dict(path=slide._path, assembler=slide.assembler.name, data=json.dumps(slide._data)))
	
	return slide

def delete(c, id):
	s = from_id(c, id)
	
	c.execute("""
		DELETE FROM
			slide
		WHERE
			id = :id
	""", dict(id=s.id))
	
	shutil.rmtree(s._path)
