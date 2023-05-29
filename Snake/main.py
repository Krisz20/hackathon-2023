import random
import os

# Állandók
PLAYABLE_WIDTH = 60
PLAYABLE_HEIGHT = 30

GAME_WIDTH = PLAYABLE_WIDTH + 2
GAME_HEIGHT = PLAYABLE_HEIGHT + 2

SNAKE_CHAR = "@"
FENCE_CHAR = "*"

# Kígyó osztály
class Snake:
    def __init__(self):
        self.x = 0
        self.y = 0

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1

    def move_up(self):
        self.y -= 1

    def move_down(self):
        self.y += 1

# Játék osztály
class SnakeGame:
    def __init__(self):
        self.snake = Snake()
        self.fence = []

    # A kígyó és a kerítés létrehozása
    def setup(self):
        self.place_snake()
        self.create_fence()

    # Elhelyezi a kígyót egy véletlenszerű helyre
    def place_snake(self):
        self.snake.x = random.randint(1, PLAYABLE_WIDTH - 1)
        self.snake.y = random.randint(1, PLAYABLE_HEIGHT - 1)

    # Létrehozza a kerítést
    def create_fence(self):
        for i in range(GAME_HEIGHT):
            self.fence.append((0, i))
            self.fence.append((GAME_WIDTH - 1, i))

        for i in range(GAME_WIDTH):
            self.fence.append((i, 0))
            self.fence.append((i, GAME_HEIGHT - 1))

    # Megrajzolja a játékot
    def draw_game(self):
        # A konzol törlése
        os.system("cls" if os.name == "nt" else "clear") 

        # A játéktér megrajzolása karakterenként
        for y in range(GAME_HEIGHT):
            for x in range(GAME_WIDTH):
                if (x, y) == (self.snake.x, self.snake.y):
                    print(SNAKE_CHAR, end="")
                elif (x, y) in self.fence:
                    print(FENCE_CHAR, end="")
                else:
                    print(" ", end="")
            print()

    def play(self):
        # A játék beállítása és megrajzolása 
        self.setup()
        self.draw_game()

        # A játék fő ciklusa
        while True:
            # A felhasználó utasításának bekérése
            print("Hova?")
            user_input = input()

            # A felhasználó utasítása szerinti cselekvés
            if user_input == "balra":
                self.snake.move_left()
            elif user_input == "jobbra":
                self.snake.move_right()
            elif user_input == "fel":
                self.snake.move_up()
            elif user_input == "le":
                self.snake.move_down()
            elif user_input == "meguntam":
                break
            
            # Ha a kígyó hozzáér a kerítéshez, akkor vége a játéknak
            if (self.snake.x, self.snake.y) in self.fence:
                break
            
            # játék megrajzolása
            self.draw_game()

        # Elköszönés
        print("Most ennyi volt, szép napot!")

# A játék létrehozása és elindítása
if __name__ == "__main__":
    game = SnakeGame()
    game.play()