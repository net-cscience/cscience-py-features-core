from typing import List

import torch

from api import FeatureConnector
from clip import ClipFeature


class ClipConnector():

    def __init__(self):
        ClipFeature()


    def clip_text(cls, data: str) -> List[float]:
        input = FeatureConnector[str,List[str]]()
        output = FeatureConnector[str,List[float]]()
        return output.convert(ClipFeature._clip_text(input.convert(data)))