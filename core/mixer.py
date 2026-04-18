import pygame
from setting import settings

class Mixer:
    def __init__(self):
        self.channels = []
        for i in range(8): # 8 channels for polyphony
            self.channels.append(pygame.mixer.Channel(i))

    def play_sfx(self, sound):
        if sound:
            sound.set_volume(settings.sfx_volume)
            # Find an idle channel
            for channel in self.channels:
                if not channel.get_busy():
                    channel.play(sound)
                    return
            # If all busy, just play on first
            self.channels[0].play(sound)

    def play_music(self, music_path, loop=-1, fade_ms=500):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(settings.music_volume)
        pygame.mixer.music.play(loop, fade_ms=fade_ms)

    def stop_music(self, fade_ms=500):
        pygame.mixer.music.fadeout(fade_ms)

# Global mixer instance
mixer = Mixer()
