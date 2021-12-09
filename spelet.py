import pygame
import pickle
from os import path
from pygame import mixer

# startar pygame och skriver in storleken på skärmen
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()
clock = pygame.time.Clock()
fps = 60

screen_bredd = 650
screen_hojd = 650

screen = pygame.display.set_mode((screen_bredd, screen_hojd))
# bakrunds biden
bakrund = pygame.image.load("bakround.jpg")

# namnet och logan på spelet
pygame.display.set_caption("𝕄𝕠𝕠𝕟 𝕤𝕝𝕒𝕪𝕖𝕣")
logo = pygame.image.load("moon.png")
restart_bild = pygame.image.load("restart_knapp.svg")
start_bild = pygame.image.load("Start_knapp.svg")
save_bild = pygame.image.load("Save_knapp.svg")
quit_bild = pygame.image.load("Quit_knapp.svg")
pygame.display.set_icon(logo)

# definerar vad font är
font_coins = pygame.font.SysFont("Bauhaus 94", 30)
font_game = pygame.font.SysFont("Bauhaus 94", 70)

# spel variablar neråt

# rutornas storlek
tile_size = 50

# game over funktion
game_over = 0

# så att man startar i huvudmenyn
huvud_meny = True

# vilken level man startar på
level = 1

# antal levlar
max_levels = 3

# antal coins/score
coins = 0
level_coins = 0
score_coins = 0

# definerar färger
white = (255, 255, 255)
blue = (0, 0, 255)
# ljud effekter laddas,spelas, sänker volym
pygame.mixer.music.load("bakrund.wav")
pygame.mixer.music.play(-1, 0.0, 5000)
pygame.mixer.music.set_volume(0.1)
coin_ljud = pygame.mixer.Sound("gamecoin.wav")
coin_ljud.set_volume(0.5)
hopp_ljud = pygame.mixer.Sound("gamejump.wav")
hopp_ljud.set_volume(0.5)
gameover_ljud = pygame.mixer.Sound("gameover.wav")
gameover_ljud.set_volume(0.5)
nextlevel_ljud = pygame.mixer.Sound("nextlevel.wav")
nextlevel_ljud.set_volume(0.5)


# ritar rutor i skärmen och i range så skriver man ut skärm storleken/tile_size (kan användas kan hjälpa ibland)
def draw_grid():
    for line in range(0, 13):
        pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_bredd, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_hojd))


# ritar text på skärmen
def draw_text(text, font, text_col, x, y):
    bild = font.render(text, True, text_col)
    screen.blit(bild, (x, y))


# funktionen för att reseta leveln
def reset_level(level):
    player.reset(100, screen_hojd - 200)
    alien_grupp.empty()
    lava_grupp.empty()
    lavahalf_grupp.empty()
    exit_grupp.empty()
    coin_grupp.empty()
    platform_grupp.empty()

    # laddar in världsdatan och skapar världen
    if path.exists(f"leveldata_{level}"):
        with open(f"leveldata_{level}", "rb") as pickle_file:
            world_data = pickle.load(pickle_file)
    world = World(world_data)
    return world


# klassen knapp som gör så att knappar fungerar
class Knapp:
    def __init__(self, x, y, bild):
        self.bild = bild
        self.rect = self.bild.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.klickat = False

    def draw(self):

        aktion = False

        # får musens position
        mposition = pygame.mouse.get_pos()

        # kollar ifall musen är över och ifall man klickar
        if self.rect.collidepoint(mposition):
            if pygame.mouse.get_pressed()[0] == 1 and self.klickat is False:
                aktion = True
                self.klickat = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.klickat = False

        # ska rita fram knappen
        screen.blit(self.bild, self.rect)

        return aktion


