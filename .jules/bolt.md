## 2025-02-28 - Active Duration Optimization in TranceKickGenerator
**Learning:** In audio signal generation, applying an envelope that zeroes out most of the signal (e.g., short punch or click layers) over a long buffer (e.g., 1 second) is extremely inefficient. Generating the full sine wave or noise array, filtering it, and then zeroing it wastes CPU and memory allocation time.
**Action:** By generating `t`, `signal`, and `envelope` only for the active non-zero duration and zero-padding the rest of the buffer, we can reduce generation times by ~80-90% for short elements like punch (40ms), click (10ms), and body (300ms) on a 1000ms buffer.

## 2025-02-28 - Testing RNG Functions Output Matching
**Learning:** When optimizing an RNG-dependent method (like `generate_click`) by generating fewer random samples, `np.allclose(orig, opt)` will pass if seeds match at start, but subsequent calls won't match because the optimized version consumed fewer random numbers, leaving the RNG in a different state.
**Action:** While this is acceptable for audio synthesis (the noise is meant to be random anyway), be careful when writing regression tests. Reset the seed *before every* invocation when verifying exact sample equality.
