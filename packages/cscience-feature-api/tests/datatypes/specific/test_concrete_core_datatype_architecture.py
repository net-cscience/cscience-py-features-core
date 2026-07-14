import unittest

from cscience.features.api.datatypes.audio.audio_bytes import (
    AudioBytes,
)
from cscience.features.api.datatypes.audio.audio_signal import (
    AudioSignal,
)
from cscience.features.api.datatypes.base.datatype_base import (
    DatatypeBase,
)
from cscience.features.api.datatypes.base.media.audio_bytes_base import (
    AudioBytesBase,
)
from cscience.features.api.datatypes.base.media.image_bytes_base import (
    ImageBytesBase,
)
from cscience.features.api.datatypes.base.structural.batch_base import (
    BatchBase,
)
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.primitive_vector_base import (
    PrimitiveVectorBase,
)
from cscience.features.api.datatypes.base.structural.primitive_vector_batch_base import (
    PrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.base.structural.spatial_primitive_vector_batch_base import (
    SpatialPrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)
from cscience.features.api.datatypes.image.image_bytes import (
    ImageBytes,
)
from cscience.features.api.datatypes.image.image_data_url import (
    ImageDataUrl,
)
from cscience.features.api.datatypes.image.pil_image import (
    PilImage,
)
from cscience.features.api.datatypes.image.pil_image_batch import (
    PilImageBatch,
)
from cscience.features.api.datatypes.primitives_scalar.bool_value import (
    BoolValue,
)
from cscience.features.api.datatypes.primitives_scalar.float_value import (
    FloatValue,
)
from cscience.features.api.datatypes.primitives_scalar.int_value import (
    IntValue,
)
from cscience.features.api.datatypes.primitives_vectors.bool_vector import (
    BoolVector,
)
from cscience.features.api.datatypes.primitives_vectors.float_vector import (
    FloatVector,
)
from cscience.features.api.datatypes.primitives_vectors.int_vector import (
    IntVector,
)
from cscience.features.api.datatypes.primitives_vectors_batch.bool_vector_batch import (
    BoolVectorBatch,
)
from cscience.features.api.datatypes.primitives_vectors_batch.float_vector_batch import (
    FloatVectorBatch,
)
from cscience.features.api.datatypes.primitives_vectors_batch.int_vector_batch import (
    IntVectorBatch,
)
from cscience.features.api.datatypes.references.data_url import (
    DataUrl,
)
from cscience.features.api.datatypes.references.file_path import (
    FilePath,
)
from cscience.features.api.datatypes.spatial.spatial_float_vector_batch import (
    SpatialFloatVectorBatch,
)
from cscience.features.api.datatypes.text.text import (
    Text,
)
from cscience.features.api.datatypes.text.text_batch import (
    TextBatch,
)


CONCRETE_CORE_DATATYPES = (
    AudioBytes,
    AudioSignal,
    ImageBytes,
    ImageDataUrl,
    PilImage,
    PilImageBatch,
    BoolValue,
    FloatValue,
    IntValue,
    BoolVector,
    FloatVector,
    IntVector,
    BoolVectorBatch,
    FloatVectorBatch,
    IntVectorBatch,
    DataUrl,
    FilePath,
    SpatialFloatVectorBatch,
    Text,
    TextBatch,
)


class TestConcreteCoreDatatypeArchitecture(unittest.TestCase):
    def test_all_concrete_types_are_core_datatypes(self) -> None:
        for datatype_class in CONCRETE_CORE_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertTrue(
                    issubclass(
                        datatype_class,
                        CoreDatatype,
                    )
                )

    def test_all_concrete_types_use_core_namespace(self) -> None:
        for datatype_class in CONCRETE_CORE_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.namespace,
                    "core",
                )

    def test_all_concrete_types_reach_datatype_base_once(
        self,
    ) -> None:
        for datatype_class in CONCRETE_CORE_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.__mro__.count(
                        DatatypeBase
                    ),
                    1,
                )

    def test_all_concrete_types_have_one_data_owner_branch(
        self,
    ) -> None:
        for datatype_class in CONCRETE_CORE_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                data_owner_branches = tuple(
                    base
                    for base in datatype_class.__bases__
                    if issubclass(base, DatatypeBase)
                )

                self.assertEqual(
                    len(data_owner_branches),
                    1,
                    msg=(
                        f"{datatype_class.__name__} must have "
                        f"exactly one direct data-owner branch, "
                        f"got {data_owner_branches}."
                    ),
                )

