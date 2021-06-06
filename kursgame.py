from pygame import *
import sys
from os.path import abspath, dirname
from random import choice
from random import randrange

Base_Path = abspath(dirname(__file__))
Font_Path = Base_Path + '/font/'
Image_Path = Base_Path + '/sprites/'
Background_Path = Base_Path + '/sprites/backgrounds/'
Sound_Path = Base_Path + '/sounds/'
white = (255, 255, 255)
yellow = (235, 223, 100)
red = (248, 59, 58)
orange = (255, 128, 34)
beige = (253, 237, 167)
Music1 = (Sound_Path + 'TheIcyCave.wav')
Music2 = (Sound_Path + 'TheFinaloftheFantasy.wav')
Music3 = (Sound_Path + 'TitleTheme.wav')
Screen = display.set_mode((800, 600))
Icon = image.load(Image_Path + 'Space_Ship.png')
Font = Font_Path + 'ProgressPixel.ttf'
Image_Names = ['Space_Ship', 'Secret_Invader', 'invader1_1', 'invader1_2',
               'invader2_1', 'invader2_2', 'invader3_1', 'invader3_2',
               'invader4_1', 'invader4_2', 'invader5_1', 'invader5_2',
               'explosion_blue', 'explosion_yellow', 'explosion_pink',
               'explosion_lightblue', 'explosion_purple', 'laser', 'invader_laser']
Images = {name: image.load(Image_Path + '{}.png'.format(name)).convert_alpha() for name in Image_Names}
Blocker_Position = 450
Invader_Position = 65
Invader_Move_Down = 35
back = randrange(9)
Background = 'Space_Background_{}.png'.format(back)


# Класс корабль игрока
class Space_Ship(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = Images['Space_Ship']
        self.rect = self.image.get_rect(topleft=(375, 540))
        self.speed = 5

    def update(self, keys, *args):
        if keys[K_LEFT] and self.rect.x > 10:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < 740:
            self.rect.x += self.speed
        game.screen.blit(self.image, self.rect)


# Класс снаряды
class Bullet(sprite.Sprite):
    def __init__(self, xpos, ypos, direction, speed, filename, side):
        sprite.Sprite.__init__(self)
        self.image = Images[filename]
        self.rect = self.image.get_rect(topleft=(xpos, ypos))
        self.speed = speed
        self.direction = direction
        self.side = side
        self.filename = filename

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)
        self.rect.y += self.speed * self.direction
        if self.rect.y < 15 or self.rect.y > 600:
            self.kill()


# Класс противники
class Invader(sprite.Sprite):
    def __init__(self, row, column):
        sprite.Sprite.__init__(self)
        self.row = row
        self.column = column
        self.images = []
        self.load_images()
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()

    def toggle_image(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]

    def update(self, *args):
        game.screen.blit(self.image, self.rect)

    def load_images(self):
        images = {0: ['1_2', '1_1'],
                  1: ['2_2', '2_1'],
                  2: ['3_1', '3_2'],
                  3: ['4_2', '4_1'],
                  4: ['5_1', '5_2'],
                  }
        img1, img2 = (Images['invader{}'.format(img_num)] for img_num in images[self.row])
        self.images.append(transform.scale(img1, (40, 35)))
        self.images.append(transform.scale(img2, (40, 35)))


