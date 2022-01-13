# Space Invaders (v.1.8)
# code by G.G.Otto

import turtle
from tkinter import *
import tkinter.messagebox as message
import time
import random
import os

class Player(turtle.RawTurtle):
    '''represents the player'''

    def __init__(self, master, numBullets, cooldown):
        '''Player(master, numBullets, cooldown) -> Player
        the player for the game'''
        turtle.RawTurtle.__init__(self, master.get_screen())
        self.pu()
        self.shape("player.gif")
        self.goto(0,-275)
        self.last = 0
        self.cooldown = cooldown
        self.bullets = [Bullet(master, "yellow", master.get_aliens()) for i in range(numBullets)]
        self.master = master
        self.speed = 20
        self.isMoving = False

        # key bindings
        canvas = master.get_canvas()
        canvas.bind_all("<space>",self.shoot)
        canvas.bind_all("<Up>",self.shoot)
        canvas.bind_all("<Left>",self.move_left)
        canvas.bind_all("<Right>",self.move_right)
        
    def get_bullets(self):
        '''Player.get_bullets() -> list
        returns a list with all player's bullets'''
        return self.bullets

    def minus_cooldown(self, minus):
        '''Player.minus_cooldown(minus) -> None
        minuses from cooldown'''
        if self.cooldown > 0.85:
            self.cooldown -= minus

    def shoot(self,event=''):
        '''Player.shoot(event='') -> None
        shoots a bullet'''
        if time.time() - self.last < self.cooldown:
            return

        for bullet in self.bullets:
            if not bullet.is_moving():
                self.last = time.time()
                bullet.launch((self.xcor(), self.ycor()+20), 90)
                return

    def move_left(self, event=''):
        '''Player.move_left(event) -> None
        moves the player to the left'''
        width = self.master.get_screen().window_width()
        if self.master.is_over() or self.isMoving or \
           -width/2+25 >= self.xcor():
            return

        self.isMoving = True
        self.bk(self.speed)
        self.master.get_screen().update()
        self.isMoving = False

    def move_right(self, event=''):
        '''Player.move_right(event) -> None
        moves the player to the right'''
        width = self.master.get_screen().window_width()
        if self.master.is_over() or self.isMoving or \
           self.xcor() >= width/2-25:
            return

        self.isMoving = True
        self.fd(self.speed)
        self.master.get_screen().update()
        self.isMoving = False
        
