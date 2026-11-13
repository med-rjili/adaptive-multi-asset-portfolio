# Reproducible research outputs

This directory contains metrics and provenance generated from actual historical
ETF adjusted-close observations when the research workflow runs successfully.

No performance chart or metric is included as a precomputed empirical result
until a real-data run has completed. Inspect `data_provenance.json` for the
snapshot URL, download date, SHA-256 checksum and covered dates.

**Interpretation:** close-to-close adjusted-price returns are a research proxy.
The execution model assumes fills at the signal close, which cannot be guaranteed.
Transaction costs are simplified; historical results are not forecasts.
