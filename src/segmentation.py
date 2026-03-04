import numpy as np
from sklearn.tree import DecisionTreeClassifier
from scipy.ndimage import sobel
from pathlib import Path

class ArtifactSegmenter:
    def __init__(self, max_depth=15):
        self.model = DecisionTreeClassifier(max_depth=max_depth)
        self.is_trained = False

    def _get_features(self, volume):
        dx = sobel(volume, axis=0)
        dy = sobel(volume, axis=1)
        dz = sobel(volume, axis=2)
        grad_mag = np.sqrt(dx**2 + dy**2 + dz**2).astype(np.float32)
        return np.stack([volume.flatten(), grad_mag.flatten()], axis=-1)

    def predict_mask(self, volume):
        if not self.is_trained:
            return (volume > 2500).astype(np.uint8)
        X = self._get_features(volume)
        prediction = self.model.predict(X)
        return prediction.reshape(volume.shape).astype(np.uint8)
