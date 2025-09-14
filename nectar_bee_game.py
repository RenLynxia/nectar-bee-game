# Import library yang dibutuhkan
import pygame
import random
import os

# Inisialisasi Pygame
pygame.init()
pygame.mixer.init() # Inisialisasi mixer untuk suara

# Definisikan konstanta warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (144, 238, 144)
SKY_BLUE = (135, 206, 235)
LIGHT_BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
ORANGE = (255, 165, 0)

# Pengaturan layar
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nectar Bee Game")

# Pengaturan font
# Menggunakan font pixel art. Jika gagal, akan menggunakan font bawaan Pygame.
try:
    pixel_font = pygame.font.Font(os.path.join("assets", "pixel_font.ttf"), 36)
    large_font = pygame.font.Font(os.path.join("assets", "pixel_font.ttf"), 50) # Ukuran font diperbarui
    medium_font = pygame.font.Font(os.path.join("assets", "pixel_font.ttf"), 30) # Ukuran font diperbarui
    small_font = pygame.font.Font(os.path.join("assets", "pixel_font.ttf"), 36)
except pygame.error:
    print("Gagal memuat font pixel art. Pastikan 'pixel_font.ttf' ada di direktori 'assets'.")
    print("Menggunakan font bawaan sebagai pengganti.")
    pixel_font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 50) # Ukuran font diperbarui
    medium_font = pygame.font.Font(None, 40) # Ukuran font diperbarui
    small_font = pygame.font.Font(None, 36)

# Representasi pixel art untuk karakter
BEE_PIXEL_ART = [
    "....yyy....",
    "...yyyyy...",
    "..yyyyyyy..",
    ".yyyywyyyy.",
    ".yyyyyYyyyy.",
    "..yyyyyYyy..",
    "...yyYyy...",
    "....yYy....",
    "...r...r...",
    "...r...r...",
]

# Wasp
WASP_PIXEL_ART = [
    "...bBb...",
    "..bBBBb..",
    "bBBBBBBBb",
    "bBBbBbBBb",
    "bBbBBbBbB",
    "bBBBBBBBb",
    "bbbbbbbbb",
    "..b...b..",
    "..b...b..",
    ".bb...bb.",
]

# Muat gambar latar belakang untuk efek parallax
background_image1 = None
background_image2 = None
try:
    if not os.path.isdir("assets"):
        print("Direktori 'assets' tidak ditemukan. Menggunakan latar belakang fallback.")
    else:
        background_image1 = pygame.image.load(os.path.join("assets", "background.png")).convert_alpha()
        background_image1 = pygame.transform.scale(background_image1, (WIDTH, HEIGHT))

        background_image2 = pygame.image.load(os.path.join("assets", "background2.png")).convert_alpha()
        background_image2 = pygame.transform.scale(background_image2, (WIDTH, HEIGHT))
except pygame.error:
    print("Gagal memuat gambar latar belakang. Pastikan 'assets/background.png' dan 'assets/background2.png' ada.")

# Muat efek suara
nectar_sound = None
hit_sound = None
try:
    if not os.path.isdir("assets"):
        print("Direktori 'assets' tidak ditemukan. Suara tidak dimuat.")
    else:
        nectar_sound = pygame.mixer.Sound(os.path.join("assets", "nectar_collect.wav"))
        hit_sound = pygame.mixer.Sound(os.path.join("assets", "hit.wav"))
except pygame.error:
    print("Gagal memuat file suara. Pastikan file 'nectar_collect.wav' dan 'hit.wav' ada di direktori 'assets'.")

# Variabel global untuk posisi latar belakang
bg_y1 = 0
bg_y2 = 0

