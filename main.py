from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.graphics import Rectangle, Color, RoundedRectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
import random
import os

Window.size = (480, 720)
Window.clearcolor = (0.85, 0.93, 1, 1)

# Get the base path for resources
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
RECS_PATH = os.path.join(BASE_PATH, "recs")


def clamp(val, lo, hi):
    return max(lo, min(val, hi))


class Bird(Widget):
    velocity_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (48, 48)
        with self.canvas:
            self.bird_img = Rectangle(source=os.path.join(RECS_PATH, "character.jpg"), pos=self.pos, size=self.size)
        self.bind(pos=self._update_rects)

    def _update_rects(self, *args):
        self.bird_img.pos = self.pos

    def flap(self, power):
        self.velocity_y = power

    def update(self, dt, gravity):
        self.velocity_y += gravity * dt
        self.y += self.velocity_y * dt


class Pipe(Widget):
    def __init__(self, gap_y, gap_size, **kwargs):
        super().__init__(**kwargs)
        self.gap_y = gap_y
        self.gap_size = gap_size
        self.width = 70
        self.scored = False
        with self.canvas:
            self.pipe_img_top = Rectangle(source=os.path.join(RECS_PATH, "pipes.jpeg"), 
                                          pos=(self.x, self.gap_y + self.gap_size / 2),
                                          size=(self.width, Window.height - (self.gap_y + self.gap_size / 2)))
            self.pipe_img_bottom = Rectangle(source=os.path.join(RECS_PATH, "pipes.jpeg"), 
                                             pos=(self.x, 0),
                                             size=(self.width, self.gap_y - self.gap_size / 2))
        self.bind(pos=self._sync)

    def _sync(self, *args):
        self.pipe_img_top.pos = (self.x, self.gap_y + self.gap_size / 2)
        self.pipe_img_bottom.pos = (self.x, 0)

    def move(self, speed, dt):
        self.x -= speed * dt

    def collides_with(self, bird: Bird):
        bird_box = (bird.x, bird.y, bird.width, bird.height)
        in_x = bird_box[0] + bird_box[2] > self.x and bird_box[0] < self.x + self.width
        hit_top = in_x and (bird_box[1] + bird_box[3] > self.gap_y + self.gap_size / 2)
        hit_bottom = in_x and (bird_box[1] < self.gap_y - self.gap_size / 2)
        return hit_top or hit_bottom


class Ground(Widget):
    def __init__(self, height=70, **kwargs):
        super().__init__(**kwargs)
        self.height_val = height
        with self.canvas:
            self.ground_img = Rectangle(source=os.path.join(RECS_PATH, "background.jpeg"), 
                                        pos=(0, 0), size=(Window.width, height))


class HUD(BoxLayout):
    score_text = StringProperty("Score: 0")
    best_text = StringProperty("Best: 0")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (None, None)
        self.height = 56
        self.padding = [12, 8]
        self.spacing = 12
        self.score_label = Label(text=self.score_text, font_size=22, bold=True, color=(0, 0, 0, 1),
                                 size_hint=(None, 1))
        self.best_label = Label(text=self.best_text, font_size=18, bold=True, color=(0, 0, 0, 0.8),
                                size_hint=(None, 1))
        self.add_widget(self.score_label)
        self.add_widget(self.best_label)
        self.bind(score_text=lambda *_: self._refresh(),
                  best_text=lambda *_: self._refresh())
        self._refresh()

    def _refresh(self):
        self.score_label.text = self.score_text
        self.best_label.text = self.best_text
        self.score_label.texture_update()
        self.best_label.texture_update()
        self.width = self.padding[0]*2 + self.spacing + self.score_label.texture_size[0] + self.best_label.texture_size[0]
        self.score_label.width = self.score_label.texture_size[0]
        self.best_label.width = self.best_label.texture_size[0]