class TestConcreteCoreDatatypeMro(unittest.TestCase):
    def assert_mro_before(
        self,
        datatype_class: type,
        earlier_class: type,
        later_class: type,
    ) -> None:
        mro = datatype_class.__mro__

        self.assertLess(
            mro.index(earlier_class),
            mro.index(later_class),
        )

    def test_media_bases_precede_core_datatype(self) -> None:
        cases = (
            (AudioBytes, AudioBytesBase),
            (ImageBytes, ImageBytesBase),
        )

        for datatype_class, media_base in cases:
            with self.subTest(datatype_class=datatype_class):
                self.assert_mro_before(
                    datatype_class,
                    media_base,
                    CoreDatatype,
                )

    def test_vector_bases_precede_core_datatype(self) -> None:
        cases = (
            (BoolVector, PrimitiveVectorBase),
            (FloatVector, PrimitiveVectorBase),
            (IntVector, PrimitiveVectorBase),
            (
                BoolVectorBatch,
                PrimitiveVectorBatchBase,
            ),
            (
                FloatVectorBatch,
                PrimitiveVectorBatchBase,
            ),
            (
                IntVectorBatch,
                PrimitiveVectorBatchBase,
            ),
            (
                SpatialFloatVectorBatch,
                SpatialPrimitiveVectorBatchBase,
            ),
        )

        for datatype_class, structural_base in cases:
            with self.subTest(datatype_class=datatype_class):
                self.assert_mro_before(
                    datatype_class,
                    structural_base,
                    CoreDatatype,
                )

    def test_embedding_base_precedes_core_datatype(
        self,
    ) -> None:
        embedding_types = (
            FloatVector,
            FloatVectorBatch,
            SpatialFloatVectorBatch,
        )

        for datatype_class in embedding_types:
            with self.subTest(datatype_class=datatype_class):
                self.assert_mro_before(
                    datatype_class,
                    EmbeddingBase,
                    CoreDatatype,
                )

    def test_batch_base_precedes_core_datatype(self) -> None:
        batch_types = (
            TextBatch,
            PilImageBatch,
            BoolVectorBatch,
            FloatVectorBatch,
            IntVectorBatch,
            SpatialFloatVectorBatch,
        )

        for datatype_class in batch_types:
            with self.subTest(datatype_class=datatype_class):
                self.assert_mro_before(
                    datatype_class,
                    BatchBase,
                    CoreDatatype,
                )

import unittest

from PIL import Image

from cscience.features.api.datatypes.audio.audio_bytes import (
    AudioBytes,
)
from cscience.features.api.datatypes.image.image_bytes import (
    ImageBytes,
)
from cscience.features.api.datatypes.image.pil_image_batch import (
    PilImageBatch,
)
from cscience.features.api.datatypes.primitives_vectors.bool_vector import (
    BoolVector,
)
from cscience.features.api.datatypes.primitives_vectors.float_vector import (
    FloatVector,
)
from cscience.features.api.datatypes.primitives_vectors.int_vector import (
    IntVector,
)
from cscience.features.api.datatypes.primitives_vectors_batch.float_vector_batch import (
    FloatVectorBatch,
)
from cscience.features.api.datatypes.text.text_batch import (
    TextBatch,
)


class TestConcreteCoreDatatypeConstruction(
    unittest.TestCase
):
    def test_constructs_encoded_media(self) -> None:
        audio = AudioBytes(b"audio")
        image = ImageBytes(b"image")

        self.assertEqual(audio.data(), b"audio")
        self.assertEqual(image.data(), b"image")

    def test_constructs_primitive_vectors(self) -> None:
        bool_vector = BoolVector([True, False])
        float_vector = FloatVector([1.0, 2.0])
        int_vector = IntVector([1, 2])

        self.assertEqual(bool_vector.length(), 2)
        self.assertEqual(float_vector.length(), 2)
        self.assertEqual(float_vector.embedding_dim(), 2)
        self.assertEqual(int_vector.length(), 2)

    def test_constructs_embedding_batch(self) -> None:
        batch = FloatVectorBatch({
            1: [3.0, 4.0],
            0: [1.0, 2.0],
        })

        self.assertEqual(batch.batch_size(), 2)
        self.assertEqual(batch.length(), 2)
        self.assertEqual(batch.embedding_dim(), 2)
        self.assertEqual(batch.ordered_keys(), (0, 1))

    def test_constructs_text_batch(self) -> None:
        batch = TextBatch({
            1: "second",
            0: "first",
        })

        self.assertEqual(
            batch.ordered_values(),
            ("first", "second"),
        )

    def test_constructs_pil_image_batch(self) -> None:
        first = Image.new("RGB", (10, 10))
        second = Image.new("RGB", (10, 10))

        batch = PilImageBatch({
            1: second,
            0: first,
        })

        self.assertEqual(
            batch.ordered_values(),
            (first, second),
        )