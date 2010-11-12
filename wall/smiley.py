import random
import time
import colorsys
from effects import Effect
from allegro import FadeIter
import smiley_util
import math

class TestEffect(Effect):
    class Worm:
	def __init__(self,startp,startc):
		self.hinc=1/128.0
		self.vinc=1/256.0
		self.color=startc
		self.p=startp
	def genhsv(self,oldval):
		(h,s,v)=oldval
		h=h+self.hinc
		v=v-self.vinc
		return (h,s,v)
	def newpixel(self,oldpixel):
		(x,y)=oldpixel
		direction=random.randint(0,3)
		if direction==0:
			x=x+1
		elif direction==1:
			x=x-1
		elif direction==2:
			y=y+1
		else:
			y=y-1
		if x>7: 
			x=0
		elif x<0:
			x=7
		if y>7: 
			y=0
		elif y<0:
			y=7
		return (x,y)
	def draw(self,wall):
		self.color=self.genhsv(self.color)
		wall.pixel(self.p[0],self.p[1]).hsv=self.color
		self.p=self.newpixel(self.p)
   
    def _init(self,kw):
	self.hinc=1/64.0
	self.vinc=1/128.0
	
    def startcolors(self):
	   sh1=random.random()
	   sh2=random.random()
	   d=math.fabs(sh1-sh2)
	   while d<(1/4.0):
		sh2=random.random()
	 	d=math.fabs(sh1-sh2)
	   return (sh1,sh2)

    def rotatepalate(self):
	for x in range(0,8):
		for y in range(0,8):
			(h,s,v)=self.wall.pixel(x,y).hsv
			h=h+self.hinc
			if h>=1:
				h=0
			self.wall.pixel(x,y).hsv=(h,s,v)
    def fadeout(self):
	cont=False
	for x in range(0,8):
		for y in range(0,8):
			(h,s,v)=self.wall.pixel(x,y).hsv
			if v>0:
				cont=True
				v=v-self.vinc
				if v<=0: v=0
			self.wall.pixel(x,y).hsv=(h,s,v)
			
	return cont
	
    def run(self):
	   (sh1,sh2)=self.startcolors()
	   starth=random.random()
	   worm1=self.Worm((3,3),(sh1,1,1))
	   worm2=self.Worm((3,4),(sh2,1,1))
	   #worm3=self.Worm((4,3))
	   #worm4=self.Worm((4,4))
	   self.wall.clear()
   	   for i in range(0,100):
		worm1.draw(self.wall)
		worm2.draw(self.wall)
		#worm3.draw(self.wall)
		#worm4.draw(self.wall)
		self.wall.draw()
		time.sleep(0.04)
	   for i in range(0,250):
		self.rotatepalate()
		self.wall.draw()
	   while self.fadeout():
		self.rotatepalate()
		self.wall.draw()

