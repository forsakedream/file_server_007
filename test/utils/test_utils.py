from src import utils


def test_uniquness():
    generated_strings = []
    string_length = 10
    for _ in range(100):
        value = utils.generate_name(string_length)
        assert value not in generated_strings
        assert len(value) == string_length
