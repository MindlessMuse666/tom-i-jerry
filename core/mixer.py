import pygame
from setting import settings

class Mixer:
    def __init__(self):
        # Initialize mixer with more channels
        pygame.mixer.set_num_channels(16)

    def play_sfx(self, sound):
        if sound:
            sound.set_volume(settings.sfx_volume)
            # Use pygame's built-in channel management for better reliability
            channel = pygame.mixer.find_channel(True)
            if channel:
                channel.play(sound)

    def play_music(self, music_path, loop=-1, fade_ms=500):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(settings.music_volume)
        pygame.mixer.music.play(loop, fade_ms=fade_ms)

    def stop_music(self, fade_ms=500):
        pygame.mixer.music.fadeout(fade_ms)

# Global mixer instance
mixer = Mixer()
