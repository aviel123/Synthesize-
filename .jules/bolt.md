## 2024-05-22 - [Audio Synthesis Optimization]
**Learning:** In audio synthesis, generating full-duration buffers for short percussive sounds (like kicks/clicks) is extremely wasteful (90%+ silence).
**Action:** Always calculate the active duration based on the amplitude envelope first, generate only the necessary samples, and pad the rest.
