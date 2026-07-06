import unittest
from typing import Literal

from numpy import random
from pydantic import Field

from cscience.features.api.config.config_base import ConfigBase


class MockConfig(ConfigBase):
        string_value: str = Field(
            default="Hello World!",
            title='A string value',
            description='This is a string value for testing purposes.',
            min_length=3,
            max_length=50,
        )
        int_value:int = Field(
            default=42,
            title='An integer value',
            description='This is an integer value for testing purposes.',
            ge=0,
            le=100
        )
        bool_value:bool = Field(
            default=False,
            title='A boolean value',
            description='This is a boolean value for testing purposes.'
        )
        float_value:float = Field(
            default=3.14,
            title='A float value',
            description='This is a float value for testing purposes.',
            ge=0,
            le=10
        )
        list_value:list[int] = Field(
            default=[1, 2, 3],
            title='A list value',
            description='This is a list value for testing purposes.'
        )
        dict_value:dict[str,str] = Field(
            default={"key": "value"},
            title='A dict value',
            description='This is a dict value for testing purposes.'
        )
        literal_value: Literal["test1", "test2"] = Field(
            default="test1",
            title='A literal value',
            description='This is a literal value for testing purposes.'
        )

        @classmethod
        def _namespace(cls):
            return "mock"

class ConfigTest(unittest.TestCase):

    def test_read(self):
        cfg=MockConfig()
        print(cfg.model_dump())
        self.assertEqual(cfg.string_value, "Hello World!")
        self.assertEqual(cfg.int_value, 42)
        self.assertEqual(cfg.bool_value, False)
        self.assertEqual(cfg.float_value, 3.14)
        self.assertEqual(cfg.list_value, [1, 2, 3])
        self.assertEqual(cfg.dict_value, {"key": "value"})
        self.assertEqual(cfg.literal_value, "test1")
        pass

    def test_multiple(self):
        cfg1 = MockConfig()
        cfg2 = MockConfig()
        self.assertEqual(cfg1.model_dump(), cfg2.model_dump())
        cfg2.string_value = "Hello World and Moon!"
        print(f"\n-Dump cfg 1 contains: {cfg1.model_dump()}")
        print(f"\n-Dump cfg 2 contains: {cfg2.model_dump()}")
        print(cfg2.model_dump())
        self.assertNotEqual(cfg1.model_dump(), cfg2.model_dump())
        pass

    def test_literal(self):
        cfg = MockConfig()
        cfg.literal_value = "test2"
        self.assertEqual(cfg.literal_value, "test2")
        cfg.literal_value = "test3"
        MockConfig.model_validate(cfg)
        pass