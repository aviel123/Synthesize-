## 2025-02-12 - Kick Generator Active Duration Optimization
**Learning:** Audio synthesis buffers often contain long tails of zeros (e.g., after envelope decay). Generating and processing signals for the full buffer duration when only a small fraction is active is wasteful.
**Action:** Calculate the active duration based on envelope decay times and generate signals only for that duration, then pad with zeros. This reduces computation in the synthesis stage significantly (e.g., ~10% overall speedup including effects).
