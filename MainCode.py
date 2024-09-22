import pygame
from os.path import join
from random import randint, uniform


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load((join("images", "player.png"))).convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_frect(center=(Window_Width / 2, Window_Height / 2))
        self.direction = pygame.Vector2()
        self.speed = 300

        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 300

        # mask
        self.mask = pygame.mask.from_surface(self.image)
        # mask_surface = mask.to_surface()
        # mask_surface.set_colorkey((0,0,0))
        # self.image = mask_surface
        # lives
        self.lives = 5

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_aud.play()
            laser_aud.set_volume(0.2)

        self.laser_timer()

        # continuous rotation


class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=(randint(0, Window_Width), randint(0, Window_Height)))


class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, position, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=position)

    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, position, groups):
        super().__init__(groups)
        self.original_surface = pygame.image.load((join("images", "meteor.png"))).convert_alpha()
        self.image = self.original_surface
        self.rect = self.image.get_frect(center=position)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 4500
        self.direction = pygame.Vector2(uniform(-0.7, 0.5), 1)
        self.speed = randint(200, 300)
        self.rotation_speed = randint(40, 80)
        self.rotation = 0

        # transform

    def update(self, dt):
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surface, self.rotation, 1)
        self.rect = self.image.get_frect(center=self.rect.center)

        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()


class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, position, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center=position)

    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()


def collisions():
    global Running
    global game_over
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        player.lives -= 1
        DisplayMessage(f" Taking Damage!!! \n Lives left: {player.lives}", player.rect.center, 1500, all_sprites)
        if player.lives == 0:
            game_over = True
            Running = False
        damage_aud.play()
        damage_aud.set_volume(0.4)

    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_aud.play()
            explosion_aud.set_volume(0.2)


def lives_display():
    lives_surface = font.render(f"Lives: {player.lives}", True, (240, 240, 220))
    lives_rect = lives_surface.get_frect(topleft=(10, 60))  # Position below the score
    display_surface.blit(lives_surface, lives_rect)


def show_menu():
    menu_background = pygame.image.load(join("images", "backgroundmenu.png")).convert_alpha()
    menu_background = pygame.transform.scale(menu_background, (Window_Width, Window_Height))
    menu_font = pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 60)
    # menu_font2 = pygame.font.Font(join("images")," ")
    title_surface = menu_font.render("METEOR SHOOTER", True, (0, 0, 10))

    start_surface = menu_font.render("START", True, (240, 240, 220))
    quit_surface = menu_font.render("QUIT", True, (240, 240, 220))

    title_rect = title_surface.get_rect(left = 50,top = 100)
    start_rect = start_surface.get_rect(left=100, top=Window_Height / 3)
    quit_rect = quit_surface.get_rect(left=100, top=Window_Height / 2.3)

    def display_message(message, duration):
        font = pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 30)
        message_surface = font.render(message, True, (255, 0, 0))  # Red color
        message_rect = message_surface.get_rect(center=(Window_Width / 2, Window_Height / 2))

        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < duration:
            display_surface.fill((0, 0, 0), (0, 0, Window_Width, Window_Height))  # Clear screen
            display_surface.blit(message_surface, message_rect)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

    while True:
        display_surface.blit(menu_background, (0, 0))
        # display_surface.fill((0, 0, 200))  # Black background for the menu
        display_surface.blit(title_surface, title_rect)

        # Get the current mouse position
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        # Highlight "Start" if the mouse is hovering over it
        if start_rect.collidepoint(mouse_pos):
            start_surface = menu_font.render("Start", True, (255, 255, 0))  # Highlighted color
            if mouse_click[0]:
                game_start_time = pygame.time.get_ticks()  # Left mouse button is clicked
                return  # Exits the menu and starts the game
        else:
            start_surface = menu_font.render("Start", True, (34, 214, 64))

        # Highlight "Quit" if the mouse is hovering over it
        if quit_rect.collidepoint(mouse_pos):
            quit_surface = menu_font.render("Quit", True, (255, 255, 0))  # Highlighted color
            if mouse_click[0]:  # Left mouse button is clicked
                pygame.quit()
                quit()  # Exits the game
        else:
            quit_surface = menu_font.render("Quit", True, (240, 0, 0))

        # Draw the updated buttons
        display_surface.blit(start_surface, start_rect)
        display_surface.blit(quit_surface, quit_rect)

        # Check for QUIT event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        pygame.display.update()