# Fungsi untuk mengonversi pixel art ke permukaan Pygame
def pixel_surface_from_art(art, scale=4, palette={}):
    """
    Mengonversi representasi pixel art berbasis teks menjadi permukaan Pygame.
    """
    height = len(art)
    width = len(art[0])
    surface = pygame.Surface((width * scale, height * scale), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    pixel_colors = {
        'y': YELLOW,
        'Y': WHITE,
        'w': WHITE,
        'r': LIGHT_BROWN,
        'b': BLACK,
        'B': ORANGE, # Ubah warna tawon agar lebih terlihat
        '.': (0, 0, 0, 0)
    }

    for y, row in enumerate(art):
        for x, pixel_char in enumerate(row):
            color = pixel_colors.get(pixel_char)
            if color:
                pygame.draw.rect(surface, color, (x * scale, y * scale, scale, scale))
    return surface

# Fungsi untuk menggambar latar belakang yang bergerak
def draw_scrolling_background():
    global bg_y1, bg_y2

    if background_image1 and background_image2:
        SCREEN.blit(background_image1, (0, bg_y1))
        SCREEN.blit(background_image1, (0, bg_y1 - HEIGHT))

        SCREEN.blit(background_image2, (0, bg_y2))
        SCREEN.blit(background_image2, (0, bg_y2 - HEIGHT))

        bg_y1 += 1
        bg_y2 += 0.5

        if bg_y1 >= HEIGHT:
            bg_y1 = 0
        if bg_y2 >= HEIGHT:
            bg_y2 = 0
    else:
        # Fallback jika gambar tidak ditemukan
        SCREEN.fill(SKY_BLUE)
        pygame.draw.rect(SCREEN, DARK_GREEN, (0, HEIGHT - 100, WIDTH, 100))

# Kelas objek pemain (Lebah)
class Lebah(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pixel_surface_from_art(BEE_PIXEL_ART, scale=4)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.speed = 4

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

# Kelas objek nektar (Kuning)
class Nektar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([20, 20])
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed = random.randrange(1, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed = random.randrange(1, 5)

# Kelas objek musuh (Tawon)
class Tawon(pygame.sprite.Sprite):
    def __init__(self, speed_multiplier=1.0):
        super().__init__()
        self.image = pixel_surface_from_art(WASP_PIXEL_ART, scale=4)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed = random.randrange(1, 4) * speed_multiplier

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed = random.randrange(1, 4)

# Kelas untuk efek partikel
class Particle(pygame.sprite.Sprite):
    def __init__(self, center_pos, color, size=5):
        super().__init__()
        self.image = pygame.Surface([size, size])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = center_pos
        self.velocity_x = random.uniform(-1, 1)
        self.velocity_y = random.uniform(-1, 1)
        self.life = 60 # Umur partikel dalam frame

    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        self.life -= 1
        if self.life <= 0:
            self.kill() # Hapus partikel saat umurnya habis

# Fungsi untuk menampilkan teks di layar
def display_text(text, font, color, x, y, center=False):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    SCREEN.blit(text_surface, text_rect)

def draw_score_box(score):
    score_text = f"Skor: {score}"
    # Render the text
    text_surface = medium_font.render(score_text, True, WHITE)
    text_rect = text_surface.get_rect()

    # Create the background box
    box_padding = 10
    box_rect = pygame.Rect(10, 10, text_rect.width + box_padding * 2, text_rect.height + box_padding * 2)

    # Draw a semi-transparent black box
    s = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 128))
    SCREEN.blit(s, box_rect)

    # Draw a white border around the box
    pygame.draw.rect(SCREEN, WHITE, box_rect, 2)

    # Position the text inside the box
    text_rect.topleft = (box_rect.left + box_padding, box_rect.top + box_padding)
    SCREEN.blit(text_surface, text_rect)

# Fungsi layar menu utama
def main_menu():
    while True:
        draw_scrolling_background()

        # Mengubah ukuran font pada menu utama
        display_text("Nectar Bee Game", large_font, WHITE, WIDTH / 2, HEIGHT / 4, center=True)

        # Buat tombol
        new_game_button = pygame.Rect(WIDTH / 2 - 125, HEIGHT / 2, 250, 60) # Ukuran tombol diperbarui
        exit_button = pygame.Rect(WIDTH / 2 - 125, HEIGHT / 2 + 80, 250, 60) # Ukuran tombol diperbarui

        pygame.draw.rect(SCREEN, YELLOW, new_game_button)
        pygame.draw.rect(SCREEN, RED, exit_button)

        display_text("Mulai Baru", medium_font, BLACK, WIDTH / 2, HEIGHT / 2 + 30, center=True) # Posisi teks disesuaikan
        display_text("Keluar", medium_font, BLACK, WIDTH / 2, HEIGHT / 2 + 110, center=True) # Posisi teks disesuaikan

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "EXIT"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if new_game_button.collidepoint(event.pos):
                    return "NEW_GAME"
                if exit_button.collidepoint(event.pos):
                    return "EXIT"

# Fungsi layar game over
def game_over_screen(score):
    draw_scrolling_background()

    # Efek layar buram
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 128))
    SCREEN.blit(s, (0, 0))

    display_text("Game Over", large_font, RED, WIDTH / 2, HEIGHT / 4, center=True)
    display_text(f"Skor Anda: {score}", medium_font, WHITE, WIDTH / 2, HEIGHT / 2, center=True)
    display_text("Tekan R untuk kembali ke Menu", small_font, WHITE, WIDTH / 2, HEIGHT * 3/4, center=True)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "EXIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "MENU"
    return "MENU"

