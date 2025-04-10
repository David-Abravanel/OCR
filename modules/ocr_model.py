from typing import List
import numpy as np


class OcrData:
    def __init__(self, image: np.ndarray, use_angle_cls: bool = True, lang: str = 'en'):
        self.image = image
        self.use_angle_cls = use_angle_cls
        self.lang = lang


class OcrResult:
    def __init__(self, texts: List[str], output_data: List[dict]):
        self.texts = texts
        self.output_data = output_data

