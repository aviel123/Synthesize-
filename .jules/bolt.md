# Bolt's Journal

## 2024-05-22 - [Project Initialization]
**Learning:** Initialized Bolt's journal for the Euphoria Trance Drum Designer.
**Action:** Will document critical performance learnings here.

## 2024-05-22 - [Clap Generator Optimization]
**Learning:** Generating full-length noise arrays for short transients is wasteful. Limiting generation to the active envelope duration yielded a ~20% speedup.
**Action:** When synthesizing short sounds or envelopes, always calculate the active duration first and slice/generate only what's needed, padding the rest.