# Fungsi utama game
def main():
    game_state = "MENU"
    score = 0
    wasp_spawn_rate = 5
    difficulty_threshold = 10

    while True:
        if game_state == "MENU":
            action = main_menu()
            if action == "NEW_GAME":
                game_state = "PLAYING"
            elif action == "EXIT":
                break

        elif game_state == "PLAYING":
            # Grup sprite
            all_sprites = pygame.sprite.Group()
            nectar_sprites = pygame.sprite.Group()
            wasp_sprites = pygame.sprite.Group()
            particle_sprites = pygame.sprite.Group()

            # Reset game state
            score = 0
            wasp_spawn_rate = 5

            bee = Lebah()
            all_sprites.add(bee)

            for i in range(10):
                nectar = Nektar()
                all_sprites.add(nectar)
                nectar_sprites.add(nectar)

            for i in range(wasp_spawn_rate):
                wasp = Tawon()
                all_sprites.add(wasp)
                wasp_sprites.add(wasp)

            while game_state == "PLAYING":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_state = "EXIT"

                all_sprites.update()
                particle_sprites.update()

                nectar_collisions = pygame.sprite.spritecollide(bee, nectar_sprites, True)
                for nectar in nectar_collisions:
                    score += 1
                    if nectar_sound:
                        nectar_sound.play()

                    for _ in range(10):
                        particle = Particle(nectar.rect.center, YELLOW)
                        all_sprites.add(particle)
                        particle_sprites.add(particle)

                    new_nectar = Nektar()
                    all_sprites.add(new_nectar)
                    nectar_sprites.add(new_nectar)

                    if score % difficulty_threshold == 0 and score > 0:
                        wasp_spawn_rate += 1
                        for _ in range(wasp_spawn_rate):
                            speed_increase = 1.0 + (score / 20)
                            wasp = Tawon(speed_increase)
                            all_sprites.add(wasp)
                            wasp_sprites.add(wasp)

                if pygame.sprite.spritecollide(bee, wasp_sprites, False):
                    if hit_sound:
                        hit_sound.play()
                    game_state = "GAME_OVER"

                draw_scrolling_background()
                all_sprites.draw(SCREEN)
                draw_score_box(score)

                pygame.display.flip()

        elif game_state == "GAME_OVER":
            action = game_over_screen(score)
            if action == "MENU":
                game_state = "MENU"
            elif action == "EXIT":
                break

    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        pygame.quit()

