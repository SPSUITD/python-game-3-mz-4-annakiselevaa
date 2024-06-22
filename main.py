import arcade
import random

# Константы для настройки окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Eco Game for Kids"

# Константы для игрового процесса
MOVEMENT_SPEED = 5
TRASH_COUNT = 10

# Монолог для начальной истории
MONOLOGUE = [
    "Привет, друг!",
    "Ты в игре 'Eco Game for Kids'!",
    "Помоги девочке собрать мусор в лесу.",
    "Чистый лес - это здоровая планета.",
    "Собери весь мусор, чтобы помочь природе.",
    "Используй стрелки для передвижения.",
    "Нажимай 'Далее', чтобы начать игру. Удачи!"
]

# Список изображений мусора
TRASH_IMAGES = [
    ("plastic_trash.png", "plastic"),
    ("glass_trash.png", "glass"),
    ("paper_trash.png", "paper"),
    ("metal_trash.png", "metal")
]


# Классы для игры
class Trash(arcade.Sprite):
    def __init__(self, image, scale, trash_type):
        super().__init__(image, scale)
        self.trash_type = trash_type


class Player(arcade.Sprite):
    def __init__(self, image, scale):
        super().__init__(image, scale)


class StoryView(arcade.View):
    def __init__(self):
        super().__init__()
        self.monologue_index = 0
        self.background = arcade.load_texture("story_background.png")
        self.player_sprite = arcade.Sprite("player_image1.png", 0.1, center_x=SCREEN_WIDTH // 1.3,
                                           center_y=SCREEN_HEIGHT // 2.4)
        self.next_button = arcade.SpriteSolidColor(200, 50, arcade.color.DARK_GREEN)
        self.next_button.center_x = 150
        self.next_button.center_y = 200

    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_GREEN)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        self.player_sprite.draw()
        self.next_button.draw()

        # Отображение текста монолога без подложки
        arcade.draw_text("Далее", 150, 190, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text(MONOLOGUE[self.monologue_index], 50, 430, arcade.color.BLACK, 18, anchor_x="left", width=500)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.next_button.collides_with_point((x, y)):
            arcade.schedule(self.animate_button, 1 / 60)

    def animate_button(self, delta_time):
        self.next_button.color = arcade.color.DARK_GREEN
        arcade.unschedule(self.animate_button)
        self.monologue_index += 1
        if self.monologue_index >= len(MONOLOGUE):
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_sprite = None
        self.trash_list = None
        self.score = 0
        self.jump_animation = False
        self.jump_timer = 0
        self.start_y = None
        self.jump_speed = 10  # Скорость прыжка

    def setup(self):
        self.player_sprite = Player("player_image.png", 0.05)
        self.player_sprite.center_x = SCREEN_WIDTH // 2
        self.player_sprite.center_y = SCREEN_HEIGHT // 2

        self.trash_list = arcade.SpriteList()
        for _ in range(TRASH_COUNT):
            trash_image, trash_type = random.choice(TRASH_IMAGES)
            trash = Trash(trash_image, 0.1, trash_type)
            trash.center_x = random.randint(0, SCREEN_WIDTH)
            trash.center_y = random.randint(0, SCREEN_HEIGHT)
            self.trash_list.append(trash)

        self.background = arcade.load_texture("forest_background.png")

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        self.player_sprite.draw()
        self.trash_list.draw()
        arcade.draw_text(f"Score: {self.score}", 10, 20, arcade.color.WHITE, 14)

    def on_update(self, delta_time):
        self.trash_list.update()
        self.player_sprite.update()

        trash_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.trash_list)
        for trash in trash_hit_list:
            trash.remove_from_sprite_lists()
            self.score += 1
            self.start_jump_animation()

        if self.jump_animation:
            self.update_jump()

        if len(self.trash_list) == 0:
            self.show_end_screen()

    def start_jump_animation(self):
        self.player_sprite.texture = arcade.load_texture("player_image2.png")
        self.jump_animation = True
        self.jump_timer = 0
        self.start_y = self.player_sprite.center_y

    def update_jump(self):
        if self.jump_timer < 0.25:
            # Прыгаем вверх
            self.player_sprite.center_y += self.jump_speed
        elif self.jump_timer < 0.5:
            # Спускаемся
            self.player_sprite.center_y -= self.jump_speed

        self.jump_timer += 0.012  # Скорость анимации

        if self.jump_timer >= 0.5:
            self.jump_animation = False
            self.player_sprite.texture = arcade.load_texture("player_image.png")
            self.player_sprite.center_y = self.start_y

    def show_end_screen(self):
        end_view = EndView()
        self.window.show_view(end_view)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.UP, arcade.key.DOWN]:
            self.player_sprite.change_y = 0
        elif key in [arcade.key.LEFT, arcade.key.RIGHT]:
            self.player_sprite.change_x = 0