class Bullet(turtle.RawTurtle):
    '''represent's the player's bullet'''

    def __init__(self, master, color, aliens=None, radius=16, wait=30):
        '''Bullet(master, color, aliens=None) -> Bullet
        creates a bullet at the position of shootFrom'''
        turtle.RawTurtle.__init__(self, master.get_screen())
        self.pu()
        self.ht()
        self.shape("triangle")
        self.color(color)
        self.initColor = color
        self.shapesize(0.2,0.7)
        self.isMoving = False
        self.exploding = False
        self.master = master
        self.aliens = aliens
        self.radius = radius
        self.pensize(5)
        self.wait = wait

    def is_moving(self):
        '''Bullet.is_moving() -> bool
        returns if the bullet is moving or not'''
        return self.isMoving or self.exploding

    def get_radius(self):
        '''Bullet.get_radius() -> int
        returns the radius of the bullet's explosion'''
        return self.radius

    def launch(self, pos, heading):
        '''Bullet.launch(pos, heading) -> None
        launches the bullet from pos in direction'''
        if self.master.is_over():
            return

        self.isMoving = False
        self.color(self.initColor)
        self.goto(pos)
        self.st()
        self.seth(heading)
        self.isMoving = True
        self.start_movement()

    def start_movement(self):
        '''Bullet.start_movement() -> None
        starts the bullet moving'''
        if not self.isMoving or self.master.is_over():
            return

        self.fd(10)

        # check if out of site
        width = self.master.get_screen().window_width()/2
        if self.ycor() < -width or self.ycor() > width:
            self.explode()
            return

        # check for aliens
        if self.aliens != None:
            alienShot = self.aliens.shoot_alien(self.pos())
            if alienShot[0]:
                self.explode(["red",("","lime","yellow","hot pink")[alienShot[2]]],
                    40, 5, alienShot[1])
                return

        # check for spaceship
        x,y = self.master.get_spaceship().pos()
        if x - 50 <= self.xcor() <= x + 50 and \
           y - 20 <= self.ycor() <= y + 20:
            self.explode(["blue","blue","blue","dark grey","dark grey"], 50, 7, self.master.get_spaceship().pos())
            self.master.get_spaceship().stop()
            # add score for spaceship
            self.master.add_score(100)
            return

        # shoot at shields
        for shield in self.master.get_shields():
            shield.shoot_shield(self)
            
        self.master.get_screen().update()
        self.master.get_screen().ontimer(self.start_movement, self.wait) 

    def explode(self, colors=None, size=None, speed=5, pos=None):
        '''Bullet.explode(colors=None, size=None, pos=None) -> None
        hides the bullet and stops its movement'''
        self.ht()
        self.isMoving = False

        # explode
        if colors != None:
            self.exploding = True
            self.expSize = 5
            self.expColors = colors
            self.expSpeed = speed
            self.expMax = size

            # get pos
            if pos == None:
                self.expPos = self.pos()
            else:
                self.expPos = pos

            self.explosion()

    def explosion(self):
        '''Bullet.explosion() -> None
        creates an explosion'''
        # add to dict            
        if self.expSize > self.expMax:
            self.clear()
            self.exploding = False
            return

        # get into position
        self.color(random.choice(self.expColors))
        self.clear()
        self.goto(self.expPos)
        self.fd(self.expSize)
        self.left(90)

        # draw explosion
        self.pd()
        self.circle(self.expSize)
        self.pu()
        self.right(90)
        self.expSize += self.expSpeed

        self.master.get_screen().update()
        self.master.get_screen().ontimer(self.explosion, 12)  
        
class Shield:
    '''represents the shield'''

    def __init__(self, master, x, y, width, height, color):
        '''Shield(master, x,y,width,height) -> Shield
        constructs a shield with dimestion width x height and postion (x,y)'''
        master.get_canvas().create_rectangle(x-width/2, -y-height/2, x+width/2, -y+height/2, fill=color)
        self.holes = []

        # store postion date
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.master = master

    def get_holes(self):
        '''Shield.get_holes() -> list
        returns a list of all holes'''
        return self.holes

    def shoot_shield(self, bullet):
        '''Shield.shoot_shield(bullet) -> None
        checks if bullet has shot shield'''
        # get bullet position
        x,y = bullet.pos()

        # check if inside shield
        if not (self.x - self.width/2 - 3 <= x <= self.x + self.width/2 + 3 and \
                self.y - self.height/2 - 3 <= y <= self.y + self.height/2 + 3):
            return

        # check if inside hole
        for hole in self.holes:
            # get distance from center of hole
            distance = ((hole[0] - x)**2 + (hole[1] - y)**2)**(1/2)
            # check if in hole
            if distance < hole[2]-4:
                return
        
        # draw hole
        radius = bullet.get_radius()
        num = self.master.get_canvas().create_oval(x-radius, -y-radius, x+radius, -y+radius, fill="black")
        self.holes.append((x, y, radius, num))
        bullet.explode()

