import unittest
from pathlib import Path

import torch

from cscience.features.api import (
    SpatialBatchLayout,
    SpatialRegion,
    SpatialVectorBatchData,
)
from cscience.features.clip_spatial import ClipSpatialConnector
from cscience.features.clip_spatial.clip_spatial_config import ClipSpatialConfig

from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_tensor_batch import (
    ClipSpatialTensorBatch,
)
from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_text_tensor_batch import (
    ClipSpatialTextTensorBatch,
)
from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_text_tensor_batch_data import (
    ClipSpatialTextTensorBatchData,
)
from cscience.features.clip_spatial.clip_spatial_feature import (
    ClipSpatialFeature,
)


def make_regions() -> tuple[SpatialRegion, ...]:
    return (
        SpatialRegion(
            index=0,
            row=0,
            column=0,
            center_x=5,
            center_y=5,
            x0=0,
            y0=0,
            x1=10,
            y1=10,
            nx0=0.0,
            ny0=0.0,
            nx1=0.5,
            ny1=1.0,
        ),
        SpatialRegion(
            index=1,
            row=0,
            column=1,
            center_x=15,
            center_y=5,
            x0=10,
            y0=0,
            x1=20,
            y1=10,
            nx0=0.5,
            ny0=0.0,
            nx1=1.0,
            ny1=1.0,
        ),
    )


def make_spatial_vectors() -> ClipSpatialTensorBatch:
    return ClipSpatialTensorBatch(
        SpatialVectorBatchData(
            vectors={
                0: torch.tensor([1.0, 0.0]),
                1: torch.tensor([0.0, 1.0]),
                2: torch.tensor([0.5, 0.5]),
                3: torch.tensor([-1.0, 0.0]),
            },
            layout=SpatialBatchLayout(
                item_count=2,
                regions_per_item=2,
            ),
            item_keys=(10, 20),
            regions=make_regions(),
            base_vectors={
                10: torch.tensor([1.0, 0.0]),
                20: torch.tensor([0.0, 1.0]),
            }
        )
    )


def make_text_vectors() -> ClipSpatialTextTensorBatch:
    return ClipSpatialTextTensorBatch(
        ClipSpatialTextTensorBatchData(
            keys=(100, 200),
            vectors=torch.tensor(
                [
                    [1.0, 0.0],
                    [0.0, 1.0],
                ]
            ),
        )
    )

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"

class TestClipSpatialScoring(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        ClipSpatialConfig.set_default_config_directory(FIXTURE_DIR / "config")
        cls.connector = ClipSpatialConnector(ClipSpatialConfig())


    def test_scores_queries_against_regions(self) -> None:
        result = self.connector.feature._score_embeddings(
            text_vectors=make_text_vectors(),
            spatial_vectors=make_spatial_vectors(),
        )

        self.assertEqual(
            result.query_keys,
            (100, 200),
        )
        self.assertEqual(result.query_count, 2)
        self.assertEqual(result.item_keys, (10, 20))
        self.assertEqual(result.batch_size(), 4)

        self.assertEqual(
            result.vector_at(0, 0),
            [1.0, 0.0],
        )
        self.assertEqual(
            result.vector_at(0, 1),
            [0.0, 1.0],
        )
        self.assertEqual(
            result.vector_at(1, 0),
            [0.5, 0.5],
        )
        self.assertEqual(
            result.vector_at(1, 1),
            [-1.0, 0.0],
        )

    def test_preserves_spatial_metadata(self) -> None:
        spatial = make_spatial_vectors()

        result = self.connector.feature._score_embeddings(
            text_vectors=make_text_vectors(),
            spatial_vectors=spatial,
        )

        self.assertEqual(result.layout, spatial.layout)
        self.assertEqual(result.regions, spatial.regions)
        self.assertEqual(result.item_keys, spatial.item_keys)

    def test_rejects_embedding_dimension_mismatch(
        self,
    ) -> None:
        text_vectors = ClipSpatialTextTensorBatch(
            ClipSpatialTextTensorBatchData(
                keys=(100,),
                vectors=torch.tensor(
                    [[1.0, 0.0, 0.0]]
                ),
            )
        )

        with self.assertRaises(ValueError):
            self.connector.feature._score_embeddings(
                text_vectors=text_vectors,
                spatial_vectors=make_spatial_vectors(),
            )