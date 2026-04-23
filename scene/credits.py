import pygame
import os
import cv2
import numpy as np
from moviepy import *
from scene.base import Scene
from ui.button import Button
from constant import DEFAULT_FONT, LOGICAL_WIDTH, LOGICAL_HEIGHT, ASSET_DIR
from core.resource import resource_manager
from core.mixer import mixer

class CreditsScene(Scene):
    """
    Сцена титров.
    Отображает текст "Титры" с эффектом затухания, а затем запускает финальное видео.
    """
    def __init__(self, game):
        """
        Инициализация сцены титров.

        Args:
            game: Объект игры.
        """
        super().__init__(game)
        self.font_large = resource_manager.get_font(DEFAULT_FONT, 72)
        self.text_alpha = 0
        self.fade_in = True
        self.fade_timer = 0
        self.show_video = False
        
        # Захват видео через OpenCV
        self.cap = None
        self.fps = 0
        self.start_time = 0
        
        # Черный фон
        self.bg = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
        self.bg.fill((0, 0, 0))
        
        # Текст титров
        self.text_surf = self.font_large.render("Титры", True, (255, 255, 255))
        self.text_rect = self.text_surf.get_rect(center=(LOGICAL_WIDTH // 2, LOGICAL_HEIGHT // 2))
        
        self.video_path = os.path.join(ASSET_DIR, "other", "初音ミク_Ievan_polkka.mp4")
        
        center_x = LOGICAL_WIDTH // 2
        self.buttons = [
            Button(center_x, 650, "Меню", self.go_to_menu, game=self.game)
        ]

    def enter(self, **kwargs):
        """Подготовка сцены перед показом."""
        self.text_alpha = 0
        self.fade_in = True
        self.fade_timer = 0
        self.show_video = False
        if self.cap:
            self.cap.release()
            self.cap = None
        mixer.stop_music()
        mixer.stop_all_sfx()

    def start_video(self):
        """Запуск воспроизведения видео и аудио."""
        try:
            self.cap = cv2.VideoCapture(self.video_path)
            if not self.cap.isOpened():
                raise Exception("Не удалось открыть видеофайл")
            
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            if self.fps <= 0: self.fps = 30 # Запасной вариант
            
            # Извлечение и запуск аудио через MoviePy (кроссплатформенно)
            try:
                from moviepy import VideoFileClip
                clip = VideoFileClip(self.video_path)
                # Создание временного mp3 для проигрывания через pygame.mixer.music
                temp_audio = os.path.join("asset", "other", "temp_credits_audio.mp3")
                if not os.path.exists(temp_audio):
                    clip.audio.write_audiofile(temp_audio, logger=None)
                
                pygame.mixer.music.load(temp_audio)
                pygame.mixer.music.play()
            except Exception as audio_e:
                print(f"Ошибка аудио Moviepy: {audio_e}")
                # Попытка прямого воспроизведения, если аудиодорожка поддерживается
                try:
                    pygame.mixer.music.load(self.video_path)
                    pygame.mixer.music.play()
                except:
                    print("Воспроизведение видео без звука")
                
            self.start_time = pygame.time.get_ticks()
            self.show_video = True
            
        except Exception as e:
            print(f"Ошибка видео: {e}")
            self.go_to_menu()

    def go_to_menu(self):
        """Остановка видео и возврат в главное меню."""
        if self.cap:
            self.cap.release()
            self.cap = None
        pygame.mixer.music.stop()
        self.game.state_machine.set_state("MENU")

    def update(self, dt: float):
        """
        Обновление состояния сцены.

        Args:
            dt: Дельта времени.
        """
        if not self.show_video:
            # Логика появления и затухания текста
            if self.fade_in:
                self.text_alpha += 128 * dt
                if self.text_alpha >= 255:
                    self.text_alpha = 255
                    self.fade_timer += dt
                    if self.fade_timer >= 2.0:
                        self.fade_in = False
            else:
                self.text_alpha -= 128 * dt
                if self.text_alpha <= 0:
                    self.text_alpha = 0
                    self.start_video()
        
        super().handle_events(pygame.event.get())

    def draw(self, screen: pygame.Surface):
        """
        Отрисовка кадра видео или текста.

        Args:
            screen: Поверхность для отрисовки.
        """
        screen.blit(self.bg, (0, 0))
        
        if not self.show_video:
            temp_surf = self.text_surf.copy()
            temp_surf.set_alpha(int(self.text_alpha))
            screen.blit(temp_surf, self.text_rect)
        else:
            if self.cap and self.cap.isOpened():
                # Логика синхронизации: расчет нужного кадра на основе времени звука
                current_time = (pygame.time.get_ticks() - self.start_time) / 1000.0
                target_frame = int(current_time * self.fps)
                
                # Переход к нужному кадру для поддержания синхронизации
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
                
                ret, frame = self.cap.read()
                if ret:
                    # Конвертация OpenCV BGR в Pygame RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Транспонирование для корректного отображения в Pygame
                    frame = np.rot90(frame)
                    frame = np.flipud(frame)
                    
                    video_surf = pygame.surfarray.make_surface(frame)
                    # Масштабирование под размер экрана
                    video_surf = pygame.transform.scale(video_surf, (LOGICAL_WIDTH, LOGICAL_HEIGHT))
                    screen.blit(video_surf, (0, 0))
                else:
                    # Видео закончено
                    pass
            
            for button in self.buttons:
                button.draw(screen)

