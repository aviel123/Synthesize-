## 2025-02-18 - Numpy Optimization: Active Duration
**Learning:** Generating full-duration arrays for short events (like 10ms clicks in a 500ms buffer) is a major bottleneck (~7x slowdown).
**Action:** Calculate `active_samples` and process only that segment, then zero-pad. Careful with RNG state divergence in stereo generation if using random numbers.
