import pytest
from dataclasses import fields

def cross_equality_assertions(output_py, output_rs):
    metadata_py = output_py.metadata
    metadata_rs = output_rs.metadata
    heights_py = output_py.dopbins.height
    heights_rs = output_rs.dopbins.height
    freq_list_py = output_py.freq_list
    freq_list_rs = output_rs.freq_list
    frequencies_py = output_py.dopbins.frequency
    frequencies_rs = output_rs.dopbins.frequency
    dop_shifts_py = output_py.dopbins.dop_shifts
    dop_shifts_rs = output_rs.dopbins.dop_shifts
    signals_py = output_py.dopbins.signals
    signals_rs = output_rs.dopbins.signals
    assert (heights_py == heights_rs).all()
    assert (freq_list_py == freq_list_rs).all()
    assert (frequencies_py == frequencies_rs).all()
    assert (dop_shifts_py == dop_shifts_rs).all()
    assert (signals_py == signals_rs).all()
    assert (output_py.dopbins.timepartitions.keys() == output_rs.dopbins.timepartitions.keys())
    for key in output_py.dopbins.timepartitions.keys():
        assert (output_py.dopbins.timepartitions[key] == output_rs.dopbins.timepartitions[key])
    assert (output_py.freqbins.frequency == output_rs.freqbins.frequency).all()
    assert (output_py.freqbins.frebins_gain_flag == output_rs.freqbins.frebins_gain_flag).all()
    assert (output_py.freqbins.frebins_noise_flag == output_rs.freqbins.frebins_noise_flag).all()
    assert (output_py.freqbins.frebins_noise_power10 == output_rs.freqbins.frebins_noise_power10).all()
    # Exclude custom function added in dataclass for easy initialization
    header_py = [a for a in dir(metadata_py) if ((not a.startswith("__")) and (a != "from_raw_header"))]
    # Exclude dictionary methods in Rust output
    header_rs = [a for a in dir(metadata_rs) if ((not a.startswith("__")) and (a not in ["items", "keys"]))]
    assert header_py == header_rs
    for field in fields(metadata_py):
        value_py = getattr(metadata_py, field.name)
        value_rs = getattr(metadata_rs, field.name)
        assert value_py == value_rs, f"For field {field.name}, Python value is {value_py} and Rust value is {value_rs}"
    assert metadata_py.datetime.tzinfo == metadata_rs.datetime.tzinfo

@pytest.mark.rust_test
class TestCADIRustPyEquality:
    def test_py_rs_reader_equality_mock(self, mock_raw_files, test_raw_reader, test_rust_raw_reader):
        for mock_raw_file in mock_raw_files:
            file_path = mock_raw_file
            output_py = test_raw_reader.read_raw_data(file_path)
            output_rs = test_rust_raw_reader.read_raw_data(file_path)
            cross_equality_assertions(output_py, output_rs)
    
    def test_py_rs_reader_equality(self, test_real_md3, test_real_md4, test_raw_reader, test_rust_raw_reader):
        for raw_file in [test_real_md3, test_real_md4]:
            output_py = test_raw_reader.read_raw_data(raw_file)
            output_rs = test_rust_raw_reader.read_raw_data(raw_file)
            cross_equality_assertions(output_py, output_rs)

    def test_py_rs_reader_equality_othersites(self, test_raw_othersites, test_raw_reader, test_rust_raw_reader):
        for raw_file in test_raw_othersites:
            output_py = test_raw_reader.read_raw_data(raw_file)
            output_rs = test_rust_raw_reader.read_raw_data(raw_file)
            cross_equality_assertions(output_py, output_rs)


    def test_py_rs_reader_equality_badfile(self, test_raw_badfile, test_raw_reader, test_rust_raw_reader):
        output_py = test_raw_reader.read_raw_data(test_raw_badfile)
        output_rs = test_rust_raw_reader.read_raw_data(test_raw_badfile)
        cross_equality_assertions(output_py, output_rs)