class Spaceship(turtle.RawTurtle):
    '''represents the alien spaceship'''

    def __init__(self, master):
        '''Spaceship(master) -> Spaceship
        constructs the spaceship'''
        turtle.RawTurtle.__init__(self, master.get_screen())

        # info and data
        self.waitPeriod = random.randint(5,30)
        self.last = time.time()
        self.pu()
        self.shape("spaceship.gif")
        self.height = master.get_screen().window_height()/2 - 25
        self.width = master.get_screen().window_width()/2+100
        self.goto(self.width, self.height)
        self.direction = -1
        self.speed = 3
        self.master = master
        self.isMoving = False

        self.start_movement()

    def start_movement(self):
        '''Spaceship.start_movement() -> None
        starts the movement of the spaceship'''
        if self.master.is_over():
            return

        # move
        if self.isMoving:
            self.fd(self.direction*self.speed)

            # check if out of screen
            if self.xcor() <= -self.width or self.xcor() >= self.width:
                self.stop()
                
        elif time.time() - self.last > self.waitPeriod:
            self.isMoving = True
            self.fd(self.direction)
            self.st()

        self.master.get_screen().update()
        self.master.get_screen().ontimer(self.start_movement, 5)

    def stop(self):
        '''Spaceship.stop() -> None
        stops the spaceship'''
        self.isMoving = False
        self.ht()
        self.direction = random.choice([1,-1])
        self.goto(self.direction*self.width,self.height)
        self.direction = -self.direction
        self.waitPeriod = random.randint(5, 30)
        self.last = time.time()     

