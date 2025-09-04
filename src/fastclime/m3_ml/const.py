from fastclime.m0_storage import DATA_DIR

MODELS_DIR = DATA_DIR / "models"
DEFAULT_SPLIT = dict(test_size=0.2, random_state=42, stratify=True)
TARGETS = {
    "stress_clf": "stress_flag",
    "lamina_reg": "lamina_opt_mm",
}
