import numpy as np


class BPNeuralNetwork:
    def __init__(self, input_size: int, hidden_size: int, output_size: int = 1, seed: int = 42) -> None:
        rng = np.random.default_rng(seed)
        self.w1 = rng.normal(0, 0.1, size=(input_size, hidden_size))
        self.b1 = np.zeros(hidden_size)
        self.w2 = rng.normal(0, 0.1, size=(hidden_size, output_size))
        self.b2 = np.zeros(output_size)

    def forward(self, x: np.ndarray) -> np.ndarray:
        h = np.tanh(x @ self.w1 + self.b1)
        return h @ self.w2 + self.b2

    def flatten(self) -> np.ndarray:
        return np.concatenate([self.w1.ravel(), self.b1.ravel(), self.w2.ravel(), self.b2.ravel()])

    def load_flat(self, params: np.ndarray, input_size: int, hidden_size: int) -> None:
        idx = 0
        w1_size = input_size * hidden_size
        self.w1 = params[idx : idx + w1_size].reshape(input_size, hidden_size)
        idx += w1_size
        self.b1 = params[idx : idx + hidden_size]
        idx += hidden_size
        w2_size = hidden_size * 1
        self.w2 = params[idx : idx + w2_size].reshape(hidden_size, 1)
        idx += w2_size
        self.b2 = params[idx : idx + 1]

    def mse(self, x: np.ndarray, y: np.ndarray) -> float:
        pred = self.forward(x)
        return float(np.mean((pred - y) ** 2))