class Aliens(turtle.RawTurtle):
    '''all of the aliens'''

    def __init__(self, master, startPos, frameWait, speed, moveWait, numDown=6):
        '''Aliens(master, startPos, frameWait, speed, moveWait, numDown) -> Aliens
        the object for all the aliens'''
        # set up turtle
        turtle.RawTurtle.__init__(self, master.get_screen())
        self.pu()
        self.ht()

        # add aliens
        self.aliens = []
        distance = 55
        for y in range(6):
            self.aliens.extend([((-110,y*distance),1),((-185,y*distance),1),((-35,y*distance),2),
                ((35,y*distance),2),((110,y*distance),3),((185,y*distance),3)])

        self.startPos = startPos
        self.currentPos = startPos
        self.frameWait = frameWait
        self.master = master
        self.moveSpeed = speed
        self.direction = -1
        self.moveWait = moveWait
        self.numDown = numDown
        self.currentDown = 0

        # set up bullets
        self.bullets = [Bullet(master, "red", None) for i in range(2)]
        self.cooldown = 1
        self.last = 0
        
        self.move(startPos)

    def __len__(self):
        '''len(Aliens) -> int
        returns the number of remaining aliens'''
        return len(self.aliens)

    def get_frame(self):
        '''Aliens.get_frame() -> str
        returns the current frame (1 or 2)'''
        return str(int((self.currentPos[0]//self.frameWait) % 2 + 1))

    def get_bullets(self):
        '''Aliens.get_bullets() -> list
        returns a list of all bullets'''
        return self.bullets

    def get_lowest_ycor(self):
        '''Aliens.get_lowest_ycor() -> int
        returns the lowest ycor of the alien'''
        if len(self) == 0:
            return

        lowest = self.aliens[0][0]
        for alien in self.aliens:
            if alien[0][1] < lowest[1]:
                lowest = alien[0]
        return lowest[0] + self.currentPos[0], lowest[1] + self.currentPos[1]

    def update_level(self ,level):
        '''Aliens.update_level(level) -> None
        updates the aliens for level'''
        if self.moveWait > 5:
            self.moveWait -= 1
            self.moveSpeed += 1/15
        if level >= 7:
            self.bullets.append(Bullet(self.master, "red", None, 20))
            self.cooldown -= 0.9
        if 5 < level <= 10:
            self.numDown += 1

    def move(self, x, y=None):
        '''Aliens.move(x, y=None) -> None
        moves aliens to pos'''
        self.clear()

        # position
        if y == None:
            x,y = x
        self.currentPos = x,y
            
        # draw all aliens
        for alien in self.aliens:
            self.goto(alien[0][0]+x, alien[0][1]+y) 
            self.shape("alien_"+str(alien[1])+"_frame_"+self.get_frame()+".gif")
            self.stamp()

    def shoot_alien(self, pos):
        '''Aliens.shoot_alien(x, y) -> bool
        checks if (x,y) shoots an alien. If it does, returns True and the alien is removed.
        Otherwise returns False'''
        isHit = self.is_hit(pos) # get if hit
        # if alien is hit
        if isHit[0]:
            self.aliens.remove(isHit[1])
            # add score for alien
            self.master.add_score(10)

        # return
        if isHit[1] == None:
            return isHit
        else:
            return isHit[0], (isHit[1][0][0]+self.currentPos[0], isHit[1][0][1]+self.currentPos[1]), isHit[1][1]

    def is_hit(self, pos):
        '''Aliens.is_hit(pos) -> bool, obj
        returns (True, alien) if hit. Otherwise returns (False, None)'''
        x,y = pos # unpack

        # loop though aliens
        for alien in self.aliens:            
            # if alien is hit
            if self.currentPos[0]+alien[0][0]-30.5 <= x <= self.currentPos[0]+alien[0][0]+30.5 and\
               self.currentPos[1]+alien[0][1]-24 <= y <= self.currentPos[1]+alien[0][1]+24:
                return True, alien
        return False, None

    def start_movement(self):
        '''Aliens.start_movement() -> None
        starts the aliens moving'''
        # check for next level
        if len(self) == 0:
            self.move(self.currentPos)
            return
        
        # check if game is over
        if self.master.is_over():
            self.move(self.currentPos)
            self.master.end_game()
            return

        width = self.master.get_screen().window_width()/2 # width of half the screen
        if (self.currentPos[0] < -width+230 or self.currentPos[0] > width-230) and self.currentDown >= 0:
            # go for player
            if self.get_lowest_ycor()[1] - self.master.get_player().ycor() <= 20 and len(self) != 0:
                self.direction = -self.direction
                self.move(self.currentPos[0]+self.moveSpeed*self.direction,self.currentPos[1])
                self.currentDown = -1

                # change direction
                if self.master.get_player().xcor() - self.get_lowest_ycor()[0] >= 0:
                    self.direction = 1
                else:
                    self.direction = -1
                    
            # move down
            elif self.currentDown != self.numDown:
                self.move(self.currentPos[0],self.currentPos[1]-5)
                self.currentDown += 1
            # end move down
            else:
                self.direction = -self.direction
                self.move(self.currentPos[0]+self.moveSpeed*self.direction,self.currentPos[1])
                self.currentDown = 0
        else:
            self.move(self.currentPos[0]+self.moveSpeed*self.direction,
                self.currentPos[1])
        # shoot bullet
        if len(self) != 0:
            self.shoot()

        self.master.get_screen().update()
        self.master.screen.ontimer(self.start_movement, self.moveWait)

    def shoot(self):
        '''Aliens.shoot() -> None
        shoots one of the alien bullets'''
        if time.time() - self.last < self.cooldown:
            return

        for bullet in self.bullets:
            if not bullet.is_moving():
                self.last = time.time()
                randomAlien = random.choice(self.aliens)[0]
                bullet.launch((randomAlien[0]+self.currentPos[0],
                    randomAlien[1]+self.currentPos[1]), 270)
                return

    def restart(self, level):
        '''Aliens.restart(level) -> None
        restarts the aliens'''
        self.__init__(self.master, self.startPos, self.frameWait, self.moveSpeed, self.moveWait, self.numDown)
        self.update_level(level)
        self.start_movement()
        
class SpaceInvadersFrame(Frame):
    '''the frame for space invaders'''

    def __init__(self, master, numLives=5):
        '''SpaceInvadersFrame(master, numLives=5) -> SpaceInvadersFrame
        sets up the frame and game data'''
        # enter game
        self.waiting = StringVar(value="waiting")
        self.master = master
        self.name_input()
        master.geometry("1000x700+100+50")
        
        Frame.__init__(self, master)
        self.grid()
        
        # canvas and screen
        self.canvas = Canvas(self, width=1000, height=700)
        self.canvas.grid(row=0, column=0)
        self.screen = turtle.TurtleScreen(self.canvas)
        self.screen.tracer(0)
        self.screen.bgcolor("black")
        self.isOver = False

        # game data
        self.lives = numLives
        self.level = 1
        self.score = 0
        self.highScore = self.get_high_score()
        self.scoreLabel = self.canvas.create_text(0,self.screen.window_height()/2-30,
            text=str(self).format(numLives,1,0, self.highScore),font=("Arial",17),fill="white")
        
        # import all gif shapes using screen.register_shape
        for alienNum in range(1,4):
            for frame in range(1,3):
                self.screen.register_shape("alien_"+str(alienNum)+"_frame_"+str(frame)+".gif")
        self.screen.register_shape("player.gif")
        self.screen.register_shape("spaceship.gif")
        self.screen.register_shape("broken_player.gif")

        # explosion dict
        self.expDic = {}

        # game components
        self.shields = [Shield(self, x, -200, 100, 60, "brown") for x in range(-300,301,300)]
        self.spaceship = Spaceship(self)
        self.aliens = Aliens(self, (105,-20), 10, 1, 10)
        self.aliens.start_movement()
        self.player = Player(self, 3, 1)
        self.screen.update()

        self.game_checkup()

    def __str__(self):
        '''str(SpaceInvadersFrame) -> str
        returns a string with stats'''
        name = self.nameVar.get()

        if name == "":
            return "Lives: {}" + " "*12 + "Level: {}" + " "*12 + "Score: {}"
        return name+" "*12+"Lives: {}" + " "*12 + "Level: {}" + " "*12 + "Score: {}" + " "*12 + "High Score: {}"

    def get_screen(self):
        '''SpaceInvadersFrame.get_screen() -> TurtleScreen
        returns the screen of the game'''
        return self.screen

    def get_canvas(self):
        '''SpaceInvadersFrame.get_canvas() -> Canvas
        returns the current tkinter canvas used for the game'''
        return self.canvas

    def get_aliens(self):
        '''SpaceInvadersFrame.get_aliens() -> Aliens
        returns the aliens'''
        return self.aliens

    def get_player(self):
        '''SpaceInvadersFrame.get_player() -> Player
        returns the player'''
        return self.player

    def get_spaceship(self):
        '''SpaceInvadersFrame.get_spaceship() -> Spaceship
        returns the spaceship'''
        return self.spaceship

    def get_shields(self):
        '''SpaceInvadersFrame.get_shields() -> list
        returns a list of all shields'''
        return self.shields

    def is_over(self):
        '''SpaceInvadersFrame.is_over() -> bool
        returns if the game is over'''
        return self.isOver

    def add_score(self, scoreToAdd=0):
        '''SpaceInvadersFrame.add_score(scoreToAdd) -> None
        adds scoreToAdd to score'''
        # update score and high score
        self.score += scoreToAdd
        if self.score > self.highScore:
            self.highScore = self.score
            
        self.canvas.itemconfigure(self.scoreLabel, text=str(self).format(self.lives, self.level, self.score, self.highScore))

    def game_checkup(self):
        '''SpaceInvadersFrame.game_checkup() -> None
        checks up on the game. Calls itself every 11 milliseconds'''
        if self.isOver:
            return
        
        # check if game is lost
        if self.lives == 0 or self.aliens.is_hit((self.player.xcor(), self.player.ycor()+15))[0]:
            self.end_game()
            return

        # check if hit
        for bullet in self.aliens.get_bullets():
            x,y = bullet.pos()
            # check if bullet has hit player
            if self.player.xcor()-23 <= x <= self.player.xcor()+23 and \
               self.player.ycor()-30 <= y <= self.player.ycor()+20 and bullet.is_moving() and \
               bullet.isvisible():
                self.lives -= 1
                bullet.explode(["red","dark orange","gold"],30)
                self.add_score()

        # next level
        if len(self.aliens) == 0:
            self.new_level()

        self.screen.ontimer(self.game_checkup, 8)

    def end_game(self):
        '''SpaceInvadersFrame.end_game() -> None
        ends the game'''
        # stop everything
        self.isOver = True
        self.player.shape("broken_player.gif")
        self.screen.update()
        self.save_high_score()
        self.lives = 0
        self.add_score()

        # add the final text
        self.canvas.create_text(0,0, text="Game Over!", fill="white", font=("Arial", 100))

    def new_level(self):
        '''SpaceInvadersFrame.new_level() -> None
        starts a new level'''
        self.level += 1
        self.isOver = True
        self.newLevelText = self.canvas.create_text(0,0, text="Level " + str(self.level), font=("Arial", 100), fill="White")
        self.screen.ontimer(self.start_up, 2500)

    def start_up(self):
        '''SpaceInvadersFrame.start_up() -> None
        starts up the game'''
        # move all alien bullets
        for alienBullet in self.aliens.get_bullets():
            alienBullet.goto(0, 500)
        # move player bullets
        for playerBullet in self.player.get_bullets():
            playerBullet.goto(0,-500)
            playerBullet.explode()
        # reset shields
        for shield in self.shields:
            for hole in shield.get_holes():
                self.canvas.delete(hole[3])
            shield.get_holes().clear()
            
        self.isOver = False
        self.spaceship.ht()
        oldSpaceship = self.spaceship
        self.spaceship = Spaceship(self)
        del oldSpaceship
        
        self.aliens.restart(self.level)
        self.player.setx(0)
        self.game_checkup()
        self.add_score()
        self.canvas.delete(self.newLevelText)
        self.screen.update()

    def name_input(self):
        '''name_input() -> str
        returns the player's name'''
        window = Frame(self.master)
        window.grid()
        
        # buttons and text area
        Label(window, text="Enter your name:").grid(row=1, column=0, sticky=W)
        Label(window, text="(Leave blank to play anonymously)", font=("Arial", 7, "italic")).grid(row=0, column=0, sticky=W)
        Button(window, text="Play Game", command=self.enter_game).grid(row=4, column=0)
        self.nameVar = StringVar()
        entryField = Entry(window, textvariable=self.nameVar)
        entryField.grid(row=3, column=0)
        entryField.focus_set() # cursor in entry
        self.clearHigh = IntVar()
        Checkbutton(window, text="Clear high score", variable=self.clearHigh).grid(row=5, column=0, sticky=W)
        Canvas(window, height=5, width=10).grid(row=2, column=0)
        window.bind_all("<Return>", self.enter_game)
        
        self.master.wait_variable(self.waiting)
        window.destroy()

    def enter_game(self, event=''):
        '''SpaceInvadersFrame.enter_game(event='') -> None
        enters the game'''
        if len(self.nameVar.get()) > 15:
            message.showerror(title="Error 3406", message="The name you have entered is too long.")
            return
        
        self.waiting.set("enter")

    def get_high_score(self):
        '''SpaceInvadersFrame.get_high_score() -> int
        returns the total high score'''
        fileName = "space_invaders_"+self.nameVar.get().lower()+".txt"
        
        if self.nameVar.get() == "" or not os.path.isfile(fileName) or self.clearHigh.get() == 1:
            return 0

        # get score from file
        file = open(fileName)
        highScore = int(file.read().split()[-1])
        file.close()
        return highScore
        
    def save_high_score(self):
        '''SpaceInvadersFrame.save_high_score() -> None
        saves the proper file'''
        if self.nameVar.get() == "":
            return

        # save score
        file = open("space_invaders_"+self.nameVar.get().lower()+".txt","w")
        file.write(" "+str(self.highScore))
        file.close()

root = Tk()
root.title("Space Invaders")
root.iconbitmap("hourglass")

SpaceInvadersFrame(root)
mainloop()
quit()
