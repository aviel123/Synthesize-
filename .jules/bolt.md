## 2024-05-23 - Signal Generation Optimization
**Learning:** Generating full-duration signal arrays (e.g. 0.5s) for short transient events (e.g. 10ms clicks) is a major waste.
**Action:** Calculate the active duration in samples first, generate/process only that segment, and zero-pad the result to the full buffer length. Be careful with random seeds to maintain reproducibility where possible.