# spelargubbens klass, laddar fram bilden på han och sedan gör om storleken
class Player:
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        # variablar
        x_change = 0
        y_change = 0
        walk_cooldown = 5
        # hur långt det kan gå (en tröskel)
        col_troskel = 20
        if game_over == 0:
            # knapptryckningar
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped is False and self.in_air is False:
                self.velocity_y = -12
                self.jumped = True
                hopp_ljud.play()
            if key[pygame.K_SPACE] is False:
                self.jumped = False
            if key[pygame.K_LEFT] and key:
                x_change -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                x_change += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] is False and key[pygame.K_RIGHT] is False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.bilder_r[self.index]
                if self.direction == -1:
                    self.image = self.bilder_v[self.index]

            # själva animering,gör så den sker,counter +med 1 när den når walk_cooldown reset,får animeringen långsammre
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.bilder_r):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.bilder_r[self.index]
                if self.direction == -1:
                    self.image = self.bilder_v[self.index]

            # gravitation och hur högt man kan hoppa
            self.velocity_y += 0.5
            if self.velocity_y > 10:
                self.velocity_y = 10
            y_change += self.velocity_y

            # letar efter kollision
            self.in_air = True
            for tile in world.tile_list:
                # kollar eftter kollision i x kordinater
                if tile[1].colliderect(self.rect.x + x_change, self.rect.y, self.width, self.height):
                    x_change = 0
                # kollar ifall kollison i Y kordinater
                if tile[1].colliderect(self.rect.x, self.rect.y + y_change, self.width, self.height):
                    # kollar ifall man är under ett "block" när man hoppar
                    if self.velocity_y < 0:
                        y_change = tile[1].bottom - self.rect.top
                        self.velocity_y = 0
                    # kollar ifall man är över ett "block" när man faller
                    elif self.velocity_y >= 0:
                        y_change = tile[1].top - self.rect.bottom
                        self.in_air = False

            # kollision mellan fiender, false gör så att fienderna in raderas
            if pygame.sprite.spritecollide(self, alien_grupp, False):
                game_over = -1
                gameover_ljud.play()
            # kollsion lava
            if pygame.sprite.spritecollide(self, lavahalf_grupp, False):
                game_over = -1
                gameover_ljud.play()
            # kollision med lava
            if pygame.sprite.spritecollide(self, lava_grupp, False):
                game_over = -1
                gameover_ljud.play()

            # letar efter kollision med nextlevel dörren
            if pygame.sprite.spritecollide(self, exit_grupp, False):
                game_over = 1
            # letar efter kollision med de plattformer som rör sig
            for plattform in platform_grupp:
                # kollisionen i x axeln
                if plattform.rect.colliderect(self.rect.x + x_change, self.rect.y, self.width, self.height):
                    x_change = 0
                # kollison i y axeln
                if plattform.rect.colliderect(self.rect.x, self.rect.y + y_change, self.width, self.height):
                    # kollar ifall man är under plattform
                    if abs(self.rect.top + y_change - plattform.rect.bottom) < col_troskel:
                        self.velocity_y = 0
                        y_change = plattform.rect.bottom - self.rect.top
                    # kollar ifall man är över plattform
                    elif abs((self.rect.bottom + y_change) - plattform.rect.top) < col_troskel:
                        self.rect.bottom = plattform.rect.top - 1
                        self.in_air = False
                        y_change = 0
                    # gör så man flyttas med plattformen
                    if plattform.move_x != 0:
                        self.rect.x += plattform.move_direction

            # uppdaterar spelgubbens kordinater
            self.rect.x += x_change
            self.rect.y += y_change

        # när man dör så kommer ett spöke som stiger i y axeln
        elif game_over == -1:
            self.image = self.dead_image
            draw_text("GAME OVER", font_game, blue, (screen_bredd // 2) - 150, screen_hojd // 2)
            if self.rect.y > 200:
                self.rect.y -= 5

        # ritar spelargubben på skärmen
        screen.blit(self.image, self.rect)

        return game_over

    def reset(self, x, y):
        # till animering, döpt alla bilder till samma förutom med olika nummer och de är nummer som skiljer
        self.bilder_r = []
        self.bilder_v = []
        self.index = 0
        self.counter = 0
        # antalet bilder som går runt i animeringen samt lite av animeringen
        for num in range(1, 4):
            bild_r = pygame.image.load(f"guy{num}r.png")
            bild_r = pygame.transform.scale(bild_r, (40, 80))
            bild_v = pygame.transform.flip(bild_r, True, False)
            self.bilder_r.append(bild_r)
            self.bilder_v.append(bild_v)
        # spelargubben + lite av gravitationen samt hopp tekniken
        self.dead_image = pygame.image.load("ghost.png")
        self.image = self.bilder_r[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.velocity_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


# ska gör så man kan göra egna slags "block" som blir som en plattform
class World:
    def __init__(self, data):
        self.tile_list = []

        # hur jordbitarna laddas fram ( de är rutorna), tile är vilket som är vad och är de som fylls i "world creater"
        jord_bild = pygame.image.load("jord.png.jpg")
        grass_bild = pygame.image.load("32xdirt.png")
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    bild = pygame.transform.scale(jord_bild, (tile_size, tile_size))
                    bild_rect = bild.get_rect()
                    bild_rect.x = col_count * tile_size
                    bild_rect.y = row_count * tile_size
                    tile = (bild, bild_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    bild = pygame.transform.scale(grass_bild, (tile_size, tile_size))
                    bild_rect = bild.get_rect()
                    bild_rect.x = col_count * tile_size
                    bild_rect.y = row_count * tile_size
                    tile = (bild, bild_rect)
                    self.tile_list.append(tile)
                # col_count är x och row_count är y
                if tile == 3:
                    alien = Fiende(col_count * tile_size, row_count * tile_size + 30)
                    alien_grupp.add(alien)

                if tile == 4:
                    lava_top = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lavahalf_grupp.add(lava_top)

                if tile == 5:
                    lava = Redlava(col_count * tile_size, row_count * tile_size)
                    lava_grupp.add(lava)

                if tile == 6:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_grupp.add(exit)

                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_grupp.add(coin)

                if tile == 8:
                    plattform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_grupp.add(plattform)

                if tile == 9:
                    plattform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_grupp.add(plattform)

                col_count += 1
            row_count += 1

    # ritar alla "blocks"
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1], )


# fiende klassen
class Fiende(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("pixelated-alien.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    # rörelse till fienderna, abs gör så att numret alltid är positivt
    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


# lava klassen
class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        bild = pygame.image.load("lavatop.png")
        self.image = pygame.transform.scale(bild, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# lava classen fast för hela lava block
class Redlava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("lava.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# coin klassen och centrerar den i mitten av "tile"
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        bild = pygame.image.load("moon coin.png")
        self.image = pygame.transform.scale(bild, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


# exit utgången
class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        bild = pygame.image.load("door.png")
        self.image = pygame.transform.scale(bild, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# de förflyttande plattformarna
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        bild = pygame.image.load("magicdirt.png")
        self.image = pygame.transform.scale(bild, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    # rörelse i y och x axeln
    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


# start position
player = Player(100, screen_hojd - 200)
# gör en grupp som man kan lägga till saker i som olika fiender eller coins
alien_grupp = pygame.sprite.Group()
lavahalf_grupp = pygame.sprite.Group()
lava_grupp = pygame.sprite.Group()
exit_grupp = pygame.sprite.Group()
score_grupp = pygame.sprite.Group()
coin_grupp = pygame.sprite.Group()
platform_grupp = pygame.sprite.Group()

# skapar en fake coin till att visa i analet coins i hörnet
score_coin = Coin(tile_size // 2, tile_size // 2)
score_grupp.add(score_coin)

# laddar in världsdatan och skapar världen
if path.exists(f"leveldata_{level}"):
    with open(f"leveldata_{level}", "rb") as pickle_file:
        world_data = pickle.load(pickle_file)
world = World(world_data)

# restart knappen
restart_knapp = Knapp(screen_bredd // 2 - 100, screen_hojd // 2 - 50, restart_bild)
start_knapp = Knapp(screen_bredd // 2 - 200, screen_hojd // 2, start_bild)
save_knapp = Knapp(screen_bredd // 2 - 200, screen_hojd // 2, save_bild)
quit_knapp = Knapp(screen_bredd // 2 + 100, screen_hojd // 2, quit_bild)

# spel loopen
run = True
while run:
    # fixar så att fps finns vilket gör så animationen funkar
    clock.tick(fps)
    # ritar bakrunden samt allting annat
    screen.fill((0, 0, 0))
    screen.blit(bakrund, (0, 0))
    # startmenyn
    if huvud_meny is True:
        if quit_knapp.draw():
            run = False
        if start_knapp.draw():
            huvud_meny = False
    # ritar sedan världen ifall man trycker på start
    else:
        world.draw()
        # ifall spelet är igång startar de rörelse tiles
        if game_over == 0:
            alien_grupp.update()
            platform_grupp.update()

            # uppdaterar hur många coins man har
            # kollar ifall man kolliderar med en coin, True står för do kill kommandet vilket får coins att försvina
            if pygame.sprite.spritecollide(player, coin_grupp, True):
                level_coins += 1
                score_coins += 1
                coin_ljud.play()
        draw_text("X" + str(score_coins), font_coins, white, tile_size - 10, 10)
        # ritar ut grupperna på skärmen (ritar tiles)
        alien_grupp.draw(screen)
        lava_grupp.draw(screen)
        lavahalf_grupp.draw(screen)
        coin_grupp.draw(screen)
        exit_grupp.draw(screen)
        score_grupp.draw(screen)
        platform_grupp.draw(screen)

        game_over = player.update(game_over)

        # ifall man dör så dyker knappen upp
        if game_over == -1:
            if restart_knapp.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score_coins -= level_coins
                level_coins = 0

        # ifall man klarat nivån
        if game_over == 1:
            # går till nästa nivå
            level += 1
            coins += level_coins

            level_coins = 0

            nextlevel_ljud.play()
            if level <= max_levels:
                # resetar leveln
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text("YOU WON", font_game, blue, (screen_bredd // 2) - 140, screen_hojd // 2)
                # resetar spelet
                if restart_knapp.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    coins = 0
                    score_coins = 0

    # gör så man kan stänga av spelet
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()

pygame.quit()
