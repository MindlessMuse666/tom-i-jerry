"""
Модуль аудио-микшера для управления фоновой музыкой и звуковыми эффектами.
Поддерживает полифонию, плавное затухание и управление громкостью.
"""
import pygame
from setting import settings

class Mixer:
    """
    Класс для работы со звуковой подсистемой игры.
    """
    def __init__(self):
        # Инициализация микшера с поддержкой 16 каналов для одновременных звуков
        pygame.mixer.set_num_channels(16)

    def play_sfx(self, sound, loops=0):
        """Проигрывает звуковой эффект на свободном канале."""
        if sound:
            sound.set_volume(settings.sfx_volume)
            # Поиск свободного канала для воспроизведения
            channel = pygame.mixer.find_channel(True)
            if channel:
                channel.play(sound, loops=loops)
                return channel
        return None

    def play_music(self, music_path, loop=-1, fade_ms=500):
        """Загружает и проигрывает фоновую музыку."""
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(settings.music_volume)
        pygame.mixer.music.play(loop, fade_ms=fade_ms)

    def stop_music(self, fade_ms=500):
        """Останавливает музыку с эффектом затухания."""
        pygame.mixer.music.fadeout(fade_ms)

    def stop_all_sfx(self):
        """Мгновенно останавливает все звуковые эффекты на всех каналах."""
        pygame.mixer.stop()

# Глобальный экземпляр микшера
mixer = Mixer()
