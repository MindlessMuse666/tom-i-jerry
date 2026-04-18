import pygame
import os

class ResourceManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}

    def get_image(self, path):
        if path not in self.images:
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.images[path] = img
            else:
                print(f"Warning: Image not found at {path}")
                # Create a placeholder surface if image is missing
                placeholder = pygame.Surface((32, 32))
                placeholder.fill((255, 0, 255)) # Magenta
                self.images[path] = placeholder
        return self.images[path]

    def get_sound(self, path):
        if path not in self.sounds:
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                from setting import settings
                sound.set_volume(settings.sfx_volume)
                self.sounds[path] = sound
            else:
                print(f"Warning: Sound not found at {path}")
                return None
        return self.sounds[path]

    def set_sfx_volume(self, volume):
        for sound in self.sounds.values():
            sound.set_volume(volume)

    def get_font(self, path, size):
        key = (path, size)
        if key not in self.fonts:
            if os.path.exists(path):
                self.fonts[key] = pygame.font.Font(path, size)
            else:
                print(f"Warning: Font not found at {path}")
                self.fonts[key] = pygame.font.SysFont("Arial", size)
        return self.fonts[key]

# Global resource manager instance
resource_manager = ResourceManager()
