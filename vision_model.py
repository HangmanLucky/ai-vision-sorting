# -*- coding: utf-8 -*-
"""
vision_model.py
----------------
A deliberately small, honest neural network for the AI-Driven Edge Vision
Integration project.

WHAT THIS IS: a real, trained 2-layer MLP (5 input features -> 8 hidden
ReLU units -> 2 output classes, softmax) that genuinely learns to separate
"defect" from "ok" synthetic surface patches from engineered features.
Forward and backward passes are hand-written in numpy - no framework -
so every line of the network is inspectable.

WHAT THIS IS NOT: a production machine-vision defect classifier. Real
industrial vision systems use convolutional networks trained on tens of
thousands of real labelled images, run on a GPU or vision-specific edge
accelerator. This project's honest scope is the INTEGRATION problem -
how a trained model's verdict reaches a PLC reliably - not the computer
vision problem itself. See the project manual, Chapter 5, for the full
discussion of that boundary.

Author: Sipho Lucky Sibanda
"""

import numpy as np

PATCH_SIZE = 16
FEATURE_NAMES = ["mean", "std", "max_abs_dev", "h_gradient", "v_gradient"]
DEFECT_CLASSES = ["None", "Scratch", "Dent", "Discoloration"]


def generate_synthetic_patch(defect_type, rng, severity=None):
    """Generate a synthetic 16x16 grayscale 'surface' patch.

    defect_type: 0=ok, 1=scratch, 2=dent, 3=discoloration
    severity: 0.0-1.0, how strong the injected defect signature is
              (None = random). Lower severity produces patches that are
              genuinely ambiguous - this is what creates realistic
              mid-range confidence scores rather than everything being
              a trivially easy 99% or 1%.
    """
    baseline = 0.5
    patch = rng.normal(baseline, 0.04, size=(PATCH_SIZE, PATCH_SIZE))
    if severity is None:
        severity = rng.uniform(0.15, 1.0) if defect_type != 0 else 0.0

    if defect_type == 1:  # Scratch - a bright/dark diagonal line
        strength = 0.35 * severity
        for i in range(PATCH_SIZE):
            j = i + rng.integers(-1, 2)
            if 0 <= j < PATCH_SIZE:
                patch[i, j] += strength * (1 if rng.random() > 0.5 else -1)
    elif defect_type == 2:  # Dent - a localised dark blob
        cx, cy = rng.integers(4, 12, size=2)
        for i in range(PATCH_SIZE):
            for j in range(PATCH_SIZE):
                d = ((i - cx) ** 2 + (j - cy) ** 2) ** 0.5
                if d < 3.5:
                    patch[i, j] -= 0.30 * severity * (1 - d / 3.5)
    elif defect_type == 3:  # Discoloration - a broad low-contrast patch shift
        cx, cy = rng.integers(4, 12, size=2)
        for i in range(PATCH_SIZE):
            for j in range(PATCH_SIZE):
                d = ((i - cx) ** 2 + (j - cy) ** 2) ** 0.5
                if d < 6:
                    patch[i, j] += 0.18 * severity

    return np.clip(patch, 0.0, 1.0)


def extract_features(patch):
    """Five hand-engineered features - simple, fast, and inspectable.
    A real system would feed pixels (or learned conv features) directly
    into a much larger network; these stand in for that at a scale a
    from-scratch numpy MLP can learn from a small synthetic dataset."""
    mean = float(np.mean(patch))
    std = float(np.std(patch))
    max_abs_dev = float(np.max(np.abs(patch - mean)))
    h_gradient = float(np.mean(np.abs(np.diff(patch, axis=1))))
    v_gradient = float(np.mean(np.abs(np.diff(patch, axis=0))))
    return np.array([mean, std, max_abs_dev, h_gradient, v_gradient])


def classify_defect_type(patch, features):
    """Lightweight heuristic sub-classifier for the defect TYPE label only.
    Deliberately not a second trained network - this just distinguishes
    which injected signature is most likely present, for a human-readable
    class name alongside the trained model's pass/fail confidence."""
    mean = features[0]
    h_grad, v_grad = features[3], features[4]
    max_dev = features[2]
    if max_dev < 0.10:
        return "None"
    if abs(h_grad - v_grad) > 0.01 and max_dev > 0.15:
        return "Scratch"
    if mean > 0.52:
        return "Discoloration"
    return "Dent"


class TinyMLP:
    """A minimal 2-layer MLP: Linear -> ReLU -> Linear -> Softmax.
    Weights are plain numpy arrays; training is manual gradient descent.
    """

    def __init__(self, n_in=5, n_hidden=8, n_out=2, seed=42):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0, 0.5, size=(n_in, n_hidden))
        self.b1 = np.zeros(n_hidden)
        self.W2 = rng.normal(0, 0.5, size=(n_hidden, n_out))
        self.b2 = np.zeros(n_out)

    def forward(self, X):
        z1 = X @ self.W1 + self.b1
        a1 = np.maximum(0, z1)  # ReLU
        z2 = a1 @ self.W2 + self.b2
        z2 = z2 - np.max(z2, axis=-1, keepdims=True)
        exp = np.exp(z2)
        probs = exp / np.sum(exp, axis=-1, keepdims=True)
        return probs, (X, z1, a1)

    def train_step(self, X, y_onehot, lr=0.05):
        probs, (X_in, z1, a1) = self.forward(X)
        n = X.shape[0]
        dz2 = (probs - y_onehot) / n
        dW2 = a1.T @ dz2
        db2 = np.sum(dz2, axis=0)
        da1 = dz2 @ self.W2.T
        dz1 = da1 * (z1 > 0)
        dW1 = X_in.T @ dz1
        db1 = np.sum(dz1, axis=0)

        self.W1 -= lr * dW1
        self.b1 -= lr * db1
        self.W2 -= lr * dW2
        self.b2 -= lr * db2

        loss = -np.mean(np.sum(y_onehot * np.log(probs + 1e-9), axis=1))
        return loss

    def predict_proba(self, X):
        probs, _ = self.forward(X)
        return probs

    def save(self, path):
        np.savez(path, W1=self.W1, b1=self.b1, W2=self.W2, b2=self.b2)

    @classmethod
    def load(cls, path):
        data = np.load(path)
        model = cls()
        model.W1, model.b1 = data["W1"], data["b1"]
        model.W2, model.b2 = data["W2"], data["b2"]
        return model
