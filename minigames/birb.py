import pygame
import random

class InteractableObject:
    def __init__(self, xpos, ypos, size, xspeed, yspeed, colour=(255,255,255)):
        # mutable changing verables
        self.x = xpos
        self.y = ypos
        self.xspeed = xspeed
        self.yspeed = yspeed
        self.colour = colour

        # constant tupple
        self.size = size

    def colide(self, xy, size):

        if self.x - size[0] <= xy[0] and self.x  + self.size[0] >= xy[0]:
                # within the x range
                #print('x')
                if xy[1] + size[1] >= self.y and xy[1] <= self.y + self.size[1]:
                    #print('y')
                    #within the y range
                    return True
                return False
        return False



class game:

    def __init__(self,xmax,ymax):

        self.xmax = xmax
        self.ymax = ymax

        self._runing = True
        self.screen = None
        self.keyinput = None

        self.btop = [InteractableObject(int(self.xmax /2), 0, (int(self.xmax / 10), random.randint(20, int (self.xmax + (self.xmax/-6 - 10)))), -1, 0), InteractableObject(self.xmax, 0, (int(self.xmax / 10), random.randint(20, int (self.xmax + (self.xmax/-6 - 10)))), -1, 0)]
        self.bbot = [InteractableObject(int(self.xmax /2), self.btop[0].size[1] + (self.xmax/6), (int(self.xmax / 10), self.ymax), -1, 0), InteractableObject(self.xmax, self.btop[1].size[1] + (self.xmax/6), (int(self.xmax / 10), self.ymax), -1, 0)]

        self.player = InteractableObject(int(self.xmax / 10), int(self.xmax / 2), (int(self.xmax / 20), int(self.xmax / 20)), 0, 0, (0, 25, 120))

        self.points = 0


    def on_init(self):
        pygame.init()

        self.screen = pygame.display.set_mode((self.xmax, self.ymax))
        self._runing = True
        self.clock = pygame.time.Clock()

    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                self._runing = False

    def get_vals(self):
        return [self.player.y, self.btop[0].x, self.btop[0].y, self.bbot[0].y, self.btop[1].x, self.btop[1].y, self.bbot[1].y]

    def get_points(self):
        return self.points


    def colisions(self, *objects):
        # death
        if objects[0].y > self.ymax or objects[0].y < 0:
            self._runing = False
            self.points -= 2
            return False
            #print('out',self.points)

        if self._runing:
            for i in range(len(objects)):
                for j in range(len(objects)):
                    if objects[i].colide((objects[j].x, objects[j].y), objects[j].size) and i != j:
                        self._runing = False
                        self.points -= 0.5
                        return False

        if self.player.x == self.btop[0].x or self.player.x == self.btop[1].x:
            self.points += 1

        if self.player.x == self.btop[0].x + self.btop[0].size[0] or self.player.x == self.btop[1].x + self.btop[1].size[0]:
            self.points += 1

        #for i in range(2):
            #if self.btop[i].colide((self.player.x, self.player.y), self.player.size):
                #print('t')
                #self._runing = False
            #if self.bbot[i].colide((self.player.x, self.player.y), self.player.size):
                #print('b')
                #self._runing = False

        return True

    def movement(self, press, *objects):

        #, App.player, App.btop[0], App.btop[1], App.bbot[0], App.bbot[1]

        # gets the user input and sets the player aceleration
        if press:
            objects[0].yspeed = -3.5
        else:
            objects[0].yspeed += 0.1

        for object in objects:
            object.y += object.yspeed
            object.x += object.xspeed

            if object.x <= -object.size[0]:
                object.x = self.xmax

                if object.y == 0:
                    object.size = (int(self.xmax / 10), random.randint(20, int (self.xmax + (self.xmax/-6 - 10))))
                else:
                    if self.btop[0].x == self.xmax:
                        object.y = self.btop[0].size[1] + (self.xmax/6)
                    elif self.btop[1].x == self.xmax:
                        object.y = self.btop[1].size[1] + (self.xmax/6)


            if object.x >= self.xmax + object.size[0]:
                object.x = 0

                if object.y == 0:
                    object.size = (int(self.xmax / 10), random.randint(20, int (self.xmax + (self.xmax/-6 - 10))))
                else:
                    if self.btop[0].x == 0:
                        object.y = self.btop[0].size[1] + (self.xmax/6)
                    elif self.btop[1].x == 0:
                        object.y = self.btop[1].size[1] + (self.xmax/6)


            #if object.y <= -object.size[1]:
                #object.y = self.ymax

            #if object.y >= self.ymax + object.size[1]:
                #object.y = 0



    def render_game(self,fps, *objects):
        self.screen.fill((0,0,0))

        for object in objects:
            pygame.draw.rect(self.screen, object.colour, pygame.Rect(int(object.x), int(object.y), int(object.size[0]), int(object.size[1])))

        self.clock.tick(fps)
        pygame.display.flip()


if __name__ == "__main__" :
    App = game(800,800)
    App.on_init()

    while App._runing == True:

        App.movement(pygame.key.get_pressed()[pygame.K_SPACE], App.player, App.btop[0], App.btop[1], App.bbot[0], App.bbot[1])
        App.colisions(App.player, App.btop[0], App.btop[1], App.bbot[0], App.bbot[1])
        App.event()
        App.render_game(30, App.player, App.btop[0], App.btop[1], App.bbot[0], App.bbot[1])

    pygame.quit()

    print(App.points)
