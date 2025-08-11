import pgzrun

WIDTH = 1024
HEIGHT = 512
TILE_SIZE = 70
TITLE = "ET Astronauta"
# Estados do jogo
MENU, GAME, GAMEOVER = "menu", "game", "gameover"
game_state = MENU
music_on = True
# Mapa do nível
LEVEL_MAP = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 1, 2, 3, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
]
# Texturas por tipo
TILE_IMAGES = {
    1: "tile_left",
    2: "tile_mid",
    3: "tile_right",
    4: "tile_center",
    5: "tile_full",
}
platforms = []

def load_level():
    global platforms
    platforms.clear()
    for row_idx, row in enumerate(LEVEL_MAP):
        for col_idx, tile in enumerate(row):
            if tile != 0:
                x = col_idx * TILE_SIZE + TILE_SIZE // 2
                y = row_idx * TILE_SIZE + TILE_SIZE // 2
                platforms.append(Actor(TILE_IMAGES[tile], (x, y)))

# Classes
class Player(Actor):
    def __init__(self, pos):
        super().__init__("player_idle1", pos)
        self.speed_y = 0
        self.on_ground = False
        self.frame = 0
        self.anim_timer = 0

    def update_animation(self):
        self.anim_timer += 1
        if self.on_ground:
            if keyboard.left or keyboard.right:
                if self.anim_timer % 10 == 0:
                    self.image = f"player_walk{self.frame + 1}"
                    self.frame = (self.frame + 1) % 2
            else:
                if self.anim_timer % 20 == 0:
                    self.image = f"player_idle{self.frame + 1}"
                    self.frame = (self.frame + 1) % 2

    def move(self):
        if keyboard.left:
            self.x -= 3
        if keyboard.right:
            self.x += 3
        if keyboard.space and self.on_ground:
            self.speed_y = -12
            self.on_ground = False
            if music_on:
                sounds.jump.play()
        self.y += self.speed_y
        self.speed_y += 0.3
        self.on_ground = False
        for plat in platforms:
            if self.colliderect(plat) and self.speed_y >= 0:
                self.y = plat.y - TILE_SIZE
                self.speed_y = 0
                self.on_ground = True
        self.x = max(0, min(self.x, WIDTH))

class Enemy(Actor):
    def __init__(self, pos, move_range):
        super().__init__("enemy_idle1", pos)
        self.start_x = pos[0]
        self.move_range = move_range
        self.direction = 1
        self.frame = 0
        self.anim_timer = 0
        self.state = "idle"
        self.idle_time = 2
        self.walk_time = 4
        self.timer = 0

    def update_animation(self):
        self.anim_timer += 1
        if self.state == "idle":
            if self.anim_timer % 20 == 0:
                self.image = f"enemy_idle{self.frame + 1}"
                self.frame = (self.frame + 1) % 2
        else:
            if self.anim_timer % 10 == 0:
                self.image = f"enemy_walk{self.frame + 1}"
                self.frame = (self.frame + 1) % 2

    def move(self):
        self.timer += 1 / 60
        if self.state == "idle":
            if self.timer >= self.idle_time:
                self.state = "walk"
                self.timer = 0
        else:
            self.x += self.direction * 2
            if not (
                self.start_x - self.move_range
                <= self.x
                <= self.start_x + self.move_range
            ):
                self.direction *= -1
            if self.timer >= self.walk_time:
                self.state = "idle"
                self.timer = 0
        self.update_animation()
# Objetos do jogo
player = Player((100, 407))
enemies = [Enemy((500, 407), 40), Enemy((700, 407), 80), Enemy((300, 407), 40)]
menu_buttons = [("Iniciar", Actor("button_start", (WIDTH // 2, HEIGHT // 2 - 50))), ("Som ON", Actor("button_music", (WIDTH // 2, HEIGHT // 2 + 20))), ("Sair", Actor("button_exit", (WIDTH // 2, HEIGHT // 2 + 90)))]

# Funções de controle
def draw_menu():
    for label, button in menu_buttons:
        button.draw()
        text = label if label != "Som ON" else ("Som ON" if music_on else "Som OFF")
        screen.draw.text(text, center=button.center, fontsize=18, color="white", owidth=2, ocolor="black")

def draw():
    screen.clear()
    screen.blit("background", (0, 0))
    if game_state == MENU:
        draw_menu()
    elif game_state == GAME:
        for plat in platforms:
            plat.draw()
        player.draw()
        for e in enemies:
            e.draw()
    elif game_state == GAMEOVER:
        screen.draw.text("GAME OVER", center=(WIDTH / 2, HEIGHT / 2 - 50), fontsize=80, color="red")
        screen.draw.text("Clique aqui para voltar ao menu", center=(WIDTH / 2, HEIGHT / 2 + 50), fontsize=40, color="white")

def update():
    global game_state
    if game_state == GAME:
        player.move()
        player.update_animation()
        for e in enemies:
            e.move()
            if player.colliderect(e):
                if music_on:
                    sounds.hit.play()
                game_over()

def game_over():
    global game_state
    game_state = GAMEOVER

def on_mouse_down(pos):
    global game_state
    if game_state == MENU:
        if menu_buttons[0][1].collidepoint(pos):
            start_game()
        elif menu_buttons[1][1].collidepoint(pos):
            toggle_music()
        elif menu_buttons[2][1].collidepoint(pos):
            exit()
    elif game_state == GAMEOVER:
        game_state = MENU

def start_game():
    global game_state, player, enemies
    player = Player((100, 407))
    enemies = [Enemy((500, 407), 40), Enemy((700, 407), 80), Enemy((300, 407), 40)]
    game_state = GAME
# Música
def toggle_music():
    global music_on
    music_on = not music_on
    if music_on:
        music.play("bg_music")
    else:
        music.stop()

music.play("bg_music")
load_level()
pgzrun.go()
