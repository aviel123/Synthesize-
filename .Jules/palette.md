## 2025-02-18 - Tooltips for Sliders
**Learning:** Adding tooltips to unlabeled or technically dense sliders (like "Phase" or "Drive") significantly reduces cognitive load for non-expert users.
**Action:** Always wrap `ttk.Scale` creation in a helper that supports an optional `tooltip_text` parameter.
