import pytest

def common_assertions(output):
    metadata = output.metadata
    heights = output.dopbins.height
    freqs = output.dopbins.frequency
    freq_list = output.freq_list
    dop_shifts = output.dopbins.dop_shifts
    sensors = output.dopbins.signals
    if not metadata.incompleteheader:
        assert metadata.nfreqs == len(freq_list)
    assert type(output.dopbins.timepartitions) == dict
    assert type(output.freqbins.timepartitions) == dict
    assert heights.shape == freqs.shape
    assert heights.shape[0] == sensors.shape[0]
    assert dop_shifts.shape == heights.shape
    assert len(output.freqbins.timepartitions) == len(output.dopbins.timepartitions)
    assert len(output.freqbins.frebins_noise_power10) == len(output.freqbins.frebins_gain_flag)
    assert len(output.freqbins.frebins_noise_power10) == len(output.freqbins.frebins_noise_flag)
    assert len(output.freqbins.frebins_gain_flag) == len(output.freqbins.frebins_noise_power10)

@pytest.mark.rust_test
class TestCADIRustRaw:
    def test_read_rawmd4(self, mock_raw_file, test_rust_raw_reader):
        output = test_rust_raw_reader.read_raw_data(mock_raw_file)
        common_assertions(output)
        heights = output.dopbins.height
        metadata = output.metadata
        assert heights.shape[0] == list(output.dopbins.timepartitions.values())[-1]
        assert len(output.freqbins.frebins_gain_flag) == list(output.freqbins.timepartitions.values())[-1]
        assert len(output.freqbins.frebins_noise_power10) == metadata.nfreqs * len(output.freqbins.timepartitions)
    
    def test_read_rawmd4_incomplete_header(self, mock_raw_file_incomplete_header, test_rust_raw_reader):
        output = test_rust_raw_reader.read_raw_data(mock_raw_file_incomplete_header)
        common_assertions(output)
        metadata = output.metadata
        assert metadata.incompletedata == True
        assert metadata.incompleteheader == True
    
    def test_read_rawmd4_incomplete_header_2(self, mock_raw_file_incomplete_header_2, test_rust_raw_reader):
        output = test_rust_raw_reader.read_raw_data(mock_raw_file_incomplete_header_2)
        common_assertions(output)
        metadata = output.metadata
        assert metadata.incompletedata == True
        assert metadata.incompleteheader == True

    def test_read_rawmd4_incomplete_data(self, mock_raw_file_incomplete_data, test_rust_raw_reader):
        output = test_rust_raw_reader.read_raw_data(mock_raw_file_incomplete_data)
        common_assertions(output)
        metadata = output.metadata
        assert metadata.incompletedata == True
        assert metadata.incompleteheader == False
    
    def test_read_rawmd4_incomplete_data_2(self, mock_raw_file_incomplete_data_2, test_rust_raw_reader):
        output = test_rust_raw_reader.read_raw_data(mock_raw_file_incomplete_data_2)
        metadata = output.metadata
        common_assertions(output)
        assert type(output.dopbins.timepartitions) == dict
        assert type(output.freqbins.timepartitions) == dict
        assert metadata.incompletedata == True
        assert metadata.incompleteheader == False
    
    def test_read_rawmd4_incomplete_data_3(self, mock_raw_file_incomplete_data_3, test_rust_raw_reader):
        output = test_rust_raw_reader.read_raw_data(mock_raw_file_incomplete_data_3)
        metadata = output.metadata
        common_assertions(output)
        assert type(output.dopbins.timepartitions) == dict
        assert type(output.freqbins.timepartitions) == dict
        assert metadata.incompletedata == True
        assert metadata.incompleteheader == False
    
    def test_read_rawmd4_incomplete_data_4(self, mock_raw_file_incomplete_data_4, test_rust_raw_reader):
        output = test_rust_raw_reader.read_raw_data(mock_raw_file_incomplete_data_4)
        common_assertions(output)
        metadata = output.metadata
        assert metadata.incompletedata == True
        assert metadata.incompleteheader == False
        assert output.dopbins.height.shape[0] == list(output.dopbins.timepartitions.values())[-1]
        assert len(output.freqbins.frebins_gain_flag) == list(output.freqbins.timepartitions.values())[-1]
        assert len(output.freqbins.frebins_noise_power10) == metadata.nfreqs * len(output.freqbins.timepartitions)