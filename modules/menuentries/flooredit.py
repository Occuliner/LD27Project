#    Copyright (c) 2012 Connor Sherson
#
#    This file is part of ThisHackishMess
#
#    ThisHackishMess is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This file defines the FloorEditState, FloorEditButton and TileButton classes."""
import pygame

from imageload import loadImage

from button import Button

from menustate import MenuState

from gridrounding import gridRound

from staticimage import StaticImage

from selectionbox import SelectionBox

from label import Label

class UndoButton( Button ):
	"""UndoButton class, pretty obvious what it does."""
	image = loadImage("undo.png", 2)
	
	def __init__( self, parentState=None ):
		Button.__init__( self, None, None, parentState )
		self.rect = self.image.get_rect()
		self.rect.topleft = ( 44, 18 )
	def push( self, clickKey ):
		"""Call Floor.undoChange() on the playState's floor."""
		if "up" in clickKey:
			self.parentState.floor.undoChange()

class RedoButton( Button ):
	"""RedoButton class, also pretty obvious what it does."""
	image = loadImage("redo.png", 2)
	
	def __init__( self, parentState=None ):
		Button.__init__( self, None, None, parentState )
		self.rect = self.image.get_rect()
		self.rect.topleft = ( 93, 18 )
	def push( self, clickKey ):
		if clickKey is 'mouse1up':
			self.parentState.floor.redoChange()

class TileButton( Button ):
	"""TileButton class, is used for creating Buttons from a given tile in the FloorEditState."""
	def __init__( self, theTile, tileNum, pos, parentState=None ):
		Button.__init__( self, theTile.image, pos, parentState )
		self.tileNum = tileNum
	def push( self, clickKey ):
		"""Sets the parentState (Should be FloorEditState) to start using this given Tile."""
		if clickKey is 'mouse1up' and self.parentState.tileNum is not self.tileNum:
			self.parentState.tileNum = self.tileNum
			if self.paretnState.tileSelectionBox in self.parentState.sprites:
				self.parentState.removeSprite( self.parentState.tileSelectionBox )
			self.parentState.tileSelectionBox = SelectionBox( self.rect, self.parentState )
			self.parentState.addSprite( self.parentState.tileSelectionBox )
			self.parentState.menu.loadMenuState( self.parentState )

class ScrollBackButton( Button ):
	def __init__( self, parentState=None ):
		Button.__init__( self, loadImage( "backarrowsmall.png", 2 ), ( 24, 380 ), parentState )
	def push( self, clickKey ):
		if "up" in clickKey:
			if self.parentState.curPage > 0:
				self.parentState.repage( self.parentState.curPage - 1 )

class ScrollNextButton( Button ):
	def __init__( self, parentState=None ):
		Button.__init__( self, loadImage( "forwardarrowsmall.png", 2 ), ( 116, 380 ), parentState )
	def push( self, clickKey ):
		if "up" in clickKey:
			if self.parentState.curPage < max( self.parentState.pages.keys() ):
				self.parentState.repage( self.parentState.curPage + 1 )
				
				

