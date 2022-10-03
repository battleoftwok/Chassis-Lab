from pathlib import Path
import main
import unittest


class TestChoosePneumatics(unittest.TestCase):

    input_data = main.read_yml_file(Path('../data/variants_data.yml'))
    pneumatics_data = main.read_yml_file((Path('../data/pneumatics.yml')))

    def test_Belyaev(self):
        var_data = main.get_unique_variant(1, self.input_data)
        assert main.pneumatics_selection(self.pneumatics_data, var_data, 2)["№"] == 21

    def test_Svatshov(self):
        var_data = main.get_unique_variant(18, self.input_data)
        assert main.pneumatics_selection(self.pneumatics_data, var_data, 4)["№"] == 6

    def test_Solonin(self):
        var_data = main.get_unique_variant(20, self.input_data)
        assert main.pneumatics_selection(self.pneumatics_data, var_data, 1)["№"] == 7


if __name__ == '__main__':
    unittest.main()
