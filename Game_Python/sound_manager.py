"""
Sound manager for SI3LN Game.
Generates simple procedural SFX so the game works without external audio files.
"""
import math
import array
import pygame


SAMPLE_RATE = 44100
BITS = -16  # signed 16-bit
CHANNELS = 1


def _sine_wave(frequency, duration_ms, volume=0.5):
    """Generate a sine wave buffer."""
    samples = int(SAMPLE_RATE * duration_ms / 1000)
    buf = array.array('h')
    max_amp = int(32767 * volume)
    for i in range(samples):
        t = i / SAMPLE_RATE
        value = int(max_amp * math.sin(2 * math.pi * frequency * t))
        buf.append(value)
    return buf


def _noise_wave(duration_ms, volume=0.5):
    """Generate white noise buffer."""
    import random
    samples = int(SAMPLE_RATE * duration_ms / 1000)
    buf = array.array('h')
    max_amp = int(32767 * volume)
    for _ in range(samples):
        value = random.randint(-max_amp, max_amp)
        buf.append(value)
    return buf


def _sweep(start_freq, end_freq, duration_ms, volume=0.5):
    """Generate a frequency sweep buffer."""
    samples = int(SAMPLE_RATE * duration_ms / 1000)
    buf = array.array('h')
    max_amp = int(32767 * volume)
    for i in range(samples):
        t = i / samples
        freq = start_freq + (end_freq - start_freq) * t
        phase = 2 * math.pi * freq * (i / SAMPLE_RATE)
        # Envelope to avoid clicking
        env = 1.0 - abs(2 * t - 1)
        value = int(max_amp * env * math.sin(phase))
        buf.append(value)
    return buf


class SoundManager:
    """Manages procedural sound effects and music state."""

    def __init__(self, enabled=True, volume=0.5):
        self.enabled = enabled
        self.volume = max(0.0, min(1.0, volume))
        self.sounds = {}
        self._initialized = False
        self._init_mixer()
        self._generate_sounds()

    def _init_mixer(self):
        """Initialize pygame mixer if not already done."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SAMPLE_RATE, size=BITS, channels=CHANNELS)
            self._initialized = bool(pygame.mixer.get_init())
        except Exception as e:
            print(f"Could not initialize audio: {e}")
            self._initialized = False
            self.enabled = False

    def _generate_sounds(self):
        """Pre-generate all procedural sound effects."""
        if not self._initialized:
            return

        sound_defs = {
            "shoot": (_sine_wave(880, 80, 0.4), 80),
            "enemy_shoot": (_sine_wave(440, 80, 0.3), 80),
            "explosion": (_noise_wave(250, 0.5), 250),
            "player_explosion": (_noise_wave(400, 0.6), 400),
            "bonus": (_sweep(600, 1200, 150, 0.4), 150),
            "shield": (_sweep(200, 800, 200, 0.4), 200),
            "mega": (_sweep(400, 1000, 200, 0.5), 200),
            "dash": (_sweep(800, 1600, 150, 0.4), 150),
            "hit": (_noise_wave(80, 0.3), 80),
            "level_win": (_sweep(400, 1200, 400, 0.5), 400),
            "game_over": (_sweep(600, 100, 800, 0.5), 800),
        }

        for name, (buf, max_ms) in sound_defs.items():
            try:
                sound = pygame.mixer.Sound(buffer=buf)
                sound.set_volume(self.volume)
                self.sounds[name] = sound
            except Exception as e:
                print(f"Could not generate sound '{name}': {e}")

    def set_enabled(self, enabled):
        self.enabled = enabled

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)

    def play(self, name):
        """Play a sound effect by name."""
        if not self.enabled or not self._initialized:
            return
        sound = self.sounds.get(name)
        if sound:
            try:
                sound.play()
            except Exception as e:
                print(f"Could not play sound '{name}': {e}")
