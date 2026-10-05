import json
from pathlib import Path

import joblib
import numpy as np

from config.settings import get_settings
from population_model.bp.network import BPNeuralNetwork
from population_model.woa.optimizer import whale_optimization
from rag.schemas.earthquake_scenario import EarthquakeScenario


FEATURE_ORDER = ["magnitude", "depth_km", "population_density"]


class PopulationPredictor:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.model_path = Path(self.settings.woa_bp_model_path)
        self.last_uncertainty: str | None = None
        self._artifact: dict | None = None
        self._load()

    def _load(self) -> None:
        if self.model_path.exists():
            self._artifact = joblib.load(self.model_path)

    def predict(self, scenario: EarthquakeScenario) -> dict:
        pop = scenario.population
        if pop.population_status == "reported" and pop.affected_population is not None:
            return {
                "status": "reported",
                "value": pop.affected_population,
                "source": pop.population_source or "user_reported",
            }
        if self._artifact is None:
            self.last_uncertainty = "WOA-BP model not trained; training data not configured."
            return {"status": "unknown", "value": None, "source": "not_trained"}

        features = self._vectorize(scenario)
        if features is None:
            self.last_uncertainty = "Missing required features for WOA-BP inference."
            return {"status": "unknown", "value": None, "source": "missing_features"}

        net: BPNeuralNetwork = self._artifact["model"]
        x = np.array([features], dtype=float)
        if "x_mean" in self._artifact:
            x = (x - self._artifact["x_mean"]) / self._artifact["x_std"]
        pred_norm = float(net.forward(x)[0, 0])
        if "y_mean" in self._artifact:
            pred = pred_norm * self._artifact["y_std"] + self._artifact["y_mean"]
        else:
            pred = pred_norm
        self.last_uncertainty = self._artifact.get("metrics", {}).get("note", "model_estimate")
        return {
            "status": "woa_bp_estimated",
            "value": max(0, int(round(pred))),
            "source": f"WOA-BP ({self._artifact.get('training_dataset', 'unknown')})",
            "model_version": self._artifact.get("model_version"),
            "features_used": self._artifact.get("features_used"),
        }

    def _vectorize(self, scenario: EarthquakeScenario) -> list[float] | None:
        values = {
            "magnitude": scenario.event.magnitude,
            "depth_km": scenario.event.depth_km,
            "population_density": scenario.population.population_density,
        }
        if values["magnitude"] is None:
            return None
        vec = []
        for key in self._artifact.get("features_used", FEATURE_ORDER):
            v = values.get(key)
            if v is None:
                return None
            vec.append(float(v))
        return vec

    def train_from_csv(self, csv_path: Path, hidden_size: int = 8) -> dict:
        import csv

        rows = []
        with csv_path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        if len(rows) < 5:
            raise ValueError("Training requires at least 5 labeled rows in CSV.")

        features_used = [c for c in FEATURE_ORDER if c in rows[0]]
        if not features_used:
            raise ValueError(f"CSV must include features among {FEATURE_ORDER}")
        if "affected_population" not in rows[0]:
            raise ValueError("CSV must include affected_population target column.")

        x = np.array([[float(r[f]) for f in features_used] for r in rows], dtype=float)
        y = np.array([[float(r["affected_population"])] for r in rows], dtype=float)

        x_mean, x_std = x.mean(axis=0), x.std(axis=0) + 1e-9
        y_mean, y_std = y.mean(), y.std() + 1e-9
        x_norm = (x - x_mean) / x_std
        y_norm = (y - y_mean) / y_std

        woa_net, woa_mse = whale_optimization(
            x_norm, y_norm, input_size=x_norm.shape[1], hidden_size=hidden_size, seed=self.settings.random_seed
        )
        baseline = BPNeuralNetwork(x_norm.shape[1], hidden_size, seed=self.settings.random_seed)
        bp_mse = baseline.mse(x_norm, y_norm)

        artifact = {
            "model": woa_net,
            "features_used": features_used,
            "x_mean": x_mean,
            "x_std": x_std,
            "y_mean": y_mean,
            "y_std": y_std,
            "training_dataset": str(csv_path),
            "model_version": "woa_bp_v0.1",
            "metrics": {
                "woa_bp_mse_norm": woa_mse,
                "bp_baseline_mse_norm": bp_mse,
                "note": "Metrics on normalized training set; provide held-out evaluation CSV for research reporting.",
            },
            "training_limitations": (
                "User-supplied training data only; not validated for all Indian seismotectonic contexts."
            ),
        }
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(artifact, self.model_path)
        self._artifact = artifact
        return artifact["metrics"]
