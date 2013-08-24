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

import pygame, os

from imageload import loadImageNoAlpha

from hudelement import HudElement

class Label(HudElement):
    font = pygame.font.Font( os.path.join( "data", "fonts", "PD-tarzeau_-_Atari_Small.ttf" ), 16 )
    def __init__( self, pos, text, playState, colour=None ):
        self.text = text
        if colour is None:
            colour =  pygame.Color(0,0,0)
        self.colour = colour
        sheet = self.font.render( self.text, False, colour )
        HudElement.__init__( self, playState, pos, sheet, False )

    def regenerateImage( self ):
        tmpLoc = self.rect.topleft
        self.image = self.font.render( self.text, False, self.colour )
        self.rect = self.image.get_rect()
        self.rect.topleft = tmpLoc
