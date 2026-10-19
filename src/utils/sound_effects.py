#!/usr/bin/env python3
"""
Sound Effects Generator for ViralShorts Factory
Creates professional sound effects: whoosh, tick, ding, dramatic hit
"""

import os
import math
import struct
import wave
from pathlib import Path

# Output directory
SFX_DIR = Path(__file__).parent / "assets" / "sfx"
SFX_DIR.mkdir(parents=True, exist_ok=True)


def create_sine_wave(frequency: float, duration: float, sample_rate: int = 44100,
                     amplitude: float = 0.5, fade_in: float = 0, fade_out: float = 0) -> list:
    """Generate a sine wave with optional fade."""
    samples = []
    n_samples = int(sample_rate * duration)
    fade_in_samples = int(sample_rate * fade_in)
    fade_out_samples = int(sample_rate * fade_out)
    
    for i in range(n_samples):
        # Base sine wave
        t = i / sample_rate
        value = amplitude * math.sin(2 * math.pi * frequency * t)
        
        # Apply fade in
        if i < fade_in_samples and fade_in_samples > 0:
            value *= i / fade_in_samples
        
        # Apply fade out
        if i > n_samples - fade_out_samples and fade_out_samples > 0:
            remaining = n_samples - i
            value *= remaining / fade_out_samples
        
        samples.append(value)
    
    return samples


def create_noise(duration: float, sample_rate: int = 44100, amplitude: float = 0.3) -> list:
    """Generate white noise."""
    import random
    n_samples = int(sample_rate * duration)
    return [amplitude * (random.random() * 2 - 1) for _ in range(n_samples)]


def save_wav(samples: list, filepath: str, sample_rate: int = 44100):
    """Save samples to WAV file."""
    # Normalize and convert to 16-bit
    max_val = max(abs(min(samples)), abs(max(samples))) if samples else 1
    if max_val == 0:
        max_val = 1
    
    normalized = [int(s / max_val * 32767 * 0.9) for s in samples]
    
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for sample in normalized:
            wav_file.writeframes(struct.pack('<h', sample))


def generate_whoosh_sfx(output_path: str = None) -> str:
    """Generate a swoosh/whoosh transition sound."""
    if output_path is None:
        output_path = str(SFX_DIR / "whoosh.wav")
    
    if os.path.exists(output_path):
        return output_path
    
    sample_rate = 44100
    duration = 0.4
    samples = []
    
    # Frequency sweep from high to low with noise
    n_samples = int(sample_rate * duration)
    for i in range(n_samples):
        t = i / sample_rate
        progress = i / n_samples
        
        # Frequency sweep
        freq = 3000 * (1 - progress) + 200 * progress
        
        # Envelope
        envelope = math.sin(math.pi * progress)
        
        # Add some noise for texture
        import random
        noise = random.random() * 0.3 - 0.15
        
        # Combine
        value = envelope * 0.5 * (math.sin(2 * math.pi * freq * t) + noise)
        samples.append(value)
    
    save_wav(samples, output_path, sample_rate)
    print(f"   ✅ Generated whoosh SFX: {output_path}")
    return output_path


def generate_tick_sfx(output_path: str = None) -> str:
    """Generate a clock tick sound for countdown."""
    if output_path is None:
        output_path = str(SFX_DIR / "tick.wav")
    
    if os.path.exists(output_path):
        return output_path
    
    sample_rate = 44100
    duration = 0.1
    samples = []
    
    n_samples = int(sample_rate * duration)
    for i in range(n_samples):
        t = i / sample_rate
        progress = i / n_samples
        
        # Sharp attack, quick decay
        envelope = math.exp(-progress * 20)
        
        # Mix of frequencies for "tick" character
        value = envelope * 0.6 * (
            0.5 * math.sin(2 * math.pi * 1200 * t) +
            0.3 * math.sin(2 * math.pi * 2400 * t) +
            0.2 * math.sin(2 * math.pi * 800 * t)
        )
        samples.append(value)
    
    save_wav(samples, output_path, sample_rate)
    print(f"   ✅ Generated tick SFX: {output_path}")
    return output_path


def generate_ding_sfx(output_path: str = None) -> str:
    """Generate a pleasant 'ding' reveal sound."""
    if output_path is None:
        output_path = str(SFX_DIR / "ding.wav")
    
    if os.path.exists(output_path):
        return output_path
    
    sample_rate = 44100
    duration = 0.8
    samples = []
    
    n_samples = int(sample_rate * duration)
    for i in range(n_samples):
        t = i / sample_rate
        progress = i / n_samples
        
        # Bell-like decay
        envelope = math.exp(-progress * 4)
        
        # Harmonics for a bell sound
        value = envelope * 0.5 * (
            0.4 * math.sin(2 * math.pi * 880 * t) +    # A5
            0.3 * math.sin(2 * math.pi * 1320 * t) +   # E6
            0.2 * math.sin(2 * math.pi * 1760 * t) +   # A6
            0.1 * math.sin(2 * math.pi * 2640 * t)     # E7
        )
        samples.append(value)
    
    save_wav(samples, output_path, sample_rate)
    print(f"   ✅ Generated ding SFX: {output_path}")
    return output_path


def generate_dramatic_hit_sfx(output_path: str = None) -> str:
    """Generate a dramatic impact/hit for hook reveal."""
    if output_path is None:
        output_path = str(SFX_DIR / "hit.wav")
    
    if os.path.exists(output_path):
        return output_path
    
    sample_rate = 44100
    duration = 0.5
    samples = []
    
    n_samples = int(sample_rate * duration)
    for i in range(n_samples):
        t = i / sample_rate
        progress = i / n_samples
        
        # Sharp attack, medium decay
        envelope = math.exp(-progress * 8)
        
        # Low frequency hit with harmonics
        import random
        noise = random.random() * 0.2 - 0.1 if i < sample_rate * 0.05 else 0
        
        value = envelope * 0.7 * (
            0.5 * math.sin(2 * math.pi * 80 * t) +
            0.3 * math.sin(2 * math.pi * 160 * t) +
            0.2 * math.sin(2 * math.pi * 240 * t) +
            noise
        )
        samples.append(value)
    
    save_wav(samples, output_path, sample_rate)
    print(f"   ✅ Generated hit SFX: {output_path}")
    return output_path


def get_all_sfx() -> dict:
    """Generate all SFX and return paths."""
    return {
        'whoosh': generate_whoosh_sfx(),
        'tick': generate_tick_sfx(),
        'ding': generate_ding_sfx(),
        'hit': generate_dramatic_hit_sfx()
    }


if __name__ == "__main__":
    print("🔊 Generating sound effects...")
    sfx = get_all_sfx()
    print("\n✅ All SFX generated:")
    for name, path in sfx.items():
        print(f"   {name}: {path}")









