# Copyright (c) 2013 Connor Sherson
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
#    1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
#
#    2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
#
#    3. This notice may not be removed or altered from any source
#    distribution.

from entity import Entity
import pygame, random

from imageload import loadImageNoAlpha

def queueCollideWithCity( givenCity, givenObject ):
    curPlayState = givenObject.groups()[0].playState
    curPlayState.postStepQueue.append( ( collideWithCity, givenCity, givenObject ) )

def collideWithCity( givenCity, givenObject ):
    if "Missile" in givenObject.__class__.__name__:
        givenCity.destroy()
        givenObject.kill()

class City( Entity ):
    width = 20
    height = 20

    playStateGroup = "genericStuffGroup"
    setName = "genericstuff"

    sheetFileName = "city.png"
    sheet = loadImageNoAlpha( sheetFileName )
    colourKey = pygame.Color(255, 0, 255)
    sheet.set_colorkey(colourKey)

    instanceSpecificVars = None

    notEditable = True

    collidable = True
    solid = False

    specialCollision = queueCollideWithCity
    
    def __init__( self, pos, group=None, **kwargs ):
        Entity.__init__( self, pos, [0,0], None, group, pygame.Rect( 0, 0, self.width, self.height ), animated=True, **kwargs )
        self.animations["online"] = { 'fps':1, 'frames':[0] }
        self.animations["offline"] = { 'fps':1, 'frames':[1] }
        self.destructionSound = group.playState.soundManager.getSound( "destruction.wav" )
        self.explosionSound = group.playState.soundManager.getSound( "explosion.wav" )
        #self.explosionSound.set_volume(0.2)
        if City.instanceSpecificVars is None:
            attrList = list( self.__dict__.keys() )
        self.destroyed = False
        if City.instanceSpecificVars is None:
            City.instanceSpecificVars = dict( [ ( eachKey, eachVal ) for eachKey, eachVal in self.__dict__.items() if eachKey not in attrList ] )
    
    def destroy( self ):
        playState = self.playStateRef()
        self.destructionSound.play(priority=1)
        self.explosionSound.play(priority=1)
        playState.gameLogicManager.__class__.shakeAmp += 5
        if self.destroyed:
            return None
        self.changeAnimation("offline")
        pop = playState.gameLogicManager.population
        cityCount = len( [ each for each in playState.gameLogicManager.cities if not each.destroyed ] )
        if cityCount == 1:
            playState.gameLogicManager.adjustPopulation( -pop )
        else:
            playState.gameLogicManager.adjustPopulation( -int(pop*((0.9+0.2*random.random())/cityCount)) )
        self.destroyed = True

    def update( self, dt ):
        Entity.update( self, dt )

entities = { "City":City }
