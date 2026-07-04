# Standards & Compliance Posture — an honest statement

Scryer is engineered *toward* defense-grade needs, and this document states
plainly what is implemented versus what formal military acceptance still requires.
We do **not** claim the software "meets all military requirements" — that is a
determination made by a sponsoring authority through a formal process, not by a
vendor or a README.

## Implemented (verifiable in-repo)

- **Controllable false-alarm rate.** Detection uses CA-CFAR with a threshold that
  can be set directly or derived from a target probability of false alarm
  (`pfa_to_k`) — the operating point is an explicit, defensible parameter.
- **ROC characterization.** `bench/` sweeps the threshold and reports detection
  probability (Pd) versus false alarms, and confirms Pd is monotonic in threshold.
- **Sensitivity / SNR management.** SNR frame-stacking recovers targets below
  single-frame detectability; temporal background subtraction handles clutter.
- **Reproducibility.** Deterministic algorithms and fixed-seed synthetic data;
  identical inputs yield identical outputs (evidentiary reproducibility).
- **Supply-chain minimalism.** Zero third-party dependencies (Python stdlib only),
  so there is nothing external to vet; runs fully offline / air-gapped.
- **Interoperability.** Standards-based, machine-readable outputs (GeoJSON tracks
  and heatmaps); Cognis Lattice adds STIX 2.1 and MISP.
- **Ethical scope.** Detection and monitoring only; non-kinetic; leads require
  analyst/operator corroboration before tasking.

## NOT yet done — required for formal military acceptance

- Independent **Test & Evaluation** against government reference data and a
  defined operational requirements document.
- **Authorization to Operate (ATO)** / RMF accreditation (NIST 800-53 controls,
  security control assessment) for any deployment enclave.
- Conformance testing to applicable **MOSA / interface standards** (e.g. MISB/
  STANAG for FMV metadata, OMS/UCI where relevant) with real sensor feeds.
- Validation on **real imagery/sensor data** (this repo is characterized on
  synthetic ground truth; fielded performance will differ and must be measured).
- Human-factors, safety, and cyber hardening reviews per the sponsoring program.

## Summary

The code is robust, tested, characterized, and reproducible — a credible TRL-5/6
prototype. Formal "military requirement" compliance is achieved *with* a sponsor
through the processes above, and this repository is built to make that path
short and honest.
