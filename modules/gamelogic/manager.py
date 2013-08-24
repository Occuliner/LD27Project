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
from modules.hud.blank import Blank
from modules.hud.bar import Bar
from gamelogicmanager import GameLogicManager

class ActualManager( GameLogicManager ):
    displayedPopulation = 3000000
    population = 3000000
    populationCounter = None
    ammoHudElements = []
    selectedLaserNum = 0
    lasers = []
    cities = []
    preparedShots = []
    shakeTimer = 0.0
    shakeAmp = 0.0
    onStartScreen = True
    waveNumber = 0
    waveTimer = 3.0
    waveLabel = None
    endGameNotice = None
    otherEndGameNotice = None
    def __init__( self, playState ):
        GameLogicManager.__init__( self, playState)

    def spawnMonitor( self ):
        playState = self.playStateRef()
        mon = Monitor( playState )
        playState.hudList.append(mon)

    def postTick( self, dt ):
        GameLogicManager.postTick( self, dt )
        playState = self.playStateRef()
        ActualManager.shakeTimer += dt
        if ActualManager.shakeAmp != 0.0:
            ActualManager.shakeAmp -= dt*(ActualManager.shakeAmp-1.0/(ActualManager.shakeAmp))
            ActualManager.shapeAmp = min(ActualManager.shakeAmp, 0.0)
        deltaPop = ActualManager.displayedPopulation-ActualManager.population
        if deltaPop != 0:
            ActualManager.displayedPopulation = max( ActualManager.population, 
                ActualManager.displayedPopulation - max(random.randint(int(deltaPop*0.1), int(deltaPop*0.2) ), 127) )
            ActualManager.populationCounter.text = "Estimated population: " +str(ActualManager.displayedPopulation)
            ActualManager.populationCounter.regenerateImage()
        
        if len( [ each for each in  playState.sprites() if each.__class__.__name__ == "Missile" ] ) < 1 and not ActualManager.onStartScreen:
            if len( [ each for each in ActualManager.cities if not each.destroyed ] ) < 1 and ActualManager.endGameNotice is None:
                ActualManager.endGameNotice = HudLabel( (0, 0), "The End", playState, pygame.Color(255,255,255) )
                ActualManager.endGameNotice.rect.topleft = (800-ActualManager.endGameNotice.rect.w)/2, (600-ActualManager.endGameNotice.rect.h)/2
                ActualManager.otherEndGameNotice = HudLabel( (0, 0), "Press space to restart.", playState, pygame.Color(255,255,255) )
                ActualManager.otherEndGameNotice.rect.topleft = (800-ActualManager.otherEndGameNotice.rect.w)/2, (600-ActualManager.otherEndGameNotice.rect.h)/2 + 20
                playState.hudList.extend( [ActualManager.endGameNotice, ActualManager.otherEndGameNotice] )
            elif ActualManager.waveLabel is None and ActualManager.endGameNotice is None:
                ActualManager.waveNumber += 1
                ActualManager.waveLabel = HudLabel( (0, 0), "Wave "+str(ActualManager.waveNumber), playState, pygame.Color(255,255,255) )
                ActualManager.waveLabel.rect.topleft = (800-ActualManager.waveLabel.rect.w)/2, (600-ActualManager.waveLabel.rect.h)/2
                playState.hudList.append( ActualManager.waveLabel )
                for eachLaser in ActualManager.lasers:
                    if not eachLaser.destroyed:
                        eachLaser.ammo = 8
                self.generateAmmoHud()
            ActualManager.waveTimer -= dt
            if ActualManager.waveTimer < 0.0 and ActualManager.endGameNotice is None:
                ActualManager.waveTimer = 3.0
                self.spawnMissiles()
                playState.hudList.remove( ActualManager.waveLabel )
                ActualManager.waveLabel = None
            
    def spawnStartScreen( self ):
        playState = self.playStateRef()
        playState.hudList.append( Blank( playState ) )
        playState.hudList.append( HudLabel( (0, 0), "End times", playState, pygame.Color(255,255,255) ) )
        playState.hudList.append( HudLabel( (0, 0), "Press space to continue.", playState, pygame.Color(255,255,255) ) )
        playState.hudList[1].rect.topleft = (800-playState.hudList[1].rect.w)/2, (600-playState.hudList[1].rect.h)/2-10
        playState.hudList[2].rect.topleft = (800-playState.hudList[2].rect.w)/2, (600-playState.hudList[2].rect.h)/2+10

    def onLaunch( self ):
        GameLogicManager.onLaunch( self )
        playState = self.playStateRef()
        self.spawnStartScreen()
        pygame.mixer.music.load(os.path.join("data", "music", "heartbeat.ogg"))
        pygame.mixer.music.play(-1)
        
    def loadGame( self ):
        ActualManager.displayedPopulation = 3000000
        ActualManager.population = 3000000
        ActualManager.populationCounter = None
        ActualManager.ammoHudElements = []
        ActualManager.selectedLaserNum = 0
        ActualManager.lasers = []
        ActualManager.cities = []
        ActualManager.preparedShots = []
        ActualManager.shakeTimer = 0.0
        ActualManager.shakeAmp = 0.0
        ActualManager.onStartScreen = True
        ActualManager.waveNumber = 0
        ActualManager.waveTimer = 3.0
        ActualManager.waveLabel = None
        ActualManager.endGameNotice = None
        ActualManager.otherEndGameNotice = None
        playState = self.playStateRef()
        newState = loadPlayState( os.path.join( "data", "maps", "empty" ), playState.floor.tileSet, playState.devMenuRef )
        playState.swap(newState)
        ActualManager.onStartScreen = False

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

    def spawnMissiles( self ):
        playState = self.playStateRef()

        missileClass = playState.devMenuRef().masterEntitySet.getEntityClass("Missile")
        
        missileCount = random.randint(5, 10)
        targets = [ each for each in ActualManager.cities+ActualManager.lasers if not each.destroyed ]
        for val in range(missileCount):
            loc = (80+640*random.random(), 80)
            target = targets[random.randint(0, len(targets)-1)]
            
            delta = target.rect.center[0]-loc[0], target.rect.center[1]-loc[1]
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
        laserClass( (320, 480), playState.genericStuffGroup ),
        laserClass( (480, 480), playState.genericStuffGroup ),
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

        #self.spawnMissiles()
