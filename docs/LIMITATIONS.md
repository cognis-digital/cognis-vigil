# Limitations & Responsible Use

- **Detection/monitoring only.** Scryer produces confidence-scored leads
  for interdiction by law-enforcement partners. It is not a targeting,
  weapons-cueing, or kinetic capability, and must not be used as one.
- **Synthetic benchmarks.** Metrics use planted synthetic tracks; they measure
  fusion-algorithm correctness, not fielded sensor accuracy. Real ISR data has
  dropouts, false tracks, and measurement error that will lower performance.
- **Simple tracker.** The greedy nearest-neighbor association is a baseline; it
  can split/merge tracks under dense traffic or long gaps. A production system
  would add motion models (e.g. Kalman) and multi-hypothesis tracking.
- **Illustrative cost figures.** Coverage and cost-per-hour inputs are examples;
  operational planning requires validated platform data.
- **A "dark" contact is a lead, not a conclusion.** Absence of AIS has lawful
  explanations; corroborate before acting.

Use only within your lawful authority (LICENSE §9, NOTICE).
