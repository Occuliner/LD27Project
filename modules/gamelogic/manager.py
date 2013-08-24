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

import os, math, pygame, random
from picklestuff import loadPlayState
from modules.hud.monitor import Monitor
from modules.hud.ammoicon import AmmoIcon
from modules.hud.label import HudLabel
from modules.hud.bar import Bar
from gamelogicmanager import GameLogicManager

class ActualManager( GameLogicManager ):
    population = 3000000
    populationCounter = None
    ammoHudElements = []
    selectedLaserNum = 0
    lasers = []
    cities = []
    preparedShots = []
    def __init__( self, playState ):
        GameLogicManager.__init__( self, playState)

    def spawnMonitor( self ):
        playState = self.playStateRef()
        mon = Monitor( playState )
        playState.hudList.append(mon)

    def postTick( self, dt ):
        GameLogicManager.postTick( self, dt )
        playState = self.playStateRef()
        for eachShot in ActualManager.preparedShots[:]:
            eachShot[0] += dt
            if eachShot[0] > 0.0:
                self.laserSound.play(priority=2)
                for eachInfo in playState.space.segment_query(eachShot[1][0], eachShot[1][1]):
                    if hasattr(eachInfo.shape, "entity"):
                        if eachInfo.shape.entity.__class__.__name__ == "Missile":
                            self.hitSound.play(priority=1)
                            eachInfo.shape.entity.kill()
                ActualManager.preparedShots.remove(eachShot)

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

    def generateBarHud( self ):
        playState = self.playStateRef()
        playState.hudList.extend( [ Bar( each, playState ) for each in ActualManager.lasers ] )

    def getSelectedLaser( self ):
        return ActualManager.lasers[ActualManager.selectedLaserNum]

    def moveToLeftLaser( self ):
        ActualManager.selectedLaserNum = max(ActualManager.selectedLaserNum-1,0)
    
    def moveToRightLaser( self ):
        ActualManager.selectedLaserNum = min(ActualManager.selectedLaserNum+1,len(ActualManager.lasers)-1)

    def getCurAimLine( self ):
        pt = pygame.mouse.get_pos()
        pt2 = self.getSelectedLaser().rect.center
        lineLen = math.hypot((pt[0]-pt2[0]), (pt[1]-pt2[1]))
        if lineLen == 0:
           return (pt2, pt2)
        coeff = 800.0/lineLen
        pt3 = pt2[0]+(pt[0]-pt2[0])*coeff, pt2[1]+(pt[1]-pt2[1])*coeff
        return (pt2, pt3)

    def shoot( self ):
        playState = self.playStateRef()
        curLaser = ActualManager.lasers[ActualManager.selectedLaserNum]
        if curLaser.ammo < 1 or curLaser.coolDown > 0.0:
            return None
        line = self.getCurAimLine()
        beamClass = playState.devMenuRef().masterEntitySet.getEntityClass("Beam")
        delta = line[1][0]-line[0][0], line[1][1]-line[0][1]
        beamClass( line[0], delta, playState.genericStuffGroup )
        self.laserSound.play(priority=2)
        #ActualManager.preparedShots.append( [0.0, line] )
        curLaser.ammo -= 1
        curLaser.coolDown = 10.0
        self.generateAmmoHud()

    def addPopulationCounter( self ):
        playState = self.playStateRef()
        ActualManager.populationCounter = HudLabel( (80, 500), "Estimated population: " +str(ActualManager.population), playState, pygame.Color(255,255,255) )
        playState.hudList.append(ActualManager.populationCounter)

    def adjustPopulation( self, change ):
        ActualManager.population += change
        ActualManager.populationCounter.text = "Estimated population: " +str(ActualManager.population)
        ActualManager.populationCounter.regenerateImage()

    def spawnMissiles( self ):
        playState = self.playStateRef()

        missileClass = playState.devMenuRef().masterEntitySet.getEntityClass("Missile")
        
        missileCount = random.randint(5, 10)
        for val in range(missileCount):
            loc = (80+640*random.random(), 80)
            target = None
            if random.randint(0,1) == 1:
                target = ActualManager.cities[random.randint(0, len(ActualManager.cities)-1)]
            else:
                target = ActualManager.lasers[random.randint(0, len(ActualManager.lasers)-1)]
            
            delta = target.rect.center[0]-loc[0], target.rect.center[1]-loc[1]
            #length = math.hypot( delta[0], delta[1] )
            #delta = delta[0]*(25.0/length), delta[1]*(25.0/length)
            missileClass( loc, delta, playState.genericStuffGroup )

    def onLoad( self ):
        GameLogicManager.onLoad( self )
        playState = self.playStateRef()
        self.spawnMonitor()
        self.addPopulationCounter()
        
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

        self.laserSound = playState.soundManager.getSound( "lasertone.wav" )
        self.hitSound = playState.soundManager.getSound( "hit.wav" )

        self.generateAmmoHud()
        self.generateBarHud()

        self.spawnMissiles()

        pygame.mixer.music.load(os.path.join("data", "music", "heartbeat.ogg"))
        pygame.mixer.music.play(-1)