class Overlay(AnchorLayout):
    def __init__(self, title, button_text, button_cb, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.anchor_x = "center"
        self.anchor_y = "center"
        self.padding = 24

        box = BoxLayout(orientation="vertical", spacing=12, size_hint=(0.8, None))
        box.bind(minimum_height=box.setter("height"))
        with box.canvas.before:
            Color(1, 1, 1, 0.92)
            self.bg = RoundedRectangle(pos=(0, 0), size=(0, 0), radius=[16])
        box.bind(pos=self._update_bg, size=self._update_bg)

        self.title_lbl = Label(text=title, font_size=32, bold=True, color=(0, 0, 0, 1),
                               size_hint=(1, None), height=60, halign="center", valign="middle")
        self.title_lbl.bind(size=lambda *args: self.title_lbl.setter("text_size")(self.title_lbl, self.title_lbl.size))

        btn = Button(text=button_text, size_hint=(1, None), height=54, font_size=20)
        btn.bind(on_release=button_cb)

        box.add_widget(self.title_lbl)
        box.add_widget(btn)
        self.add_widget(box)

    def _update_bg(self, instance, *args):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    def set_title(self, text):
        self.title_lbl.text = text


class FlappyBirdGame(Widget):
    game_over = BooleanProperty(False)
    started = BooleanProperty(False)
    score = NumericProperty(0)
    best = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gravity = -1400
        self.jump_velocity = 520
        self.pipe_speed = 220
        self.pipe_distance = 240
        self.gap_size = 180
        self.spawn_timer = 0
        self.spawn_interval = 1.35

        with self.canvas.before:
            self.bg_img = Rectangle(source=os.path.join(RECS_PATH, "background.jpeg"), 
                                    pos=(0, 0), size=Window.size)

        self.ground = Ground(height=80)
        self.bird = Bird(pos=(100, Window.height * 0.55))
        self.pipes = []

        self.hud = HUD()
        self.end_overlay = Overlay("Game Over", "Play Again", self.restart_game)
        self.end_overlay.opacity = 0
        self.end_overlay.disabled = True

        # Load background music with better error handling
        audio_path = os.path.join(RECS_PATH, "audio.mp3")
        if os.path.exists(audio_path):
            self.background_music = SoundLoader.load(audio_path)
        else:
            print(f"Warning: Audio file not found at {audio_path}")
            self.background_music = None
        self.audio_loop_event = None

        self.add_widget(self.bird)
        self.add_widget(self.ground)
        self.add_widget(self.hud)
        self.add_widget(self.end_overlay)

        self.bind(size=self._on_resize)
        Window.bind(on_resize=lambda *args: self._on_resize())

        Clock.schedule_interval(self.update, 1 / 60)

    def _on_resize(self, *args):
        self.bg_img.size = self.size
        self.ground.ground_img.size = (self.width, self.ground.height_val)
        self.hud.pos = (12, self.height - self.hud.height - 12)

    def reset(self):
        for p in self.pipes:
            self.remove_widget(p)
        self.pipes = []
        self.spawn_timer = 0
        self.score = 0
        self.game_over = False
        self.started = False
        self.bird.pos = (100, Window.height * 0.55)
        self.bird.velocity_y = 0
        self.hud.score_text = f"Score: {self.score}"
        self.end_overlay.opacity = 0
        self.end_overlay.disabled = True
        
        # Stop and restart audio
        if self.background_music:
            self.background_music.stop()
            if self.audio_loop_event:
                self.audio_loop_event.cancel()
                self.audio_loop_event = None

    def start_game(self, *args):
        self.started = True
        self.end_overlay.opacity = 0
        self.end_overlay.disabled = True
        
        # Play background music when game starts
        if self.background_music and not self.background_music.state == 'play':
            self.background_music.play()
            # Schedule audio looping
            if self.audio_loop_event:
                self.audio_loop_event.cancel()
            self.audio_loop_event = Clock.schedule_once(self._check_audio_loop, self.background_music.length)
        
        if not self.pipes:
            self.spawn_pipe(initial=True)

    def restart_game(self, *args):
        self.reset()

    def _check_audio_loop(self, dt):
        """Check if audio ended and loop it if game is still playing"""
        if self.started and not self.game_over and self.background_music:
            self.background_music.play()
            self.audio_loop_event = Clock.schedule_once(self._check_audio_loop, self.background_music.length)

    def on_touch_down(self, touch):
        if not self.started:
            self.start_game()
            self.bird.flap(self.jump_velocity)
            return True
        if self.game_over:
            self.restart_game()
            return True
        self.bird.flap(self.jump_velocity)
        return True

    def spawn_pipe(self, initial=False):
        gap_margin = 160
        gap_y = random.randint(gap_margin, Window.height - gap_margin)
        pipe = Pipe(gap_y, self.gap_size)
        pipe.x = Window.width
        pipe.y = 0
        self.pipes.append(pipe)
        self.add_widget(pipe, index=0)
        if initial and len(self.pipes) == 2:
            pipe.x += self.pipe_distance

    def update(self, dt):
        if not self.started or self.game_over:
            return

        self.bird.update(dt, self.gravity)
        self.bird.y = clamp(self.bird.y, self.ground.height, Window.height - self.bird.height)

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_pipe()

        for pipe in self.pipes[:]:
            pipe.move(self.pipe_speed, dt)
            if pipe.collides_with(self.bird):
                self.trigger_game_over()
                return
            if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.score += 1
                self.hud.score_text = f"Score: {self.score}"
            if pipe.x + pipe.width < -10:
                self.remove_widget(pipe)
                self.pipes.remove(pipe)

        if self.bird.y <= self.ground.height or self.bird.top >= Window.height:
            self.trigger_game_over()

    def trigger_game_over(self):
        self.game_over = True
        self.best = max(self.best, self.score)
        self.hud.best_text = f"Best: {self.best}"
        self.end_overlay.set_title(f"Game Over\nScore: {self.score}")
        self.end_overlay.opacity = 1
        self.end_overlay.disabled = False
        
        # Stop music on game over
        if self.background_music:
            self.background_music.stop()
        if self.audio_loop_event:
            self.audio_loop_event.cancel()
            self.audio_loop_event = None


class FlappyBirdApp(App):
    def build(self):
        root = FlappyBirdGame()
        root.reset()
        return root


if __name__ == "__main__":
    FlappyBirdApp().run()