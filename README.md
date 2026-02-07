# Euphoria Trance Kick Generator (Armin Style)

This project is a Python-based audio synthesis system designed to create professional-grade trance kick drums, specifically modeled after the "Euphoria" style (heavy white noise, aggressive transients, and deep sub) popularized by artists like Armin van Buuren.

The system includes a powerful DSP engine (`kick_generator.py`) and a user-friendly graphical interface (`kick_gui.py`).

## System Overview (תמונת המערכת)

The system operates as a synthesizer that generates audio from scratch using mathematical models (DSP). It does not use samples.

### Key Components:

1.  **Synthesis Engine (`kick_generator.py`)**: The core logic that generates waveforms, applies envelopes, and processes audio effects.
2.  **GUI Application (`kick_gui.py`)**: A Tkinter-based interface allowing visual control over all synthesis parameters.

## Functional Description (פונקציות המערכת)

Here is a detailed breakdown of what the system does:

### 1. Sound Synthesis (Generation)
*   **Punch Layer:** Generates a sine wave that sweeps from high to low frequency (150Hz -> 0Hz) very quickly (20-50ms). This creates the initial "thud" or impact of the kick.
    *   *Controls:* Start Phase (0-360°).
*   **Body Layer:** Generates a stable sine wave at a specific sub frequency (e.g., 55-70Hz) to provide the "weight" and bass of the kick.
    *   *Controls:* Duration, Decay Time, Start Phase.
*   **Click/Noise Layer:** Generates white noise, filters it (High-Pass > 2kHz), and applies a very short envelope (5-15ms). This provides the "snap" or "cut" essential for trance music.
    *   *Unique Feature:* **Stereo Width** control allows widening this layer for a massive, airy top-end.
*   **Oversampling:** The engine can run at 2x sample rate (88.2kHz or 96kHz) to reduce aliasing distortion when using heavy saturation.

### 2. Audio Effects (FX Chain)
*   **Saturation (Drive):** Applies soft-clipping (tanh) distortion to add harmonics and "glue" the layers together.
    *   *Controls:* Drive (dB).
*   **Compression:** A custom-designed compressor with fast attack (3ms) and medium release (150ms) to tighten the sound and emphasize the transient.
*   **Parametric EQ:** precision sculpting of the frequency spectrum:
    *   *Cut:* Removes mud below 30Hz.
    *   *Boost:* Adds weight at 70Hz.
    *   *Dip:* Removes "boxiness" at 300Hz.
    *   *High Boost:* Adds "air" and presence at 4kHz+ (Euphoria style).
*   **Reverb:** Adds a short, dense reverb tail to the kick, typical of big-room trance.
*   **Delay:** Adds a stereo ping-pong delay effect for rhythmic texture.
*   **Master Limiter:** A lookahead limiter that maximizes the volume (loudness) without allowing the signal to clip (distort digitally).

### 3. Bassline & Sidechain Integration (VST-like Features)
*   **Bassline Generator:** Can generate a synchronized offbeat bassline (138 BPM) to accompany the kick.
*   **Sidechain Compression:** Automatically "ducks" (lowers) the volume of the bassline whenever the kick hits, creating the pumping rhythm characteristic of trance.
*   **Trigger Export:** Can export a separate "Sidechain Trigger" audio file (short click) to be used in DAWs for routing sidechain signals to other VSTs.

## Usage Guide

### Running the GUI
To open the visual interface:
```bash
python3 main.py
```

### GUI Controls
The interface is organized into three tabs:
1.  **Synthesis:**
    *   *Quality Mode:* Choose between Standard (1x) and High (2x Oversampling).
    *   *Duration:* Length of the kick.
    *   *Phase:* Adjusts the starting phase alignment of the sub/punch.
    *   *Click/Noise:* Adjust level, decay length, and stereo width.
2.  **Effects:**
    *   *Drive:* Amount of saturation/distortion.
    *   *Reverb/Delay:* Amount of spatial effects.
3.  **Bassline & Export:**
    *   *Generate Bassline Loop:* Check this to create a 4-beat loop with kick + bass.
    *   *Bass Frequency:* Pitch of the bassline.
    *   *Sidechain Depth:* How much the bass volume drops when the kick hits.
    *   *Export Trigger:* Button to save `sidechain_trigger.wav`.

### New Features (Clap & Combo)
1.  **Clap Generator Tab:**
    *   Create custom trance claps with adjustable transient, tail, reflections, and spacing.
    *   Includes Stereo Width control for wide claps.
2.  **Pattern/Combo Tab:**
    *   Generates a full 4-bar loop (138 BPM).
    *   Automatically layers your designed Kick and Clap.
    *   Controls for Swing, Kick Volume, and Clap Volume.

### Command Line Interface (CLI)
You can also run the generator without the GUI using the module directly:
```bash
python3 -m generators.kick_generator --output my_kick.wav --drive 6.0 --click-level 1.5
```