class FloorEditState( MenuState ):
	"""The FloorEditState class, a MenuState for editing the current PlayState's Floor."""
	#Create the floorEditUpdate function, and create a loop that generates a grid of all of the tiles to select from.
	#Each tile should be converted into a button, the button has the same image, and the push() method sets FloorEditState's current tileNum to it's tile.

	#TileGroups should be a class, and each group a metaclass, so that new tiles can be added while the program is running.
		
	def __init__( self, menu, sprites=[] ):
		MenuState.__init__( self, menu, sprites )

		#print len( self.buttons ), len( self.sprites ), len( sprites )
		self.buttons = []
		self.sprites = [self.fileNameLabel]

		self.panel = StaticImage( loadImage( "devmenu.png", 2 ), ( 10, 10 ) )
		self.addSprite( self.panel )

		self.undoButton = UndoButton( self )
		self.addButton( self.undoButton )

		self.redoButton = RedoButton( self )
		self.addButton( self.redoButton )

		self.scrollNextButton = ScrollNextButton( self )
		self.addButton( self.scrollNextButton )

		self.scrollBackButton = ScrollBackButton( self )
		self.addButton( self.scrollBackButton )
		
		#A local copy to prevent excessive look ups.
		self.floor = self.menu.playState.floor

		self.tileNum = 0

		self.xPos = 0
		self.yPos = 0
		self.tallest = 0
		self.pages = {0:[]}
		self.curPage = 0
		self.processedTiles = set([])
		self.generateButtons()

		#For the tile placing functionality.
		self.startOfBlock = None
		#self.endOfBlock = None

		#curTileNum = 0
		#row = 1
		#column = 0
		#for eachTile in self.floor.tileSet.getTiles():
		#	position = ( column*eachTile.rect.w + 21, row*eachTile.rect.h + 30 )
		#	self.addButton( TileButton( eachTile, curTileNum, position, self ) )
		#	column += 1
		#	if column > 3:
		#		column = 0
		#		row += 1
		#	curTileNum += 1

		self.tileSelectionBox = SelectionBox( self.pages[self.curPage][0].rect, self )
		self.addSprite( self.tileSelectionBox )

	def generateButtons( self ):
		curPageKey = max( self.pages.keys() )
		curTileNum = 0
		for eachTile in self.floor.tileSet.getTiles():
			position = ( self.xPos + 21, self.yPos + 50 )
			givenButton = TileButton( eachTile, curTileNum, position, self )
			self.processedTiles.add( eachTile )
			#self.addButton( givenButton )
			if self.pages.has_key( curPageKey ):
				self.pages[curPageKey].append( givenButton )
			else:
				self.pages[curPageKey] = [ givenButton ]
			self.xPos += ( givenButton.rect.w )
			self.tallest = max( self.tallest, givenButton.rect.h )
			if self.xPos > 108:
				self.xPos = 0
				self.yPos += self.tallest
			if self.yPos > 318:
				self.yPos = 0
				curPageKey += 1
			curTileNum += 1
		map( self.addButton, self.pages[self.curPage] )

	def repage( self, newPageNum ):
		map( self.removeButton, self.pages[self.curPage] )
		self.curPage = newPageNum
		map( self.addButton, self.pages[self.curPage] )
		if self.tileNum not in [ each.tileNum for each in self.pages[self.curPage] ] and self.tileSelectionBox in self.sprites:
			self.removeSprite( self.tileSelectionBox )
		elif self.tileNum in [ each.tileNum for each in self.pages[self.curPage] ] and self.tileSelectionBox not in self.sprites:
			self.addSprite( self.tileSelectionBox )
		self.menu.loadMenuState( self )
	
	def update( self, dt, click, clickKey, curMousePos=None ):
		"""Where the actual Tile placing on the Floor happens."""
		if click is not None:
			if clickKey is 'mouse1down':
				#print "Down"
				
				self.startOfBlock = click
			elif clickKey is 'mouse1up':
				if self.startOfBlock != None:
					#curTile = self.floor.tileSet.getTiles()[self.tileNum]
					curTile = self.processedTiles[self.tileNum]
					
					height = curTile.rect.h
					width = curTile.rect.w
					
					leftBoundary = min( click[0], self.startOfBlock[0] )
					rightBoundary = max( click[0], self.startOfBlock[0] )
					topBoundary = min( click[1], self.startOfBlock[1] )
					bottomBoundary = max( click[1], self.startOfBlock[1] )
	
					x1Position, y1Position = gridRound( [ leftBoundary, topBoundary ], width, height, roundToTopLeft=True )
					x2Position, y2Position = gridRound( [ rightBoundary, bottomBoundary], width, height, roundToTopLeft=False )
					
	
	
					self.floor.writeArea( self.tileNum, pygame.Rect( x1Position, y1Position, x2Position-x1Position, y2Position-y1Position ) )
					self.startOfBlock = None
		elif curMousePos is not None:
			pass

class FloorEditButton( Button ):
	"""The FloorEditButton class, just creates a Button that invokes FloorEditState on the DevMenu."""
	image = loadImage("flooreditbutton.png", 2 )
	rect = image.get_rect()
	rect.topleft = ( 24, 24 )
	def __init__( self, parentState=None ):
		Button.__init__( self,  None, None, parentState )

	def push( self, clickKey ):
		"""Invoke the FloorEditState"""
		#SWITCH TO FLOOREDIT MENU STATE
		if "up" in clickKey:
			aFloorEditState = FloorEditState( self.parentState.menu )
			self.parentState.menu.loadMenuState( aFloorEditState )
