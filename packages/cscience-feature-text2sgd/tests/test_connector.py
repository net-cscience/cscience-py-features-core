import unittest

from cscience.features.text2sdg import Text2SdgConnector


class TestText2SdgConnector(unittest.TestCase):
    def test_detect(self) -> None:
        connector = Text2SdgConnector()

        result = connector.detect([
            "Climate change and renewable energy are important challenges.",
            "This course introduces relational database systems.",
        ])

        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()