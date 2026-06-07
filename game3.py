import pygame
import pygame.freetype
import random
import string
from gtts import gTTS
import tempfile

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spelling Catch Game")

WHITE = (255,255,255)
BLUE = (50,150,255)
YELLOW = (255,255,0)
BLACK = (0,0,0)

font = pygame.freetype.SysFont(None, 28)
big_font = pygame.freetype.SysFont(None, 45)
letter_font = pygame.freetype.SysFont(None, 28)

# ✅ WORDS
word_list = ["CAT","DOG","SUN","TREE","BALL","HAIR","EYES","MOUTH","HAND","LEG"]

# ✅ SAFE IMAGE LOADER
def load_image(name):
    try:
        return pygame.image.load(name).convert_alpha()
    except:
        return None

images = {
    "CAT": load_image("cat.jpeg"),
    "DOG": load_image("dog.jpeg"),
    "SUN": load_image("sun.jpeg"),
    "BALL": load_image("ball.jpeg"),
    "TREE": load_image("tree.jpeg"),
    "HAIR": load_image("hair.jpeg"),
    "EYES": load_image("eyes.jpeg"),
    "MOUTH": load_image("mouth.jpeg"),
    "HAND": load_image("hand.png"),
    "LEG": load_image("leg.jpg")
}

# ✅ NO REPEAT SYSTEM
available_words = word_list.copy()
random.shuffle(available_words)

def get_next_word():
    global available_words
    if not available_words:
        available_words = word_list.copy()
        random.shuffle(available_words)
    return available_words.pop()

def new_game(level):
    word = get_next_word()
    return {
        "target": word,
        "progress": "",
        "star_x": random.randint(50, WIDTH-50),
        "star_y": -20,
        "letter": word[0],
        "speed": 3 + level,
        "attempts": 0
    }

# ✅ SPEECH
def speak_word(word):
    try:
        pygame.mixer.music.stop()
        for letter in word:
            tts = gTTS(text=letter)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                filename = f.name
                tts.save(filename)

            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.delay(100)

        pygame.time.delay(400)

        tts = gTTS(text=word.lower())
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            filename = f.name
            tts.save(filename)

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

    except:
        pass

# ✅ GAME STATE
level = 1
score = 0
lives = 3

game = new_game(level)

player_x = WIDTH//2
player_y = HEIGHT - 60
player_w, player_h = 50, 50

show_image = False
completed_word = None

clock = pygame.time.Clock()

# ⭐ BACKGROUND
bg_stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(1,2)] for _ in range(40)]

while True:

    screen.fill((10,10,30))

    # ⭐ stars
    for s in bg_stars:
        s[1] += s[2]
        if s[1] > HEIGHT:
            s[0] = random.randint(0, WIDTH)
            s[1] = 0
        pygame.draw.circle(screen, WHITE, (int(s[0]), int(s[1])), 2)

    # ✅ SINGLE EVENT LOOP (IMPORTANT FIX)
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # ✅ ENTER TO CONTINUE IMAGE
        if show_image and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                show_image = False
                game = new_game(level)

    # ✅ SHOW IMAGE MODE
    if show_image:

        if images.get(completed_word):
            img = pygame.transform.scale(images[completed_word], (200,200))
            screen.blit(img,(WIDTH//2 - 100, HEIGHT//2 - 100))

        font.render_to(screen,(140,300),"Press ENTER to continue",(255,255,0))

        pygame.display.update()
        clock.tick(60)
        continue

    # ✅ movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= 5
    if keys[pygame.K_RIGHT] and player_x < WIDTH-player_w:
        player_x += 5

    # ✅ move star
    game["star_y"] += game["speed"]

    next_letter = game["target"][len(game["progress"])] \
        if len(game["progress"]) < len(game["target"]) else None

    # ✅ MISS LOGIC (FIXED)
    if game["star_y"] > HEIGHT:

        game["star_y"] = -20
        game["star_x"] = random.randint(50, WIDTH-50)

        next_letter = game["target"][len(game["progress"])] \
            if len(game["progress"]) < len(game["target"]) else None

        game["attempts"] += 1

        if next_letter:
            if game["attempts"] >= 5:
                game["letter"] = next_letter
                game["attempts"] = 0
            elif random.random() < 0.5:
                game["letter"] = next_letter
            else:
                game["letter"] = random.choice(string.ascii_uppercase)
        else:
            game["letter"] = random.choice(string.ascii_uppercase)

    # ✅ collision
    if (player_x < game["star_x"] < player_x+player_w and
        player_y < game["star_y"] < player_y+player_h):

        if next_letter and game["letter"] == next_letter:

            game["progress"] += game["letter"]
            score += 1
            game["attempts"] = 0

            if game["progress"] == game["target"]:
                completed_word = game["target"]

                speak_word(game["target"])

                score += 5
                level += 1

                show_image = True   # ✅ trigger image screen

        else:
            lives -= 1

        game["star_y"] = -20
        game["star_x"] = random.randint(50, WIDTH-50)

    # ✅ draw player
    pygame.draw.rect(screen, BLUE,(player_x,player_y,player_w,player_h))

    # ✅ draw star
    pygame.draw.circle(screen,YELLOW,(game["star_x"],game["star_y"]),20)

    # ✅ centered letter
    rect = letter_font.get_rect(game["letter"])
    letter_font.render_to(screen,
        (game["star_x"] - rect.width//2, game["star_y"] - rect.height//2),
        game["letter"], BLACK)

    # ✅ UI
    font.render_to(screen,(10,10),f"Word: {game['target']}",WHITE)
    font.render_to(screen,(10,40),f"Score: {score}",WHITE)
    font.render_to(screen,(10,70),f"Level: {level}",WHITE)
    font.render_to(screen,(10,100),"Lives: "+"❤️"*lives,WHITE)

    if lives <= 0:
        big_font.render_to(screen,(180,150),"GAME OVER",(255,0,0))
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

    pygame.display.update()
    clock.tick(60)