import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data"))

from prerequisite_survey import survey_text


FIXTURES = ROOT / "tests" / "survey-fixtures"


class PrerequisiteSurveyTest(unittest.TestCase):
    def survey(self, name):
        return survey_text((FIXTURES / name).read_text(), "yaml")

    def test_structured_unlock_step(self):
        self.assertEqual(self.survey("structured-unlock.yaml")["unlock"], "structured")

    def test_prose_only_unlock_mention(self):
        self.assertEqual(self.survey("prose-unlock.yaml")["unlock"], "prose-only")

    def test_no_prerequisite(self):
        self.assertEqual(self.survey("no-prerequisite.yaml")["unlock"], "none")

    def test_partition_scheme(self):
        self.assertEqual(self.survey("partition-and-identity.yaml")["partition_scheme"], "structured")

    def test_device_identity(self):
        self.assertEqual(self.survey("partition-and-identity.yaml")["identity"], "structured")


if __name__ == "__main__":
    unittest.main()