class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.start_button = None
        self.exit_button = None

    def on_show(self):
        self.background = arcade.load_texture("menu_background.png")
        self.start_button = arcade.SpriteSolidColor(200, 50, arcade.color.DARK_GREEN)
        self.start_button.center_x = SCREEN_WIDTH / 2
        self.start_button.center_y = SCREEN_HEIGHT / 2 - 20
        self.exit_button = arcade.SpriteSolidColor(200, 50, arcade.color.DARK_GREEN)
        self.exit_button.center_x = SCREEN_WIDTH / 2
        self.exit_button.center_y = SCREEN_HEIGHT / 2 - 90

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        arcade.draw_text("Eco Game for Kids", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
                         arcade.color.WHITE, font_size=40, anchor_x="center")

        self.start_button.draw()
        arcade.draw_text("Новая игра", self.start_button.center_x, self.start_button.center_y,
                         arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="center")

        self.exit_button.draw()
        arcade.draw_text("Выйти", self.exit_button.center_x, self.exit_button.center_y,
                         arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="center")

    def on_mouse_press(self, x, y, button, modifiers):
        if self.start_button.collides_with_point((x, y)):
            story_view = StoryView()
            self.window.show_view(story_view)
        elif self.exit_button.collides_with_point((x, y)):
            self.window.close()


class EndView(arcade.View):
    def __init__(self):
        super().__init__()
        self.return_button = arcade.SpriteSolidColor(220, 50, arcade.color.DARK_GREEN)
        self.return_button.center_x = 200
        self.return_button.center_y = SCREEN_HEIGHT // 2 - 60
        self.background = arcade.load_texture("story_background.png")
        self.player_sprite = arcade.Sprite("player_image2.png", 0.1)
        self.player_sprite.center_x = SCREEN_WIDTH // 1.25
        self.player_sprite.center_y = SCREEN_HEIGHT // 3

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        arcade.draw_text("Поздравляю! Ты собрал весь мусор и помог нашей планете!", 50, 450,
                         arcade.color.BLACK, 20, anchor_x="left", width=700)
        self.return_button.draw()
        arcade.draw_text("Вернуться в меню", self.return_button.center_x, self.return_button.center_y,
                         arcade.color.WHITE, font_size=18, anchor_x="center", anchor_y="center")
        self.player_sprite.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        menu_view = MenuView()
        self.window.show_view(menu_view)



class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.menu_view = MenuView()
        self.show_view(self.menu_view)

if __name__ == "__main__":
    window = MyGame()
    arcade.run()

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.menu_view = MenuView()
        self.story_view = StoryView()
        self.game_view = GameView()
        self.end_view = EndView()
        self.current_view = None

    def setup(self):
        self.current_view = self.menu_view
        self.show_view(self.current_view)

    def on_draw(self):
        arcade.start_render()
        if self.current_view:
            self.current_view.on_draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.current_view:
            self.current_view.on_mouse_press(x, y, button, modifiers)

    def on_key_press(self, key, modifiers):
        if self.current_view:
            self.current_view.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        if self.current_view:
            self.current_view.on_key_release(key, modifiers)

    def show_story_view(self):
        self.current_view = self.story_view
        self.show_view(self.current_view)

    def show_game_view(self):
        self.game_view.setup()
        self.current_view = self.game_view
        self.show_view(self.current_view)

    def show_end_view(self):
        self.current_view = self.end_view
        self.show_view(self.current_view)


if __name__ == "__main__":
    window = MyGame()
    window.setup()
    arcade.run()