# Класс группа противников
class Invaders_Group(sprite.Group):
    def __init__(self, columns, rows):
        sprite.Group.__init__(self)
        self.invaders = [[None] * columns for _ in range(rows)]
        self.columns = columns
        self.rows = rows
        self.leftAddMove = 0
        self.rightAddMove = 0
        self.moveTime = 600
        self.direction = 1
        self.rightMoves = 30
        self.leftMoves = 30
        self.moveNumber = 15
        self.timer = time.get_ticks()
        self.bottom = game.invaderPosition + ((rows - 1) * 45) + 35
        self._aliveColumns = list(range(columns))
        self._leftAliveColumn = 0
        self._rightAliveColumn = columns - 1

    def update(self, current_time):
        if current_time - self.timer > self.moveTime:
            if self.direction == 1:
                max_move = self.rightMoves + self.rightAddMove
            else:
                max_move = self.leftMoves + self.leftAddMove
            if self.moveNumber >= max_move:
                self.leftMoves = 30 + self.rightAddMove
                self.rightMoves = 30 + self.leftAddMove
                self.direction *= -1
                self.moveNumber = 0
                self.bottom = 0
                for invader in self:
                    invader.rect.y += Invader_Move_Down
                    invader.toggle_image()
                    if self.bottom < invader.rect.y + 35:
                        self.bottom = invader.rect.y + 35
            else:
                velocity = 10 if self.direction == 1 else -10
                for invader in self:
                    invader.rect.x += velocity
                    invader.toggle_image()
                self.moveNumber += 1
            self.timer += self.moveTime

    def add_internal(self, *sprites):
        super(Invaders_Group, self).add_internal(*sprites)
        for s in sprites:
            self.invaders[s.row][s.column] = s

    def remove_internal(self, *sprites):
        super(Invaders_Group, self).remove_internal(*sprites)
        for s in sprites:
            self.kill(s)
        self.update_speed()

    def is_column_dead(self, column):
        return not any(self.invaders[row][column] for row in range(self.rows))

    def random_bottom(self):
        col = choice(self._aliveColumns)
        col_invaders = (self.invaders[row - 1][col] for row in range(self.rows, 0, -1))
        return next((en for en in col_invaders if en is not None), None)

    def update_speed(self):
        if len(self) == 1:
            self.moveTime = 200
        elif len(self) <= 10:
            self.moveTime = 400

    def kill(self, invader):
        self.invaders[invader.row][invader.column] = None
        is_column_dead = self.is_column_dead(invader.column)
        if is_column_dead:
            self._aliveColumns.remove(invader.column)
        if invader.column == self._rightAliveColumn:
            while self._rightAliveColumn > 0 and is_column_dead:
                self._rightAliveColumn -= 1
                self.rightAddMove += 5
                is_column_dead = self.is_column_dead(self._rightAliveColumn)
        elif invader.column == self._leftAliveColumn:
            while self._leftAliveColumn < self.columns and is_column_dead:
                self._leftAliveColumn += 1
                self.leftAddMove += 5
                is_column_dead = self.is_column_dead(self._leftAliveColumn)


# Класс стена
class Block(sprite.Sprite):
    def __init__(self, size, color, row, column):
        sprite.Sprite.__init__(self)
        self.height = size
        self.width = size
        self.color = color
        self.image = Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.row = row
        self.column = column

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)


