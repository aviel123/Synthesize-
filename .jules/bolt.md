## 2024-05-23 - Lazy Signal Generation
**Learning:** Generating full-length arrays for short audio envelopes (e.g., clicks, punches) wastes CPU cycles on silent samples. Generating only the active duration and zero-padding yields significant speedups (~17%).
**Action:** Always check effective signal duration and use slice-based generation + padding for transient sounds.
