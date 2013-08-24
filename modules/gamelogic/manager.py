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

import os
from picklestuff import loadPlayState
from modules.hud.monitor import Monitor
from modules.hud.ammoicon import AmmoIcon
from gamelogicmanager import GameLogicManager

class ActualManager( GameLogicManager ):
    population = "3000000"
    ammoHudElements = []
    selectedLaserNum = 0
    lasers = []
    cities = []

    def spawnMonitor( self ):
        playState = self.playStateRef()
        mon = Monitor( playState )
        playState.hudList.append(mon)

    def postTick( self, dt ):
        GameLogicManager.postTick( self, dt )
        playState = self.playStateRef()

    def onLaunch( self ):
        GameLogicManager.onLaunch( self )
        playState = self.playStateRef()
        newState = loadPlayState( os.path.join( "data", "maps", "empty" ), playState.floor.tileSet, playState.devMenuRef )
        playState.swap(newState)

    def generateAmmoHud( self ):
        playState = self.playStateRef()
        [ playState.hudList.remove(each) for each in ActualManager.ammoHudElements if each in playState.hudList ]
        ActualManager.ammoHudElements = []
        for eachLaser in [ each for each in playState.genericStuffGroup if "Laser" in each.__class__.__name__ ]:
            x = eachLaser.rect.x-8
            y = eachLaser.rect.bottom
            for ammoNum in range( min(eachLaser.ammo, 10) ):
                inst = AmmoIcon( (x+(8*(ammoNum%5)),y+(9*(ammoNum/5)) ), playState )
                ActualManager.ammoHudElements.append( inst )
        playState.hudList.extend( ActualManager.ammoHudElements )

    def getSelectedLaser( self ):
        return ActualManager.lasers[ActualManager.selectedLaserNum]

    def onLoad( self ):
        GameLogicManager.onLoad( self )
        playState = self.playStateRef()
        self.spawnMonitor()
        
        mapClass = playState.devMenuRef().masterEntitySet.getEntityClass("Map")
        mapClass( playState.genericStuffGroup )

        laserClass = playState.devMenuRef().masterEntitySet.getEntityClass("Laser")
        ActualManager.lasers = [laserClass( (100, 460), playState.genericStuffGroup ),
        laserClass( (400, 480), playState.genericStuffGroup ),
        laserClass( (640, 420), playState.genericStuffGroup )]

        cityClass = playState.devMenuRef().masterEntitySet.getEntityClass("City")
        ActualManager.cities = [cityClass( (150, 460), playState.genericStuffGroup ),
        cityClass( (250, 465), playState.genericStuffGroup ),
        cityClass( (350, 470), playState.genericStuffGroup ),
        cityClass( (450, 480), playState.genericStuffGroup ),
        cityClass( (540, 480), playState.genericStuffGroup ),
        cityClass( (600, 460), playState.genericStuffGroup ),
        cityClass( (670, 420), playState.genericStuffGroup )]

        self.generateAmmoHud()
