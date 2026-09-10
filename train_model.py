# -*- coding: utf-8 -*-
"""
train_model.py
---------------
Generates a synthetic labelled dataset of surface patches and trains the
TinyMLP defect detector. Run standalone: `python3 train_model.py`

Author: Sipho Lucky Sibanda
"""

import numpy as np
from vision_model import (
    generate_synthetic_patch, extract_features, TinyMLP, PATCH_SIZE
)

def build_dataset(n_per_class=200, seed=7):
    rng = np.random.default_rng(seed)
    X, y = [], []
    # Class 0: OK (no defect)
    for _ in range(n_per_class):
        patch = generate_synthetic_patch(0, rng)
        X.append(extract_features(patch))
        y.append(0)
    # Class 1: defective (scratch / dent / discoloration, mixed severities
    # including deliberately weak/ambiguous cases)
    for defect_type in (1, 2, 3):
        for _ in range(n_per_class):
            severity = rng.uniform(0.15, 1.0)
            patch = generate_synthetic_patch(defect_type, rng, severity=severity)
            X.append(extract_features(patch))
            y.append(1)
    X = np.array(X)
    y = np.array(y)
    # Normalise features to zero mean / unit variance for stable training
    mu, sigma = X.mean(axis=0), X.std(axis=0) + 1e-9
    X_norm = (X - mu) / sigma
    return X_norm, y, mu, sigma


def one_hot(y, n_classes=2):
    out = np.zeros((len(y), n_classes))
    out[np.arange(len(y)), y] = 1.0
    return out


def main():
    print("=" * 70)
    print("TRAINING: Tiny defect-detection MLP (5 features -> 8 -> 2)")
    print("=" * 70)

    X, y, mu, sigma = build_dataset(n_per_class=200)
    n = len(y)
    idx = np.random.default_rng(1).permutation(n)
    split = int(n * 0.8)
    train_idx, test_idx = idx[:split], idx[split:]

    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]
    y_train_oh = one_hot(y_train)

    print(f"Dataset: {n} synthetic samples ({n - np.sum(y)} ok / {np.sum(y)} defective)")
    print(f"Train/test split: {len(train_idx)} / {len(test_idx)}")
    print()

    model = TinyMLP(n_in=5, n_hidden=8, n_out=2, seed=42)
    epochs = 400
    for epoch in range(epochs):
        loss = model.train_step(X_train, y_train_oh, lr=0.15)
        if epoch % 50 == 0 or epoch == epochs - 1:
            preds = np.argmax(model.predict_proba(X_train), axis=1)
            acc = np.mean(preds == y_train)
            print(f"  epoch {epoch:4d}   loss={loss:.4f}   train_acc={acc:.3f}")

    test_preds = np.argmax(model.predict_proba(X_test), axis=1)
    test_acc = np.mean(test_preds == y_test)
    print()
    print(f"FINAL TEST ACCURACY: {test_acc:.3f}  ({len(test_idx)} held-out samples)")
    print()

    model.save("model_weights.npz")
    np.savez("feature_norm.npz", mu=mu, sigma=sigma)
    print("Saved: model_weights.npz, feature_norm.npz")
    print("=" * 70)


if __name__ == "__main__":
    main()
