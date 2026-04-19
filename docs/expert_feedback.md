# Expert Feedback – HeidelFrisch Gym

## Dr. Joyjit Chatterjee (Lead Data Scientist, EPAM UK)
**Date:** 13.04.2026

### Key insights:
1. **Hybrid approach (ML + physics)** – Recommended to capture humidity, vibration, packaging
2. **Validation without real data** – Use published research + simulated data
3. **Industry practice** – Common in CPG and life sciences

### Action items:
- [ ] Add ML correction layer to physics model
- [ ] Research blueberry shelf life papers
- [ ] Add more features (humidity, vibration, packaging type)

---

## Dr. Oscar Hernán Ramírez-Agudelo (Scientist, DLR)
**Date:** 13.04.2026

### Key insights:
1. **Time-above-threshold** – More important than fixed temperature thresholds
2. **Sensitivity analysis** – Test how model responds to input variations
3. **Sensor failure handling** – Imputation with uncertainty, graceful degradation

### Action items:
- [ ] Replace `if temp > 5: spoilage *= 2.5` with hours-above calculation
- [ ] Add `sensitivity_analysis()` function
- [ ] Add confidence scores for missing data