class BallThingy(Effect):
	class Ball:
		def __init__(self,color,coords,xdir,ydir):
			self.color=color
			self.coords=coords
			(h,s,v)=color
			v=v*0.035
			#v=v*0.2
			self.shadowcolor=(h,s,v)
			self.xdir=xdir
			self.ydir=ydir

		def draw(self,wall):
			(h,s,v)=self.color
			(x,y)=self.coords
			wall.pixel(x,y).hsv=self.color
			wall.pixel(x+1,y).hsv=self.color
			wall.pixel(x,y+1).hsv=self.color
			wall.pixel(x+1,y+1).hsv=self.color
			wall.pixel(x-1,y).hsv=self.shadowcolor
			wall.pixel(x-1,y+1).hsv=self.shadowcolor
			wall.pixel(x+2,y).hsv=self.shadowcolor
			wall.pixel(x+2,y+1).hsv=self.shadowcolor
			wall.pixel(x,y-1).hsv=self.shadowcolor
			wall.pixel(x+1,y-1).hsv=self.shadowcolor
			wall.pixel(x,y+2).hsv=self.shadowcolor
			wall.pixel(x+1,y+2).hsv=self.shadowcolor
		def moveto(self,x,y):
			xerr=0
			yerr=0
			if (x-1)<0:
				xerr=1
				x=1
			elif (x+2)>7:
				xerr=-1
				x=5
			if (y-1)<0:
				yerr=1
				y=1
			elif (y+2)>7:
				yerr=-1
				y=5
			self.coords=(x,y)
			return (xerr,yerr)
		

	def _init(self,hk):
		self.bvr=1/80.0
		self.ballcoords=(random.randint(0,7),random.randint(0,7))
		self.xdir=1
		self.ydir=1
	def drawbackground(self,color,wall):
		(h,s,v)=color
		for y in range(0,8):
			for x in range(0,8):
				wall.pixel(x,7-y).hsv=(h,s,v)
			v=v-self.bvr
	
	def moveball(self,b):
	    (x,y)=b.coords
	    y=y+2*b.ydir
	    x=x+b.xdir
	    b.coords=(x,y)
	    (xerr,yerr)=b.moveto(x,y)
	    if xerr!=0:
		b.xdir=xerr
	    if yerr!=0:
		b.ydir=yerr
	    

	def run(self):
		h=random.random()
		hb=1-h
		b=self.Ball((random.random(),1,1),(random.randint(1,5),random.randint(1,5)),1,1)
		b2=self.Ball((h,1,1),(random.randint(1,5),random.randint(1,5)),-1,1)
		for i in range (1,150):
			wall=self.wall
			wall2=self.wall.copy()
			self.drawbackground((hb,1,0.1),wall)
			b.draw(wall)
			b2.draw(wall)
			self.moveball(b)
			self.moveball(b2)
			fi = FadeIter(wall2, wall, 0.07)
			fi.run()
			#self.wall.draw()
			#time.sleep(0.07)

class LineThing(Effect):
#	def line(self,x0,y0,x1,y1,wall):
#		steep = abs(y1-y0) > abs(x1-x0)
#		print steep
#		if steep:
#			temp=x0
#			x0=y0
#			y0=temp
#			temp=x1
#			x1=y1
#			y1=temp
#		if x0 > x1:
#			temp=x0
#			x0=x1
#			x1=temp
#			temp=y0
#			y1=y0
#			y0=temp
#		deltax = x1 - x0
#		print deltax
#		deltay = abs(y1-y0)
#		print deltay
#		error = 0.0
#		deltaerr = deltay/float(deltax)
#		print deltaerr
#		ystep = 0
#		y = y0
#		if y0 < y1:
#			ystep=1
#		else: 
#			ystep=-1
#		for x in range (x0,x1+1):
#			if steep:
#				wall.pixel(y,x).hsv=(0.5,1,1)
#			else:
#				wall.pixel(x,y).hsv=(0.5,1,1)
#			error = error + deltaerr
#			if error >= 0.5:
#				y = y + ystep
#				error = error - 1.0
#	
	
	def _init(self,kw):
		self.h=0;
		self.hinc=1/128.0
		self.vinc=1/16.0
		

	def inc_h(self):
		self.h=self.h+self.hinc
		if self.h>=1:
			self.h=0

	def run(self):
	    for i in range(0,25):
		for x in range (0,8):
			v=1
			points = smiley_util.line((x,0),(0,7-x))
			for p in points:
				self.wall.pixel(p[0],p[1]).hsv=(self.h,1,v,)
				v=v-self.vinc
			self.inc_h()
			self.wall.draw()
		for x in range (0,8):
			v=1
			points = smiley_util.line((x,0),(7,x))
			for p in points:
				self.wall.pixel(p[0],p[1]).hsv=(self.h,1,v,)
				v=v-self.vinc
			self.inc_h()
			self.inc_h()
			self.wall.draw()
		for x in range (0,8):
			v=1
			points = smiley_util.line((7,x),(7-x,7))
			for p in points:
				self.wall.pixel(p[0],p[1]).hsv=(self.h,1,v,)
				v=v-self.vinc
			self.inc_h()
			self.inc_h()
			self.wall.draw()
		for x in range (0,8):
			v=1
			points = smiley_util.line((7-x,7),(0,7-x))
			for p in points:
				self.wall.pixel(p[0],p[1]).hsv=(self.h,1,v,)
				v=v-self.vinc
			self.inc_h()
			self.inc_h()
			self.wall.draw()
		
			
			


	
def effects():
    return [TestEffect,LineThing,BallThingy]