game_start_time = 0


def score_display():
    current_time = (pygame.time.get_ticks() - game_start_time) // 100
    text_surface = font.render(str(current_time), True, (240, 240, 220))
    text_rect = text_surface.get_frect(midbottom=(Window_Width / 2, Window_Height - 50))
    display_surface.blit(text_surface, text_rect)
    pygame.draw.rect(display_surface, (240, 240, 220), text_rect.inflate(20, 10).move(0, -8), 5, 15)


class DisplayMessage(pygame.sprite.Sprite):
    def __init__(self, text, position, duration, groups):
        super().__init__(groups)
        self.font = pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 30)
        self.image = self.font.render(text, True, (255, 0, 0))
        self.rect = self.image.get_frect(center=position)
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.y_speed = -100  # Speed at which text moves up

    def update(self, dt):
        # Move text up
        self.rect.centery += self.y_speed * dt

        # Check if duration has passed
        if pygame.time.get_ticks() - self.start_time > self.duration:
            self.kill()


def game_over_screen():
    global Running
    display_surface.fill((0, 0, 0))  # Black background for game over screen

    # Display the "Nice Try!" message
    font = pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 60)
    message_surface = font.render("Nice Try!", True, (255, 0, 0))  # Red color
    message_rect = message_surface.get_rect(center=(Window_Width / 2, Window_Height / 3))
    display_surface.blit(message_surface, message_rect)

    # Display the score
    # score = current_time
    # score_surface = font.render(f"Score: {score}", True, (240, 240, 220))
    # score_rect = score_surface.get_rect(center=(Window_Width / 2, Window_Height / 2))
    # display_surface.blit(score_surface, score_rect)

    pygame.display.update()
    pygame.time.wait(2000)  # Show the message for 2 seconds

    # Return to the main menu
    show_menu()
    game_over = False


# general setup
pygame.init()
Window_Width, Window_Height = 1280, 720
display_surface = pygame.display.set_mode((Window_Width, Window_Height))
pygame.display.set_caption("Space Game")
Running = True
clock = pygame.time.Clock()

# import
star_surf = pygame.image.load((join("images", "star.png"))).convert_alpha()
meteor_surf = pygame.image.load((join("images", "meteor.png"))).convert_alpha()
laser_surf = pygame.image.load((join("images", "laser.png"))).convert_alpha()
font = pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 40)
text_surface = font.render("Meteor Shooter", True, (240, 240, 220))
explosion_frames = [pygame.image.load(join("images", "explosion", f"{i}.png")).convert_alpha() for i in range(21)]
laser_aud = pygame.mixer.Sound(join("audio", "laser.wav"))
explosion_aud = pygame.mixer.Sound(join("audio", "explosion.wav"))
damage_aud = pygame.mixer.Sound(join("audio", "damage.ogg"))
game_music = pygame.mixer.Sound(join("audio", "game_music.wav"))
game_music.set_volume(0.1)
game_music.play(loops=-1)

# sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

for i in range(20):
    Star(all_sprites, star_surf)
player = Player(all_sprites)

# custom event -> meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 400)

show_menu()
game_over = False

while Running:

    # event_loop
    dt = clock.tick() / 1000
    # print(clock.get_fps())


    if game_over:
        game_over_screen()
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False
        if event.type == meteor_event:
            x, y = randint(0, Window_Width), randint(-200, -100)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))
    # updates
    all_sprites.update(dt)
    collisions()

    # draw_the_game
    display_surface.fill((94, 122, 173))
    display_surface.blit(text_surface, (5, 5))
    all_sprites.draw(display_surface)
    score_display()
    lives_display()

    # draw test

    pygame.display.update()

pygame.quit()
