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

import pygame

from imageload import loadImageNoAlpha

from hudelement import HudElement

class Bar(HudElement):
    def __init__( self, laser, playState ):
        self.laser = laser
        sheet = self.generateImage()
        HudElement.__init__( self, playState, (laser.rect.left, laser.rect.top-6), sheet, False )

    def generateImage( self ):
        img = pygame.Surface( (self.laser.width, 5) ).convert()
        img.fill( pygame.Color(0, 255, 0 ) )
        length = (self.laser.width-2)*(self.laser.coolDown/10)
        img.fill( pygame.Color(0, 0, 0 ), pygame.Rect(self.laser.width-1-length, 1, length, 3) )
        return img

    def regenerateImage( self ):
        self.image = self.generateImage()

    def update( self, dt ):
        HudElement.update( self, dt )
        self.regenerateImage()
        
