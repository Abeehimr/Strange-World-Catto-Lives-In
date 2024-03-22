from random import randint,choice
import pygame
from csv import reader,writer
from os import listdir
from os.path import isfile, join
from tkinter.messagebox import showerror
# pygame setup
pygame.init()

#set caption
pygame.display.set_caption("strange world catto lives in")
#colors
GREYISH_BLUE = (42,47,68)

WIDTH = 1024
HEIGHT = 576
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

FPS = 60
PLAYER_VEL = 5
GRAVITY = 1
DIFF = 399
BLOCK_SIZE = 96
BUTTON_SIZE = {
    1:(0,0,75,12 , 0,13,75,12),
    2:(0,26,13,12 , 0,39,13,12),
    3:(14,26,26,25 , 41,26,26,25),
}
UNLOCK_AT = [[0,250],[100,500]]

#background
def get_background(name):
    """take image and return list of positions to place it"""
    image = pygame.image.load(join("thingis","Background",name)).convert_alpha()
    _,_,width , height = image.get_rect()
    tiles = []

    for i in range(WIDTH//width + 1):
        for j in range(HEIGHT//height + 1):
            tiles.append((i*width , j*height))
    return tiles , image


def flip(sprites: list) -> list:
    return [pygame.transform.flip(sprite,True,False) for sprite in sprites] #bool: flip in x direction bool: flip in y direction

def load_sp_sheets(dir1:str,dir2:str , width:int, height:int , direction=False ) -> dict: 
        # load all files
        path = join("thingis",dir1,dir2)
        images = [f for f in listdir(path) if isfile(join(path,f))]

        # key => animation style value=> all the images in that animation
        all_sps = {}

        for image in images:
            sp_sheet = pygame.image.load(join(path,image)).convert_alpha()

            sps = []
            for i in range(sp_sheet.get_width()//width): # width of individual image
                surface = pygame.Surface((width,height),pygame.SRCALPHA,32) # create surface the size of character
                rect = pygame.Rect(i*width,0,width,height) 
                surface.blit(sp_sheet,(0,0),rect) #draw sp sheet in top_left corner
                sps.append(surface)

            if direction:
                all_sps[image.replace(".png","")+"_right"] = sps
                all_sps[image.replace(".png","")+"_left"] = flip(sps)
            else:
                all_sps[image.replace(".png","")] = sps

        return all_sps

                            # x,y of position in image

def get(path: list[str] ,x: int ,y: int, width: int, height: int , fw=0 , fh=0):
    p = join(*path)
    image = pygame.image.load(p).convert_alpha()
    surface = pygame.Surface((width,height),pygame.SRCALPHA ,32)  #created surface of that size
    surface.blit(image,(0,0),pygame.Rect(x,y,width,height)) # top left coordinate of image in png (x,y in this case)
    if fw == 0 and fh == 0: return surface
    else: return pygame.transform.scale(surface , (fw,fh))

try:
    #fonts
    TITLE = pygame.font.Font(join("thingis","font","cartooni.ttf"),40)
    FONT = pygame.font.Font(join("thingis","font","cartooni.ttf"),30)
    FONT_S = pygame.font.Font(join("thingis","font","cartooni.ttf"),25)
    background , bg_image = get_background("Gray.png")
    # load all characters
    SKINS = {
    "ORANGE":load_sp_sheets("players","orange",96,96,True,False),
    "CALICO":load_sp_sheets("players","calico",96,96,True,False),
    "BLUE" :load_sp_sheets("players","blue",96,96,True,False),
    "NIGGA" : load_sp_sheets("players","nigga",96,96,True,False),
    "KITLER" :load_sp_sheets("players","kitler",96,96,True,False),
    "RETARD" : load_sp_sheets("players","retard",96,96,True,False),
    }

    GATTOS = [get(["thingis","obsticles","cars.png"],96*i,0,96,96, 64,64) for i in range(10)]

    CLOODS = [get(["thingis","obsticles","clouds.png"],0,i*96,168,96) for i in range(4)]
    CLOODS += flip(CLOODS)

    BUTTONS = { j:[get(["thingis","menu","menu.png"],*BUTTON_SIZE[j][0+i:4+i]) for i in [0,4]] for j in range(1,4)}

    QUESTIONS = [get(["thingis","menu","question.png"] , i , 0 , 72 , 72) for i in [0,72]]

    ZAMEEN = get(["thingis","zameen","zameen.png"],0,0,48,48 , BLOCK_SIZE,BLOCK_SIZE)
except Exception as e:
    showerror("ERROR: files missing",e)

class Data():
    def __init__(self) -> None:
        self.look = []
        self.data = {}

    def add(self,lis):
        if lis[0] not in self: self.look.append(lis[0])
        self.data[lis[0]] = [lis[0], int(lis[1]) , lis[2]]

    def __contains__(self,k):
        return k in self.data

    def sort(self):
        self.look.sort(key=lambda x: self.data[x][1],reverse=True)

    def retn(self,k):
        return self.data[k]
    
    def give(self,start,end):
        end = min(end,len(self))
        for i in range(start,end):
            yield (i , self.data[self.look[i]][0] , self.data[self.look[i]][1])

    def __iter__(self):
        yield from self.data.values()

    def __len__(self):
        return len(self.look)

class Gamer():
    def __init__(self,name: str,max_score = 0 ,skin = "ORANGE") -> None:
        self.name = name
        self.max_score = max_score
        self.skin = skin

        if name == "ABEEHIMR" or name == bytes.fromhex("5048415045").decode('utf-8'):
            self.lives = 10
            self.special = True
        else:
            self.lives = 5
            self.special = False
        self.unlock_all = name == "ABEEHIMR"
        #game vars
        self.curr_lives = self.lives
        self.curr_score = 0
        self.diff = DIFF
        self.cloods = 2
    def close(self) -> dict:
        return [self.name, self.max_score, self.skin]

class linkedmenu():
    def __init__(self , lis: list[str] ,x = None, back=False , skin = False) -> None:
        fac = 150 if skin else 60
        typ = 3 if skin else 1
        size = 5 if skin else 4
        self.index = 1 if back else 0
        if typ == 1:
            x = (WIDTH - size*BUTTON_SIZE[typ][2])//2
        self.y = (HEIGHT - fac*len(lis))//2
        if skin: self.y += 30
        self.arr = [Button(x , self.y + i*fac, typ, size, st) for i , st in enumerate(lis)]
        if back: self.arr = [Button(x,self.y-60,2,4,"main")]+self.arr
        self[self.index].select()

    def activate_next(self) -> None:
        self[self.index].unselect()
        self.index = 0 if self.index == len(self.arr)-1 else self.index + 1
        self[self.index].select()

    def activate_prev(self) -> None:
        self[self.index].unselect()
        self.index = len(self.arr) -1 if self.index == 0 else self.index - 1
        self[self.index].select()

    def selected(self):
        return self[self.index].text
    
    def __len__(self):
        return len(self.arr)
    
    def __getitem__(self,i):
        return self.arr[i]

    def __iter__(self):
        yield from self.arr

# sprite help do pixel perfect collision
class Player(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,skin):
        super().__init__()
        self.SPRITES = SKINS[skin]
        self.ANIMATION_DELAY = 5 if skin == "RETARD" else 9 #how slow or fast sp_sheet changes
        #rect => tuple that store x,y,w,h
        self.rect = pygame.Rect(x,y,width,height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left" #which way the player is facing so that we use appropriate image
        self.animation_count = 0 #count the animation frames
        self.fall_count = 0 #how long have we been falling
        self.jumped = False
        self.hit = False
        self.hit_count = 0

        self.sp_sheet = "idle"
        self.walk_delay = 0

    def jump(self):
        self.y_vel = -GRAVITY*6 # negative for jump UP ; 8 is speed of jump
        self.jumped = True
        self.animation_count = 0
        self.fall_count = 0 #reset the gravity count

            
    def move(self,dx,dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def move_left(self,vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
        self.walk_delay = 0

    def move_right(self,vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
        self.walk_delay = 0

    def loop(self):
        self.y_vel += min(1,(self.fall_count/FPS)*GRAVITY) # /fps so when fall_count == 60 means we fell for 1 sec then *gravity => velocity 
        self.move(self.x_vel,self.y_vel)
        
        if self.hit:
            self.hit_count += 1
        if self.hit_count > FPS*0.5: #0.5 sec
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jumped = False

    def update_sprite(self):
        if self.hit:
            self.sp_sheet = "dead"
        elif self.y_vel < 0:
            self.sp_sheet = "jump"
        elif self.y_vel > GRAVITY*2: # the gravity is always there so y_vel is never 0
            self.sp_sheet = "jump"
        elif self.x_vel != 0:
            self.sp_sheet = "walk"
        elif self.walk_delay > 1:
            self.sp_sheet = "idle"

        sp_sheet_name = self.sp_sheet + "_" + self.direction
        sprites = self.SPRITES[sp_sheet_name]
        sprite_index = (self.animation_count//self.ANIMATION_DELAY) %len(sprites)
        self.sprite = sprites[sprite_index]
        #animation + walk delay
        self.animation_count += 1
        self.walk_delay += 1
        if self.walk_delay > self.ANIMATION_DELAY: self.walk_delay = 0
        self.update()

    def update(self): # update hitbox according to the current sprite
        self.rect = self.sprite.get_rect(topleft= (self.rect.x , self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self,screen): 
        screen.blit(self.sprite,(self.rect.x, self.rect.y)) #x , y postion on screen

class Object(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.width = width
        self.height = height

    def draw(self,screen):
        screen.blit(self.image,(self.rect.x,self.rect.y))

    def loop(self):
        self.rect = self.image.get_rect(topleft= (self.rect.x , self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

class Car(Object):
    def __init__(self, x, y , px):
        super().__init__(x, y, 64, 64)
        self.x_vel = (px - x)//49
        self.y_vel = 0
        self.image = choice(GATTOS)
        self.mask = pygame.mask.from_surface(self.image)
        self.fall_count = 0

    def move(self):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel

    def loop(self,player:Player):
        self.y_vel += min(1,(self.fall_count/FPS)*GRAVITY)
        self.move()
        self.fall_count += 1
        if pygame.sprite.collide_mask(player,self):
            player.make_hit()
            self.kill()
            return 2
        elif self.rect.bottom >= HEIGHT - 72:
            self.kill()
            return 1
        else:
            return 0

class Runner(Object):
    def __init__(self):
        self.SPEED = randint(10,15)
        self.direction = choice([-1,1]) # -1 = go left 1 = go right
        x = -64 if self.direction == 1 else WIDTH
        super().__init__(x=x, y=HEIGHT-96-64, width=64,height=64)

        i = randint(0,10)
        self.image = choice(GATTOS)
        self.mask = pygame.mask.from_surface(self.image)

    def loop(self):
        self.rect.x += self.SPEED*self.direction #move
        if self.rect.x <= -64 or self.rect.x >= WIDTH:
            return True
        else:
            return False
        
class Cloud(Object):
    def __init__(self):
        self.SPEED = randint(1,2)
        self.direction = choice([-1,1]) # -1 = go left 1 = go right
        x = -168 if self.direction == 1 else WIDTH
        y = choice([24,32,48,64,72])

        super().__init__(x,y,168,96)
        self.image = choice(CLOODS)
        self.mask = pygame.mask.from_surface(self.image)

    def loop(self,cloods):
        self.rect.x += self.SPEED*self.direction #move
        if self.rect.x <= -168 or self.rect.x >= WIDTH:
            self.kill()
            cloods.add(Cloud())
            return False
        else:
            return True
            
class Button(Object):
    def __init__(self,x, y,button ,factor,text_skin):
        self.text = text_skin
        self.factor = factor
        self.button = button
        self.rect = pygame.Rect(x,y, factor*BUTTON_SIZE[button][2] , factor*BUTTON_SIZE[button][3] )
        self.selected = 0
        super().__init__(*self.rect)
        self.block = self.get_block() #text wala part
        self.image = self.block[self.selected]
        self.mask = pygame.mask.from_surface(self.image)

    def select(self):
        self.selected = 1

    def unselect(self):
        self.selected = 0

    def loop(self,screen):
        self.image = self.block[self.selected]
        super().loop()
        self.draw(screen)

    def get_block(self):
        surface_selected,surface_unselected = (pygame.transform.scale_by(s,self.factor) for s in BUTTONS[self.button])
        
        if self.button == 1:
            text_gene(surface_selected, self.text , (self.width/2,4),-0.5,0,FONT,(255,)*3)
            text_gene(surface_unselected, self.text , (self.width/2,4),-0.5,0,FONT,(215,)*3)

        elif self.button == 3: 
            if self.text == "KITLER" or self.text == "RETARD":
                emote_s = SKINS[self.text]["dead_right"][-1]
                emote_u = SKINS[self.text]["idle_right"][0]
            elif self.text == "Q":
                emote_s = QUESTIONS[1]
                emote_u = QUESTIONS[0]
            else:
                emote_s = SKINS[self.text]["idle_right"][0]
                emote_u = SKINS[self.text]["walk_right"][0]

            x_for_center =(self.width - emote_s.get_width())//2
            y_for_center = (self.height - emote_s.get_height())//2 - 4
            surface_selected.blit(emote_s,(x_for_center,y_for_center))
            surface_unselected.blit(emote_u,(x_for_center,y_for_center))
                
        return [surface_unselected,surface_selected]

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        self.image = ZAMEEN
        self.mask = pygame.mask.from_surface(self.image)

def text_gene(screen ,text:str ,pos:tuple[int] ,width_fac=0,height_fac=0,font=FONT,color=GREYISH_BLUE):
    sur = font.render(text,True,color)
    pos = (int(pos[0]+width_fac*sur.get_width()), int(pos[1]+height_fac*sur.get_height()))
    screen.blit(sur,pos)
    
def draw_background():
    for tile in background:
        SCREEN.blit(bg_image , tile)

def collide(player , dx):
    player.move(dx, 0) #move the player phle hi just to check if he moves will it collide
    player.update()
    flag = False
    if player.rect.right > WIDTH or player.rect.x < 0:
        flag = True
    player.move(-dx,0)
    player.update()
    return flag

def handl_mov(player,objects):    
    collide_left = collide(player, -PLAYER_VEL*2)
    collide_right = collide(player, PLAYER_VEL*2)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and not collide_left: #check if left key is pressed and we didnt collide if we move
        player.move_left(PLAYER_VEL)
    elif keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)
    else:
        player.x_vel = 0 # stop player when key is not pressed
    #handl_vertical_collision(player , objects)
    for o in objects:
        if pygame.sprite.collide_mask(player,o):
            player.rect.bottom = o.rect.top #put player's bottom above the object it collided with
            player.landed()
            break
    
def update_gamer(gamer:Gamer,reset=True):
    gamer.max_score = max(gamer.max_score , gamer.curr_score)
    if reset: gamer.curr_score = 0
    gamer.curr_lives = gamer.lives
    gamer.diff = DIFF
    gamer.cloods = 2

def incr_score(gamer:Gamer , cloods:set[Cloud] , runner: list):
    gamer.curr_score += 1
    gamer.diff = max(10, gamer.diff - 1)
    if len(cloods) < 20 and 0 == gamer.curr_score % 25 and randint(0,1):
        cloods.add(Cloud())
        gamer.diff += 20
    if not runner and gamer.curr_score%5 == 0 and randint(0,1):
        runner.append(Runner())


def menu(clock , lis , gamer:Gamer,skin=False,current_s=False,lives=False,game_over=False):
    emo = linkedmenu(lis)
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit?"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return emo.selected()
                if event.key == pygame.K_UP:
                    emo.activate_prev()
                if event.key == pygame.K_DOWN:
                    emo.activate_next()
        
        draw_background()
        for b in emo: b.loop(SCREEN)
        if game_over:
            text_gene(SCREEN,"GAME OVER",(WIDTH/2,emo.y),-0.5,-3,TITLE)
            text_gene(SCREEN,f"you scored {gamer.curr_score}",(WIDTH/2,emo.y),-0.5,-2)
        if skin:
            text_gene(SCREEN,f"skin: {gamer.skin}",(4,4))
        if lives:
            text_gene(SCREEN,f"lives: {gamer.curr_lives}",(4,4))
        if current_s:
            t = f"current score: {gamer.curr_score}"
        else: 
            t = f"your max score: {gamer.max_score}"
        text_gene(SCREEN,t,(WIDTH-4,4),-1)

        pygame.display.update()
    
def login(clock):
    name = ""    
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit?"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if len(name)>0:
                        return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 26:
                    name += event.unicode.upper()
                
        draw_background()
        #title
        text_gene(SCREEN,"STRANGE WORLD CATTO LIVES IN", (WIDTH/2 , HEIGHT//2 -100),-0.5,-1,TITLE)
        # enter name
        text_gene(SCREEN,"enter your name", (WIDTH/2 , HEIGHT//2) , -0.5)
        # show name 
        text_gene(SCREEN,f">> {name} <<" , (WIDTH/2 , HEIGHT//2 + 100) , -0.5)
        pygame.display.update()

def scoreboard(clock,data:Data,gamer:Gamer):
    data.sort()
    start = 0
    end = 5
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit?"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "main"
                elif event.key == pygame.K_UP and start != 0:
                    start -= 1
                    end -= 1
                elif event.key == pygame.K_DOWN and end < len(data):
                    start += 1
                    end += 1   
                
        draw_background()
        #go back thing
        SCREEN.blit(pygame.transform.scale_by(BUTTONS[2][0],4),(4,4))
        #score
        text_gene(SCREEN,f"your score: {gamer.max_score}",(WIDTH-4,4),-1)
        # title
        text_gene(SCREEN,"rank",(10, 100))
        text_gene(SCREEN,"name",(WIDTH/2, 100),-0.5)
        text_gene(SCREEN,"score",(WIDTH -10, 100),-1)
        # enter names
        for i,name,score in data.give(start,end):
            text_gene(SCREEN,f"{i+1:4}",(10, 150 + 50*(i-start)))
            text_gene(SCREEN,name,(WIDTH/2, 150 + 50*(i-start)),-0.5)
            text_gene(SCREEN,f"{score:5}",(WIDTH -10, 150 + 50*(i-start)),-1)
        pygame.display.update()

def ski(clock , gamer:Gamer):
    # menu calculations
    y2 = (WIDTH + 25)//2
    y1 = (WIDTH - 25)//2 - 130 #130 is 26*5
    col1 = ["ORANGE","Q"]
    col2 = ["Q","Q"]
    if gamer.max_score >= UNLOCK_AT[1][0] or gamer.unlock_all:
        col2[0] = "CALICO"
    if gamer.max_score >= UNLOCK_AT[0][1] or gamer.unlock_all:
        col1[1] = "BLUE"
    if gamer.max_score >= UNLOCK_AT[1][1] or gamer.unlock_all or gamer.name == "CHITTA":
        col2[1] = "NIGGA"
    if gamer.special:
        col1.append("KITLER")
        col2.append("RETARD")
        
    menu1 = linkedmenu(col1,y1,True,True)
    menu2 = linkedmenu(col2,y2 ,False,True)
    menu2[menu2.index].unselect() # undo the default selection in menu2

    active = menu1
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit?"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if active.selected() == "Q": continue
                    return active.selected()
                if event.key == pygame.K_UP:
                    active.activate_prev()
                if event.key == pygame.K_DOWN:
                    active.activate_next()
                # change line
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    i = active.index
                    if i == 0 and active == menu1: continue
                    #switch
                    active[i].unselect()
                    if active == menu1:
                        menu2.index = 0 if i == len(menu1) -1 else i
                        menu2.activate_prev()
                        active = menu2
                    elif active == menu2:
                        active[i].unselect()
                        menu1.index = i
                        menu1.activate_next()
                        active = menu1


        #draw
        draw_background()
        for b in menu1: b.loop(SCREEN)
        for b in menu2: b.loop(SCREEN)
        #display text

        #loop in menu1
        for i,b in enumerate(menu1):
            #back button
            if i == 0: continue
            (x , y) = b.rect.midleft
            if b.text == "Q": # display unlock when
                text_gene(SCREEN,f"unlock at {UNLOCK_AT[0][i-1]}",(x-25 , y), -1 , -0.5,FONT_S)
            else: # display name
                text_gene(SCREEN,b.text,(x-25 , y), -1 , -0.5,FONT_S)
        #loop in menu1
        for i,b in enumerate(menu2):
            (x , y) = b.rect.midright
            if b.text == "Q":
                text_gene(SCREEN,f"unlock at {UNLOCK_AT[1][i]}",(x+25 , y), 0 , -0.5,FONT_S)
            else:
                text_gene(SCREEN,b.text,(x+25 , y), 0 , -0.5,FONT_S)

        text_gene(SCREEN,f"skin: {gamer.skin}",(4,4))
        text_gene(SCREEN,f"your max score: {gamer.max_score}",(WIDTH-4,4),-1)
        pygame.display.update()

def main(clock , gamer:Gamer):
    player = Player(WIDTH//2,HEIGHT//2,96,96,gamer.skin)
    # make flooor
    objects = pygame.sprite.Group(Block(i,HEIGHT-BLOCK_SIZE,BLOCK_SIZE) for i in range(0,WIDTH,BLOCK_SIZE))
    #obsticles
    runner = []
    cloods = pygame.sprite.Group(Cloud() for _ in range(gamer.cloods))
    car = pygame.sprite.Group()

    running = True
    while running:
        clock.tick(FPS)
        # player die
        if gamer.curr_lives == 0:
            update_gamer(gamer,False)
            return "game over"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                update_gamer(gamer)
                return "exit?"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    gamer.cloods = len(cloods)
                    return "resume"
                if event.key == pygame.K_SPACE and not player.jumped:
                    player.jump()

        #lop and update
        player.loop()

        for c in cloods:
            if c.loop(cloods) and randint(0,gamer.diff) == 0:
                car.add(Car(c.rect.x, 72 ,player.rect.x))
            
        
        for c in car:
            match c.loop(player):
                case 2: # car when hit player
                    gamer.curr_lives -= 1
                case 1: # car when hit ground
                    incr_score(gamer,cloods,runner) 

        #kill runner if it reach other end
        if runner and runner[0].loop():
            runner.pop()
            incr_score(gamer,cloods,runner)
        # if runner collides
        if runner and pygame.sprite.collide_mask(player,runner[0]):
            player.make_hit()
            gamer.curr_lives -= 1
            runner.pop()

        handl_mov(player,objects)
        #draw
        draw_background()

        objects.draw(SCREEN)
        car.draw(SCREEN)
        if runner: runner[0].draw(SCREEN)
        cloods.draw(SCREEN)

        #show score
        text_gene(SCREEN,f"score: {gamer.curr_score}",(WIDTH-4,4),-1)
        #show live
        text_gene(SCREEN,f"lives: {gamer.curr_lives}",(4,4))

        if gamer.unlock_all:
            #show diff
            text_gene(SCREEN,f"diff: {gamer.diff}",(WIDTH-4,HEIGHT-4),-1,-1)
            #show c
            text_gene(SCREEN,f"cloods: {len(cloods)}",(4,HEIGHT-4),0,-1)

        player.draw(SCREEN)
        pygame.display.update()

def mainloop():
    clock = pygame.time.Clock()
    p = "thingis/files/saved.csv"
    data = Data()
    if isfile(p): #if saved file exists
        with open(p,"r") as saved:
            for l in reader(saved):
                data.add([bytes.fromhex(code).decode() for code in l])
    gamer = None
    #loopas
    current = "login"
    while current != "exit?":
        match current:

            case "login":
                name = login(clock)
                if name == 'exit?': break
                else:
                    if name in data:
                        gamer = Gamer(*data.retn(name))
                    else:
                        gamer = Gamer(name)
                current = "main"

            case "main":
                current = menu(clock,["new game","skins","scoreboard","log out"],gamer,True)
                if current == "log out":
                    # save gamer info...
                    if gamer.max_score != 0:
                        data.add(gamer.close())
                    current = "login"

            case "skins":
                temp = ski(clock,gamer)
                if temp == 'exit?': break
                if temp != "main":
                    gamer.skin = temp
                current = "main"

            case "scoreboard":
                if gamer.max_score != 0:
                    data.add(gamer.close())
                current = scoreboard(clock,data,gamer)

            case "new game":
                current = main(clock,gamer)

            case "game over":
                temp = menu(clock,["restart","main menu"],gamer,False,False,False,True)
                gamer.curr_score = 0
                if temp == 'exit?': break
                if temp == "restart": current = "new game"
                if temp == "main menu":
                    current = "main"

            case "resume":
                temp = menu(clock,["resume","main menu"],gamer,False,True,True)
                if temp == 'exit?':
                    update_gamer(gamer)
                    break
                if temp == "resume": current = "new game"
                if temp == "main menu":
                    update_gamer(gamer)
                    current = "main"

    #save gamer info
    if gamer and gamer.max_score > 0: data.add(gamer.close())
    with open(p,"w",newline="") as saved:
        s = writer(saved)
        for l in data:
            s.writerow(str(t).encode('utf-8').hex() for t in l)
    # exit
    pygame.quit()
    try: quit()
    except NameError: pass

if __name__ == "__main__":
    mainloop()