# Data Governance Project

## Phase 1 (Current)

Data pipeline converted from Jupyter notebooks to standalone Python scripts.

### Scripts

| Script | Purpose |
|--------|---------|
| `load_data.py` | Downloads NYC restaurant inspections dataset via kagglehub |
| `clean_data.py` | Cleans raw data with transformations and validations |
| `profile_data.py` | Generates ydata-profiling report |
| `validate_data.py` | Validates both raw and cleaned datasets |

### Missing

- Visualization (Phase 2)

### Usage

```bash
python scripts/load_data.py
python scripts/clean_data.py
python scripts/profile_data.py
python scripts/validate_data.py
```

All scripts handle missing files gracefully with warnings (not errors).