# Класс секретный захватчик
class Secret_Invader(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = Images['Secret_Invader']
        self.image = transform.scale(self.image, (75, 35))
        self.rect = self.image.get_rect(topleft=(-80, 45))
        self.row = 5
        self.moveTime = 25000
        self.direction = 1
        self.timer = time.get_ticks()
        self.secret_invader_Entered = mixer.Sound(Sound_Path + 'secretinvaderentered.wav')
        self.secret_invader_Entered.set_volume(0.3)
        self.playSound = True

    def update(self, keys, currentTime, *args):
        resetTimer = False
        passed = currentTime - self.timer
        if passed > self.moveTime:
            if (self.rect.x < 0 or self.rect.x > 800) and self.playSound:
                self.secret_invader_Entered.play()
                self.playSound = False
            if self.rect.x < 840 and self.direction == 1:
                self.secret_invader_Entered.fadeout(4000)
                self.rect.x += 2
                game.screen.blit(self.image, self.rect)
            if self.rect.x > -100 and self.direction == -1:
                self.secret_invader_Entered.fadeout(4000)
                self.rect.x -= 2
                game.screen.blit(self.image, self.rect)
        if self.rect.x > 830:
            self.playSound = True
            self.direction = -1
            resetTimer = True
        if self.rect.x < -90:
            self.playSound = True
            self.direction = 1
            resetTimer = True
        if passed > self.moveTime and resetTimer:
            self.timer = currentTime


# Класс взрыв захватчика
class Invader_Explosion(sprite.Sprite):
    def __init__(self, invader, *groups):
        super(Invader_Explosion, self).__init__(*groups)
        self.image = transform.scale(self.get_image(invader.row), (40, 35))
        self.image2 = transform.scale(self.get_image(invader.row), (50, 45))
        self.rect = self.image.get_rect(topleft=(invader.rect.x, invader.rect.y))
        self.timer = time.get_ticks()

    @staticmethod
    def get_image(row):
        img_colors = ['purple', 'blue', 'lightblue', 'pink', 'yellow']
        return Images['explosion_{}'.format(img_colors[row])]

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 100:
            game.screen.blit(self.image, self.rect)
        elif passed <= 200:
            game.screen.blit(self.image2, (self.rect.x - 6, self.rect.y - 6))
        elif 400 < passed:
            self.kill()


# Класс взрыв секретного захватчика
class Secret_Invader_Explosion(sprite.Sprite):
    def __init__(self, secret_invader, score, *groups):
        super(Secret_Invader_Explosion, self).__init__(*groups)
        self.text = Text(Font, 20, str(score), white, secret_invader.rect.x + 20, secret_invader.rect.y + 6)
        self.timer = time.get_ticks()

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 200 or 400 < passed <= 600:
            self.text.draw(game.screen)
        elif 600 < passed:
            self.kill()


# Класс взрыв корабля игрока
class Space_Ship_Explosion(sprite.Sprite):
    def __init__(self, space_ship, *groups):
        super(Space_Ship_Explosion, self).__init__(*groups)
        self.image = Images['Space_Ship']
        self.rect = self.image.get_rect(topleft=(space_ship.rect.x, space_ship.rect.y))
        self.timer = time.get_ticks()

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if 300 < passed <= 600:
            game.screen.blit(self.image, self.rect)
        elif 900 < passed:
            self.kill()


# Класс дополнительные жизни
class Extra_Life(sprite.Sprite):
    def __init__(self, xpos, ypos):
        sprite.Sprite.__init__(self)
        self.image = Images['Space_Ship']
        self.image = transform.scale(self.image, (23, 23))
        self.rect = self.image.get_rect(topleft=(xpos, ypos))

    def update(self, *args):
        game.screen.blit(self.image, self.rect)


# Класс текст
class Text(object):
    def __init__(self, textFont, size, message, color, xpos, ypos):
        self.font = font.Font(textFont, size)
        self.surface = self.font.render(message, True, color)
        self.rect = self.surface.get_rect(topleft=(xpos, ypos))

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


# Игра
class SpaceInvaders(object):
    def __init__(self):
        mixer.pre_init(44100, -16, 1, 4096)
        init()
        self.music = mixer.music.load(Music2)
        self.music_play = mixer.music.play(loops=-1)
        self.clock = time.Clock()
        self.caption = display.set_caption('Космические Захватчики')
        self.icon = display.set_icon(Icon)
        self.screen = Screen
        self.background = image.load(Background_Path + Background).convert()
        self.startGame = False
        self.mainScreen = True
        self.gameOver = False
        self.invaderPosition = Invader_Position
        self.titleText = Text(Font, 45, 'Космические Захватчики', white, 65, 100)
        self.titleText2 = Text(Font, 20, 'Для старта нажмите любую клавишу', white, 180, 205)
        self.gameOverText = Text(Font, 45, 'Игра закончена', red, 200, 230)
        self.nextRoundText = Text(Font, 45, 'Следующий раунд', yellow, 170, 230)
        self.invader1Text = Text(Font, 25, '   =   10 очков', white, 365, 270)
        self.invader2Text = Text(Font, 25, '   =   20 очков', white, 365, 320)
        self.invader3Text = Text(Font, 25, '   =   30 очков', white, 365, 370)
        self.invadersecretText = Text(Font, 25, '   =   ???', red, 365, 420)
        self.scoreText = Text(Font, 20, 'Счет', white, 10, 3)
        self.livesText = Text(Font, 20, 'Жизни', white, 625, 3)
        self.life1 = Extra_Life(715, 12)
        self.life2 = Extra_Life(742, 12)
        self.life3 = Extra_Life(769, 12)
        self.livesGroup = sprite.Group(self.life1, self.life2, self.life3)

    def reset(self, score):
        self.player = Space_Ship()
        self.playerGroup = sprite.Group(self.player)
        self.explosionsGroup = sprite.Group()
        self.bullets = sprite.Group()
        self.secret_invader_Ship = Secret_Invader()
        self.secret_invader_Group = sprite.Group(self.secret_invader_Ship)
        self.invaderBullets = sprite.Group()
        self.make_invaders()
        self.allSprites = sprite.Group(self.player, self.invaders, self.livesGroup, self.secret_invader_Ship)
        self.keys = key.get_pressed()
        self.timer = time.get_ticks()
        self.noteTimer = time.get_ticks()
        self.shipTimer = time.get_ticks()
        self.score = score
        self.create_audio()
        self.makeNewShip = False
        self.shipAlive = True

    def make_blockers(self, number):
        blockerGroup = sprite.Group()
        for row in range(4):
            for column in range(9):
                blocker = Block(10, beige, row, column)
                blocker.rect.x = 50 + (200 * number) + (column * blocker.width)
                blocker.rect.y = Blocker_Position + (row * blocker.height)
                blockerGroup.add(blocker)
        return blockerGroup

    def create_audio(self):
        self.sounds = {}
        for sound_name in ['shoot', 'shoot2', 'invaderkilled', 'secretinvaderkilled', 'shipexplosion']:
            self.sounds[sound_name] = mixer.Sound(Sound_Path + '{}.wav'.format(sound_name))
            self.sounds[sound_name].set_volume(0.2)
        self.musicNotes = [mixer.Sound(Sound_Path + '{}.wav'.format(i)) for i in range(4)]
        for sound in self.musicNotes:
            sound.set_volume(0.5)
        self.noteIndex = 0

    def play_main_music(self, currentTime):
        if currentTime - self.noteTimer > self.invaders.moveTime:
            self.note = self.musicNotes[self.noteIndex]
            if self.noteIndex < 3:
                self.noteIndex += 1
            else:
                self.noteIndex = 0
            self.note.play()
            self.noteTimer += self.invaders.moveTime

    @staticmethod
    def should_exit(evt):
        # type: (pygame.event.EventType) -> bool
        return evt.type == QUIT

    def check_input(self):
        self.keys = key.get_pressed()
        for e in event.get():
            if self.should_exit(e):
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_SPACE:
                    if len(self.bullets) == 0 and self.shipAlive:
                        if self.score < 1000:
                            bullet = Bullet(self.player.rect.x + 23, self.player.rect.y + 5, -1, 7, 'laser', 'center')
                            self.bullets.add(bullet)
                            self.allSprites.add(self.bullets)
                            self.sounds['shoot'].play()
                        else:
                            leftbullet = Bullet(self.player.rect.x + 8, self.player.rect.y + 5, -1, 15, 'laser', 'left')
                            rightbullet = Bullet(self.player.rect.x + 38, self.player.rect.y + 5, -1, 15, 'laser', 'right')
                            self.bullets.add(leftbullet)
                            self.bullets.add(rightbullet)
                            self.allSprites.add(self.bullets)
                            self.sounds['shoot2'].play()

    def make_invaders(self):
        invaders = Invaders_Group(10, 5)
        for row in range(5):
            for column in range(10):
                invader = Invader(row, column)
                invader.rect.x = 157 + (column * 50)
                invader.rect.y = self.invaderPosition + (row * 45)
                invaders.add(invader)
        self.invaders = invaders

    def make_invaders_shoot(self):
        if (time.get_ticks() - self.timer) > 700 and self.invaders:
            invader = self.invaders.random_bottom()
            self.invaderBullets.add(Bullet(invader.rect.x + 14, invader.rect.y + 20, 1, 5, 'invader_laser', 'center'))
            self.allSprites.add(self.invaderBullets)
            self.timer = time.get_ticks()

    def calculate_score(self, row):
        scores = {0: 30,
                  1: 20,
                  2: 20,
                  3: 10,
                  4: 10,
                  5: choice([50, 100, 150, 300])
                  }
        score = scores[row]
        self.score += score
        return score

    def create_main_menu(self):
        self.invader1 = Images['invader5_1']
        self.invader1 = transform.scale(self.invader1, (40, 40))
        self.invader2 = Images['invader4_2']
        self.invader2 = transform.scale(self.invader2, (40, 40))
        self.invader3 = Images['invader3_1']
        self.invader3 = transform.scale(self.invader3, (40, 40))
        self.invader4 = Images['invader2_2']
        self.invader4 = transform.scale(self.invader4, (40, 40))
        self.invader5 = Images['invader1_2']
        self.invader5 = transform.scale(self.invader5, (40, 40))
        self.invadersecret = Images['Secret_Invader']
        self.invadersecret = transform.scale(self.invadersecret, (80, 40))
        self.screen.blit(self.invader1, (268, 270))
        self.screen.blit(self.invader2, (318, 270))
        self.screen.blit(self.invader3, (268, 320))
        self.screen.blit(self.invader4, (318, 320))
        self.screen.blit(self.invader5, (318, 370))
        self.screen.blit(self.invadersecret, (299, 420))

    def check_collisions(self):
        sprite.groupcollide(self.bullets, self.invaderBullets, True, True)
        for invader in sprite.groupcollide(self.invaders, self.bullets, True, True).keys():
            self.sounds['invaderkilled'].play()
            self.calculate_score(invader.row)
            Invader_Explosion(invader, self.explosionsGroup)
            self.gameTimer = time.get_ticks()
        for secret_invader in sprite.groupcollide(self.secret_invader_Group, self.bullets, True, True).keys():
            secret_invader.secret_invader_Entered.stop()
            self.sounds['secretinvaderkilled'].play()
            score = self.calculate_score(secret_invader.row)
            Secret_Invader_Explosion(secret_invader, score, self.explosionsGroup)
            newShip = Secret_Invader()
            self.allSprites.add(newShip)
            self.secret_invader_Group.add(newShip)
        for player in sprite.groupcollide(self.playerGroup, self.invaderBullets, True, True).keys():
            if self.life3.alive():
                self.life3.kill()
            elif self.life2.alive():
                self.life2.kill()
            elif self.life1.alive():
                self.life1.kill()
            else:
                self.gameOver = True
                self.startGame = False
            self.sounds['shipexplosion'].play()
            Space_Ship_Explosion(player, self.explosionsGroup)
            self.makeNewShip = True
            self.shipTimer = time.get_ticks()
            self.shipAlive = False
        if self.invaders.bottom >= 540:
            sprite.groupcollide(self.invaders, self.playerGroup, True, True)
            if not self.player.alive() or self.invaders.bottom >= 600:
                self.gameOver = True
                self.startGame = False
        sprite.groupcollide(self.bullets, self.allBlockers, True, True)
        sprite.groupcollide(self.invaderBullets, self.allBlockers, True, True)
        if self.invaders.bottom >= Blocker_Position:
            sprite.groupcollide(self.invaders, self.allBlockers, False, True)

    def create_new_ship(self, createShip, currentTime):
        if createShip and (currentTime - self.shipTimer > 900):
            self.player = Space_Ship()
            self.allSprites.add(self.player)
            self.playerGroup.add(self.player)
            self.makeNewShip = False
            self.shipAlive = True

    def create_game_over(self, currentTime):
        self.screen.blit(self.background, (0, 0))
        passed = currentTime - self.timer
        if passed < 750:
            self.gameOverText.draw(self.screen)
        elif 750 < passed < 1500:
            self.screen.blit(self.background, (0, 0))
        elif 1500 < passed < 2250:
            self.gameOverText.draw(self.screen)
        elif 2250 < passed < 3000:
            self.screen.blit(self.background, (0, 0))
        elif passed > 3000:
            self.mainScreen = True
        for e in event.get():
            if self.should_exit(e):
                sys.exit()

    def main(self):
        while True:
            if self.mainScreen:
                self.screen.blit(self.background, (0, 0))
                self.titleText.draw(self.screen)
                self.titleText2.draw(self.screen)
                self.invader1Text.draw(self.screen)
                self.invader2Text.draw(self.screen)
                self.invader3Text.draw(self.screen)
                self.invadersecretText.draw(self.screen)
                self.create_main_menu()
                for e in event.get():
                    if self.should_exit(e):
                        sys.exit()
                    if e.type == KEYUP:
                        # Создание стен только в новой игре, а не в новом раунде
                        self.allBlockers = sprite.Group(self.make_blockers(0), self.make_blockers(1),
                                                        self.make_blockers(2), self.make_blockers(3))
                        self.livesGroup.add(self.life1, self.life2, self.life3)
                        self.reset(0)
                        self.startGame = True
                        self.mainScreen = False
                        self.music = mixer.music.load(Music1)
                        self.music_play = mixer.music.play(loops=-1)
            elif self.startGame:
                if not self.invaders and not self.explosionsGroup:
                    currentTime = time.get_ticks()
                    if currentTime - self.gameTimer < 3000:
                        self.screen.blit(self.background, (0, 0))
                        self.scoreText2 = Text(Font, 20, str(self.score), orange, 75, 5)
                        self.scoreText.draw(self.screen)
                        self.scoreText2.draw(self.screen)
                        self.nextRoundText.draw(self.screen)
                        self.livesText.draw(self.screen)
                        self.livesGroup.update()
                        self.check_input()
                    if currentTime - self.gameTimer > 3000:
                        # Перемещение захватчиков ближе к низу
                        self.invaderPosition += Invader_Move_Down
                        self.reset(self.score)
                        self.gameTimer += 3000
                else:
                    currentTime = time.get_ticks()
                    self.play_main_music(currentTime)
                    self.screen.blit(self.background, (0, 0))
                    self.allBlockers.update(self.screen)
                    self.scoreText2 = Text(Font, 20, str(self.score), orange, 75, 5)
                    self.scoreText.draw(self.screen)
                    self.scoreText2.draw(self.screen)
                    self.livesText.draw(self.screen)
                    self.check_input()
                    self.invaders.update(currentTime)
                    self.allSprites.update(self.keys, currentTime)
                    self.explosionsGroup.update(currentTime)
                    self.check_collisions()
                    self.create_new_ship(self.makeNewShip, currentTime)
                    self.make_invaders_shoot()
            elif self.gameOver:
                currentTime = time.get_ticks()
                # Сброс исходной позиции захватчика
                self.invaderPosition = Invader_Position
                self.create_game_over(currentTime)
                self.music_stop = mixer.music.stop()
                self.music = mixer.music.load(Music3)
                self.music_play = mixer.music.play(loops=-1)
            display.update()
            self.clock.tick(60)


if __name__ == '__main__':
    game = SpaceInvaders()
    game.main()