import time
import numpy as np
import os
import sys
from generators.kick_generator import TranceKickGenerator

def benchmark():
    # Setup
    seed = 42
    np.random.seed(seed)

    gen = TranceKickGenerator(duration=0.5, sample_rate=44100)

    # Parameters that trigger all components (except smoke for now to keep it simple,
    # but maybe we should include smoke if we optimized it?
    # I am targeting kick components first).
    # Default params: click_level=1.0, drive_db=4.5, etc.

    iterations = 50
    start_time = time.time()

    last_audio = None

    print(f"Running {iterations} iterations...")
    for i in range(iterations):
        # Re-seed every time to ensure identical sequence if we were comparing iteration by iteration,
        # but here we just want deterministic overall run.
        # Actually, if we change code structure, the number of random calls might change?
        # generate_click uses random. If we generate fewer samples, we consume fewer random numbers.
        # This WILL break strict equality comparison if we just rely on "same seed -> same sequence".
        #
        # PROBLEM: Optimizing by generating fewer samples means fewer calls to RNG.
        # This changes the state of RNG for subsequent calls (if any).
        # In `generate_click`, it is the only consumer of RNG in the default path.
        # But if we reduce the number of random samples generated, the actual values might be the same
        # (since `np.random.uniform` produces a sequence), but we are taking a prefix.
        #
        # Wait, `np.random.uniform(size=N)` consumes N random numbers.
        # If I change it to `np.random.uniform(size=M)` where M < N, the numbers I get are the first M of the original N.
        # So the content of the click layer should be identical (prefix).
        #
        # However, if there are multiple calls to random in the sequence, subsequent calls will get different numbers.
        # `TranceKickGenerator.generate` calls:
        # 1. `generate_punch` (deterministic)
        # 2. `generate_body` (deterministic)
        # 3. `generate_click` (uses random)
        #
        # So `generate_click` is the only one.
        # So if I reduce the size request in `generate_click`, I get the same noise for that segment.
        #
        # BUT: `generate_click` does:
        # `noise = np.random.uniform(-1, 1, self.num_samples)`
        #
        # If I change to:
        # `noise = np.random.uniform(-1, 1, active_samples)`
        #
        # The `noise` array will contain the first `active_samples` values of the original sequence.
        # Since I am only using the first `active_samples` anyway (and zeroing the rest),
        # the non-zero part of the output should be IDENTICAL.
        # The zero part is zero.
        #
        # So `np.allclose` should still pass!

        # Reset seed for each iteration to ensure we are testing the exact same generation logic repeatedly
        # and not drifting if I mess up global state (though I shouldn't).
        # Actually, reducing N means we consume fewer stats.
        # If I don't reset seed, the next iteration will start from a different point in RNG stream compared to baseline.
        # So I MUST reset seed inside the loop to guarantee the i-th iteration computes the same signal.
        np.random.seed(seed + i)

        audio = gen.generate(
            click_level=1.0,
            click_decay_ms=10.0,
            drive_db=4.5,
            oversample=1
        )
        last_audio = audio

    end_time = time.time()
    duration = end_time - start_time
    avg_time = duration / iterations * 1000.0

    print(f"Total time: {duration:.4f}s")
    print(f"Average time per kick: {avg_time:.4f}ms")

    baseline_file = "baseline_kick.npy"
    if os.path.exists(baseline_file):
        print("Loading baseline for comparison...")
        baseline_audio = np.load(baseline_file)

        if baseline_audio.shape != last_audio.shape:
             print(f"SHAPE MISMATCH: Baseline {baseline_audio.shape}, Current {last_audio.shape}")
        else:
            # We expect strict equality or very close float tolerance
            # Since we are just truncating generation, it should be exact if logic is perfect.
            # But let's use allclose.
            if np.allclose(baseline_audio, last_audio, atol=1e-7):
                print("✅ Output matches baseline!")
            else:
                max_diff = np.max(np.abs(baseline_audio - last_audio))
                print(f"❌ Output mismatch! Max diff: {max_diff}")
                # debug
                # print("Baseline:", baseline_audio[:10])
                # print("Current: ", last_audio[:10])
    else:
        print(f"Saving baseline to {baseline_file}")
        np.save(baseline_file, last_audio)

if __name__ == "__main__":
    benchmark()
