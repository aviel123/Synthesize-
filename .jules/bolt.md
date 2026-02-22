## 2024-05-23 - Signal Generation Anti-Pattern
**Learning:** The generator functions (`generate_click`, `generate_body`, etc.) generate signals for the full duration (e.g., 0.5s) even when the envelope decays to zero much earlier (e.g., 10ms). This wastes >90% of CPU/Memory on silence.
**Action:** For all transient generators, calculate `active_samples` based on decay time and generate only the required segment, zero-padding the rest.
