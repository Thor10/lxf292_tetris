import random, os, pygame
import pygame.mixer
from pygame.locals import *

#if not pygame.font: print 'Warning, fonts disabled'
#if not pygame.mixer: print 'Warning, sound disabled'

def load_image(name, colorkey=None):  # Basic function to load images
    fullname = os.path.join('Image', name)
    try:
        image = pygame.image.load(fullname)
    except (pygame.error, message):
        raise SystemExit(message)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def load_sound(name):                # Basic function to load sounds
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join('SFX', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except (pygame.error, message):
        raise SystemExit(message)
    return sound

class piece:
    """Common Tetris block, it has 4 squares"""
    def __init__(self, choice):
        # Pieces layout
        # 1 = BAR  2 = BLOCK 3 = 3-toes
        # 4 = S    5 = Z     6 = F      7 = 7
        self.yVal = 0  #Setup initial values for position, velocity, state
        self.xVal = 4
        self.xVelocity = 0
        self.yVelocity = 0
        self.timer = 0 # A timer used for movement
        self.state = 1
        self.piecechosen = choice  #Used when checking against chosen piece
        #setup sounds to use
        self.moveclick = load_sound("takeoff.wav")
        self.rotateclick = load_sound("click.wav")
        # Block layout
        #  Blocks[0] - First Block   =  Left most block
        #  Blocks[1] - Second Block  =  Top Most block
        #  Blocks[2] - Third Block   =  Right most block
        #  Blocks[3] - Fourth Block  =  Bottom most block
        #  block(x value, y value) according to a 4 x 4 grid
        if choice == 1:    #Red block is the horizontal bar
            self.blockimage = load_image("redblock.gif")
            self.blocks = [ block(1, 0), block(1, 1), block(1, 2), block(1, 3) ]
        elif choice == 2:  #Yellow block is the square
            self.blockimage = load_image("yellowblock.gif")
            self.blocks = [ block(0, 1), block(0, 0), block(1, 0), block(1, 1) ]
        elif choice == 3:  #Turqoise block is the T shaped piece
            self.blockimage = load_image("turqblock.gif")
            self.blocks = [ block(0, 0), block(1, 0), block(2, 0), block(1, 1) ]
        elif choice == 4:  #Purple block is the S block
            self.blockimage = load_image("purpleblock.gif")
            self.blocks = [ block(0, 1), block(1, 0), block(2, 0), block(1, 1) ]
        elif choice == 5:  #Green block is the Z block
            self.blockimage = load_image("greenblock.gif")
            self.blocks = [ block(0, 0), block(1, 0), block(2, 1), block(1, 1) ]
        elif choice == 6:  #Blue block is the F shaped block
            self.blockimage = load_image("blueblock.gif")
            self.blocks = [ block(0, 1), block(0, 0), block(1, 0), block(0, 2) ]
        elif choice == 7:  #Orange block is the 7 shaped block
            self.blockimage = load_image("orangeblock.gif")
            self.blocks = [ block(0, 0), block(1, 0), block(1, 1), block(1, 2) ]
        else:              #Something tried to load an invalid block
            return

    def rotateright(self, grid):
        if (self.piecechosen != 2):  #NOT THE YELLOW BLOCK PIECE, OH GOD NO
            oldstate = self.state    #Just incase it can't rotate
            if (self.piecechosen == 1) or (self.piecechosen == 4) or (self.piecechosen == 5): # 2 states, horizontal & vertical
                self.state = 2 - (self.state - 1) #switches 1 and 2
            elif (self.piecechosen == 3) or (self.piecechosen == 6) or (self.piecechosen == 7): # 4 states, T, |-, _|_, and -|
                if self.state > 3:   # increments 1-4, looping back to 1
                    self.state = 1
                else:
                    self.state += 1
            oldblocks = self.blocks  #Just incase it can't rotate
            self.rotation()          # Rotate it!
            if gridcollision(self, grid, 4): #check to see if it collided
                self.blocks = oldblocks  #it did, so set old values back
                self.state = oldstate
            else:
                self.rotateclick.play()

    def rotateleft(self, grid):
        if self.piecechosen != 2:   #NOT THE YELLOW BLOCK PIECE, OH GOD NO
            oldstate = self.state    #Just incase it can't rotate
            if (self.piecechosen == 1) or (self.piecechosen == 4) or (self.piecechosen == 5): # 2 states, horizontal & vertical
                self.state = 2 - (self.state - 1) #switches 1 and 2
            elif (self.piecechosen == 3) or (self.piecechosen == 6) or (self.piecechosen == 7): # 4 states, T, |-, _|_, and -|
                if self.state < 2:   # decrements 1-4, looping back to 4
                    self.state = 4
                else:
                    self.state -= 1
            oldblocks = self.blocks  #Just incase it can't rotate
            self.rotation()          #Rotate it!
            if gridcollision(self, grid, 4): #check to see if it collided
                self.blocks = oldblocks #it did so set old values back
                self.state = oldstate
            else:
                self.rotateclick.play()
                
#NITTY GRITTY ROTATION FUNCTION, contains all states in list-grid form
    def rotation(self):
        if self.piecechosen == 1: # 2 states, horizontal & vertical
            if self.state == 1:
                self.blocks = [ block(1, 0), block(1, 1), block(1, 2), block(1, 3) ]
            if self.state == 2:
                self.blocks = [ block(0,0), block(1,0), block(3,0), block(2, 0) ]
        elif self.piecechosen == 3: # 4 states, T, |-, _|_, and -|
            if self.state == 1:
                self.blocks = [ block(0,0), block(1,0), block(2,0), block(1,1) ]
            elif self.state == 2:
                self.blocks = [ block(0,1), block(1,0), block(1,1), block(1,2) ]
            elif self.state == 3:
                self.blocks = [ block(0,1), block(1,0), block(2,1), block(1,1) ]
            elif self.state == 4:
                self.blocks = [ block(0,1), block(0,0), block(1,1), block(0,2) ]
        elif self.piecechosen == 4: # 2 states, S and '-,
            if self.state == 1:
                self.blocks = [ block(0,1), block(1,0), block(2,0), block(1,1) ]
            elif self.state == 2:
                self.blocks = [ block(0,1), block(0,0), block(1,1), block(1,2) ]
        elif self.piecechosen == 5: # 2 states, Z and ,-'
            if self.state == 1:
                self.blocks = [ block(0, 0), block(1, 0), block(2, 1), block(1, 1) ]
            elif self.state == 2:
                self.blocks = [ block(0,1), block(1,0), block(1,1), block(0,2) ]
        elif self.piecechosen == 6: # 4 steps, F, |_, _|, --,
            if self.state == 1:
                self.blocks = [ block(0, 1), block(0, 0), block(1, 0), block(0, 2) ]
            elif self.state == 2:
                self.blocks = [ block(0, 0), block(1, 0), block(2, 0), block(2, 1) ]
            elif self.state == 3:
                self.blocks = [ block(0, 2), block(1, 0), block(1, 1), block(1, 2) ]
            elif self.state == 4:
                self.blocks = [ block(0, 1), block(0, 0), block(2, 1), block(1, 1) ]
        elif self.piecechosen == 7: # 4 step, 7, ,-- , L , --'
            if self.state == 1:
                self.blocks = [ block(0, 0), block(1, 0), block(1, 1), block(1, 2) ]            
            elif self.state == 2:
                self.blocks = [ block(0, 1), block(2, 0), block(2, 1), block(1, 1) ]
            elif self.state == 3:
                self.blocks = [ block(0, 1), block(0, 0), block(1, 2), block(0, 2) ]
            elif self.state == 4:
                self.blocks = [ block(0, 0), block(1, 0), block(2, 0), block(0, 1) ]

#If the Left block (block[0]) is on the left wall, don't move
    def moveleft(self):
        if (self.blocks[0].xGrid + self.xVal) > 0:
            self.xVal -= 1
            self.moveclick.play()
        self.xVelocity = -(1) #Always set to allow holding dir. to slide

#if the Right block (block[2]) is on the right wall, don't move
    def moveright(self):
        if (self.blocks[2].xGrid + self.xVal) < 9:
            self.xVal += 1
            self.moveclick.play()
        self.xVelocity = 1 #Always set to allow holding dir. to slide 

#If the Bottom block (block[3]) is on the bottom, don't move
    def movedown(self):
        if ((self.blocks[3].yGrid + self.yVal) < 19):
            self.yVal += 1
            self.yVelocity = 1 #Only increase velocity during true

#Combines the four blocks to display a tetris piece
    def blitimage(self, screen, isNext):
        if isNext == 0:  #This is not the piece sitting on the top right
            for i in range(0, 4):
                currentX = 240 + (self.xVal*16) + (self.blocks[i].xGrid*16)
                currentY = 80 + (self.yVal*16) + (self.blocks[i].yGrid*16)
                screen.blit(self.blockimage, (currentX, currentY))
        else: #This IS the piece sitting on the top right
            for i in range(0, 4):
                currentX = 478 + (self.blocks[i].xGrid*16)
                currentY = 63 + (self.blocks[i].yGrid*16)
                screen.blit(self.blockimage, (currentX, currentY))

#Drops the piece one down, used when delaycounter = delayrate
    def drop(self):
        self.yVal += 1

#Updates the piece, uses velocity to do quick moves (aka hold right)
    def update(self, Grid):
        if self.xVelocity < 0:  #Is it moving left?
            if (self.timer < 20):
                self.timer += 1
            else:
                if not gridcollision(self, Grid, 1):
                    self.moveleft()
        elif self.xVelocity > 0: #Is it moving right?
            if (self.timer < 20):
                self.timer += 1
            else:
                if not gridcollision(self, Grid, 2):
                    self.moveright()
        if self.yVelocity > 0:  #Is it going down?
            if not gridcollision(self, Grid, 3):
                self.movedown()

class block:
    """ One of the Four blocks used in a tetris piece """
    def __init__(self, x, y):
        # X and Y are 0-3, and are used to determine where
        # the block is on the 4x4 grid used with Piece
        self.xGrid = x   
        self.yGrid = y
        
class grid:
    """ Tetris grid, contains all of the dropped blocks """
    def __init__(self):  #setup the 2D list
        self.layers = [[[0 for x in range(0,10)] for y in range(0,20)]]
        self.currentgrid = self.layers[0]
        for i in range(0,20):
            for j in range(0, 10):
                self.currentgrid[i][j] = 0
        self.height = 0  #Current height of grid is 0 (no blocks)
        #This is a bunch of predefined images loaded into a list
        self.blockimages = [ load_image("redblock.gif"), load_image("yellowblock.gif"),\
                       load_image("turqblock.gif"), load_image("purpleblock.gif"),\
                       load_image("greenblock.gif"), load_image("blueblock.gif"),\
                       load_image("orangeblock.gif"), load_image("whiteblock.gif") ]

    def blitgrid(self, screen):
        # Setup for Blit Image
        # 1 = BAR  2 = BLOCK 3 = 3-toes
        # 4 = S    5 = Z     6 = F      7 = 7
        #    OR
        # 1 = RED  2 = YELLOW 3 = TURQOISE
        # 4 = PUPRLE    5 = GREEN     6 = BLUE  7 = ORANGE
        # 8 = WHITE BLOCK --> only occurs during tetris
        #  NOTE: 20 - self.height is a method to use dynamic blitting :)
        for i in range(20 - (self.height), 20):
            for j in range(0, 10):
                blcolor  = self.currentgrid[i][j]
                if blcolor > 0:
                    currentX = 240 + (j*16)
                    currentY = 80 + (i*16)
    #The value of the grid[x][y] implies the color the block should be,
    # 1 = red, 2 = yellow, etc. so the list equivalent is color - 1 
                    screen.blit(self.blockimages[blcolor-1],\
                                                 (currentX, currentY))
                    
#Adds a Tetris piece to the grid, and increments height accordingly
    def addpiece(self, piece):
        for i in range(0,4): #add each piece to the grid
            xSet = piece.xVal + piece.blocks[i].xGrid
            ySet = piece.yVal + piece.blocks[i].yGrid
            self.currentgrid[ySet][xSet] = piece.piecechosen
            if ( self.height < 20 - piece.yVal ):
                self.height = 20 - piece.yVal
                #  DEBUG STATEMENT ^

# TO FIX - only check rows that current piece has just been placed in
# IDEA - just input a list as TETRIS ROWS, and check them
#          then possibly rewrite list to only have TETRIS rows for animation
    def hasTetris(self):
        row_tetris = 1  #setup as the row has a tetris, will turn off
        has_tetris = 0  #does the grid have a tetris?
        for i in range(20 - (self.height), 20):
            for j in range(0, 10):
                if self.currentgrid[i][j] == 0:
                    row_tetris = 0 # ok, this row doesn't have a tetris
                    j = 9          # break the loop the old fashion way
            if row_tetris == 1:  #Did we have a tetris?
                for j in range(0, 10):
                    self.currentgrid[i][j] = 8
                has_tetris = 1   # WE HAVE A TETRIS, but keep counting
            row_tetris = 1       #Setup row_tetris again
        if has_tetris == 1: #Do we have a tetris?
            return True  #  YES
        else:
            return False #  NO

# TO DO - redo the drop detection, its crap right now
# IDEA  - get rid of the damn copy list (newgrid), and just use the
#           current grid, aka drop them all after row has been deleted
# TO FIX - like above, input a list of known tetrises, so no checks involved
    def animTetris(self, screen, bg1, clock):
        pulsenoise = load_sound("pulse.wav")
        linecount = 0
        layers = [[[0 for x in range(0,10)] for y in range(0,20)]]
        newgrid = layers[0]
        for i in range(0,20):
            for j in range(0, 10):
                newgrid[i][j] = self.currentgrid[i][j]
        for i in range(20 - (self.height), 20):
            if self.currentgrid[i][0] == 8:
                linecount += 1  # points = 13 + 5*(25*(2^pointsearned-1))
                for j in range(0, 10):
                    self.currentgrid[i][j] = 0
                    for k in range(1, i):
                        newgrid[k+1][j] = self.currentgrid[k][j]
                    screen.blit(bg1, (240, 80))
                    self.blitgrid(screen)
                    clock.tick(30)
                    pulsenoise.play()
                    pygame.display.flip()
                self.height -= 1
            #  DEBUG STATEMENT ^
            for i in range(0,20):
                for j in range(0, 10):
                    self.currentgrid[i][j] = newgrid[i][j]
        return (linecount)

def gridcollision(Piece, Grid, Direction):
    """Grid collision, to test if next move will collide"""
    #Direction Layout
    # 1 = Left  2 = Right  3 = Down   4 = No Movement
    if Direction == 1:
        for i in range(0,4):
            if (Piece.xVal + Piece.blocks[i].xGrid - 1) >= 0:
                if Grid.currentgrid[Piece.yVal + Piece.blocks[i].yGrid][Piece.xVal + Piece.blocks[i].xGrid - 1] > 0:
                    return True  # there was a collision
    elif Direction == 2:
        for i in range(0,4):
            if (Piece.xVal + Piece.blocks[i].xGrid + 1) < 10:
                if Grid.currentgrid[Piece.yVal + Piece.blocks[i].yGrid][Piece.xVal + Piece.blocks[i].xGrid + 1] > 0:
                    return True
    elif Direction == 3:
        for i in range(0,4):
            if (Piece.yVal + Piece.blocks[i].yGrid + 1) < 20:
                if (Grid.currentgrid[Piece.yVal + Piece.blocks[i].yGrid + 1][Piece.xVal + Piece.blocks[i].xGrid]) > 0:
                    return True
    elif Direction == 4:
        for i in range(0,4):
            if (Piece.xVal + Piece.blocks[i].xGrid > 9) or (Piece.xVal + Piece.blocks[i].xGrid < 0):
                return True
            elif (Piece.yVal + Piece.blocks[i].yGrid < 0) or (Piece.yVal + Piece.blocks[i].yGrid > 19):
                return True
            elif (Grid.currentgrid[Piece.yVal + Piece.blocks[i].yGrid][Piece.xVal + Piece.blocks[i].xGrid]) > 0:
                return True
    return False   # no collisions found, shame

def main():
    """main Function."""

#Start Pygame
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('LXF 292')
    while(1):
        if(Game(screen)):
            if(GameOver(screen)):
                pass
            else:
                return
        else:
            return

def Game(screen):
    #Load Background and Grid Images
    titlescreen = load_image('background1.jpg')
    screen.blit(titlescreen, (0,0))

    bggrid = load_image('gridbg1.gif')
    screen.blit(bggrid, (240,80))

#Load sound for dropping
    droppulse = load_sound("pulse.wav")

#Initial game variables
    currentlevel = 1
    currentlines = 0
    dropcounter = 0
    currentscore = 0
    currenthiscore = 99999999

#Defined variables
    droprate = 30 / (currentlevel * 0.5)

#initiate clock
    clock = pygame.time.Clock()

#setup tetris blocks
    currentBlock = piece(random.randint(1,7))
    nextBlock    = piece(random.randint(1,7))
    nextBlock.blitimage(screen, 1)

#has the block moved? (used for blitting optimization)
    block_moved = 1

#setup game grid
    gameGrid = grid()

#Text output
    if pygame.font:
        font = pygame.font.Font(None, 40)
        #setup Text
        cscoreText = font.render(str(currentscore), 0, (255,255,255))
        cscoreTextpos = cscoreText.get_rect()
        cscoreTextpos.topright = (200,65)
        hiscoreText = font.render(str(currenthiscore), 0, (255,255,255))
        hiscoreTextpos = hiscoreText.get_rect()
        hiscoreTextpos.right = 200
        hiscoreTextpos.top = 185
        levelText = font.render(str(currentlevel), 0, (255, 255, 255))
        levelTextpos = levelText.get_rect()
        levelTextpos.topright = (505, 225)
        screen.blit(cscoreText, cscoreTextpos)
        screen.blit(hiscoreText,hiscoreTextpos)
        screen.blit(levelText, levelTextpos)
        
    while(1):

        clock.tick(60) #Increment @ 60fps (or 1/60th of a second)

#handles key inputs and QUIT event        
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    return False
                elif event.key == K_p:
                    Pause(screen, clock) # PAUSE THE GAME
                    clock.tick(5)
                    screen.blit(titlescreen, (0,0))
                    screen.blit(bggrid, (240,80))
                    nextBlock.blitimage(screen, 1)
                    gameGrid.blitgrid(screen)
                    currentBlock.blitimage(screen, 0)
                    if pygame.font:
                        screen.blit(cscoreText, cscoreTextpos)
                        screen.blit(hiscoreText, hiscoreTextpos)
                        screen.blit(levelText, levelTextpos)
                #Valid Keys = Left, Right, Down, Z, and X
                if event.key == K_LEFT:
                    #Check grid collision if blocks are moved to the left
                    if not gridcollision(currentBlock, gameGrid, 1):
                        currentBlock.moveleft()
                        block_moved = 1
                elif event.key == K_RIGHT:
                    #Check grid collision if blocks are moved to the right
                    if not gridcollision(currentBlock, gameGrid, 2):
                        currentBlock.moveright()
                        block_moved = 1
                if event.key == K_DOWN:
                    #Check grid collision if blocks are moved down
                    if not gridcollision(currentBlock, gameGrid, 3):
                        currentBlock.movedown()
                        block_moved = 1
                if event.key == K_z:
                    #Rotate the block counter clockwise
                    currentBlock.rotateleft(gameGrid)
                    block_moved = 1
                elif event.key == K_x:
                    #Rotate the block clockwise
                    currentBlock.rotateright(gameGrid)
                    block_moved = 1
#handles when keys are released, used for quick movements (aka hold down right)
            elif event.type == KEYUP:
                #movement has ceased so set velocities to 0 (timer used for dash)
                if (event.key == K_LEFT) or (event.key == K_RIGHT):
                    currentBlock.xVelocity = 0
                    currentBlock.timer = 0
                if event.key == K_DOWN:
                    currentBlock.yVelocity = 0

#Update the current block's values, checking velocities for movement
        currentBlock.update(gameGrid)
        
#Drop counter is used to determine when the piece should drop, at this point
# increment it to drop the tetris block.
        dropcounter += 1
#checks to see if drop counter has hit the drop rate
        if (dropcounter >= droprate):
            if gridcollision(currentBlock, gameGrid, 3): #hit a block
                gameGrid.addpiece(currentBlock)
                droppulse.play()
                currentBlock = nextBlock
                nextBlock = piece(random.randint(1,7))
                if gridcollision(currentBlock, gameGrid, 4):
                    currentBlock.blitimage(screen, 0)
                    return True
                if gameGrid.hasTetris():
                    # Setup for adding to score, and adding lines for level
                    linecount = gameGrid.animTetris(screen, bggrid, clock)
                    currentlines += linecount
                    if currentlines > 18:  # will reach this at 20 lines
                        currentlevel += 1
                        currentlines = 0
                        droprate = 30 / (currentlevel * 0.5)
                        if pygame.font:
                            levelText = font.render(str(currentlevel), 0, \
                                                     (255,255,255))
                            levelTextpos = levelText.get_rect()
                            levelTextpos.topright = (505, 225)
                    totalpoints = 1
                    for i in range(1, linecount):
                        totalpoints *= 2
                    currentscore += 53 + 125*totalpoints
                    
                    if pygame.font:
                        cscoreText = font.render(str(currentscore), 0, \
                                                 (255,255,255))
                        cscoreTextpos = cscoreText.get_rect()
                        
                        cscoreTextpos.topright = (200, 65)
                        
            elif  (currentBlock.blocks[3].yGrid + currentBlock.yVal < 19):
                currentBlock.drop()  # all clear, so lets drop it
            else:   # Hit the bottom
                gameGrid.addpiece(currentBlock)
                droppulse.play()
                currentBlock = nextBlock
                nextBlock = piece(random.randint(1,7))
                if gridcollision(currentBlock, gameGrid, 4):
                    currentBlock.blitimage(screen, 0)
                    return True
                if gameGrid.hasTetris():
                    # Setup for adding to score, and adding lines for level
                    linecount = gameGrid.animTetris(screen, bggrid, clock)
                    currentlines += linecount
                    if currentlines > 18:  # will reach this at 20 lines
                        currentlevel += 1
                        currentlines = 0
                        droprate = 30 / (currentlevel * 0.5)
                        if pygame.font:
                            levelText = font.render(str(currentlevel), 0, \
                                                     (255,255,255))
                            levelTextpos = levelText.get_rect()
                            levelTextpos.topright = (505, 225)
                    totalpoints = 1
                    for i in range(1, linecount):
                        totalpoints *= 2
                    currentscore += 53 + 125*totalpoints
                    
                    if pygame.font:
                        cscoreText = font.render(str(currentscore), 0, \
                                                 (255,255,255))
                        cscoreTextpos = cscoreText.get_rect()
                        cscoreTextpos.topright = (200, 65)

            block_moved = 1
            dropcounter = 0

#   ONLY BLIT IF PLAYER HAS MOVED
        if not ( currentBlock.xVelocity == 0 and currentBlock.yVelocity == 0 and block_moved == 0 ):
            screen.blit(titlescreen, (0,0))
            screen.blit(bggrid, (240,80))
            nextBlock.blitimage(screen, 1)
            gameGrid.blitgrid(screen)
            currentBlock.blitimage(screen, 0)
            if pygame.font:
                screen.blit(cscoreText, cscoreTextpos)
                screen.blit(hiscoreText, hiscoreTextpos)
                screen.blit(levelText, levelTextpos)
        block_moved = 0

        pygame.display.flip()

def GameOver(screen):
    gameoverimage = load_image("gameover.gif")
    screen.blit(gameoverimage, (180, 200))
    pygame.display.flip()
    while(1):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    return False
                elif event.key == K_RETURN:
                    return True
    

def Pause(screen, clock):
    pauseimage = load_image("pause.gif")
    screen.blit(pauseimage, (180, 200))
    pygame.display.flip() #display pause image
    while(1):
        clock.tick(60)
#handles key inputs and QUIT event        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_p:
                    return   #break out of PAUSE
    
if __name__ == '__main__': main()
