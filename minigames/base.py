import pygame
import random
import pygame_menu
import requests

def getTask(gameid, location, tag, auth=''):
    return 6969

def submitTask(gameid, taskid,  auth=''):
    return True

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

        self.id = 0


    def on_init(self):
        pygame.init()

        self.screen = pygame.display.set_mode((self.xmax, self.ymax))
        self._runing = True
        self.clock = pygame.time.Clock()

    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                self._runing = False

    def renderMenu(self):
        menu = pygame_menu.Menu(300, 400, 'MurderUs',
                               theme=pygame_menu.themes.THEME_BLUE)

        menu.add_text_input('Enter Tag:', default='0000', onreturn=self.Start)
        menu.mainloop(self.screen)


    def Start(self, tag):
        x = 0
        self.id = getTask('gameid', 'location', tag)

        while self.id != 0:
            self.event()
            self.screen.fill((0,0,0))



            if x > 100:
                if submitTask('gameid', self.id):
                    self.id = 0
                    print('completed task')
                else:
                    print('fail')
            self.clock.tick(30)
            pygame.display.flip()

            x += 1



if __name__ == "__main__" :
    App = game(800,800)
    App.on_init()
    App.renderMenu()
    pygame.quit()
