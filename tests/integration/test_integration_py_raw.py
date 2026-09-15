from zoneinfo import ZoneInfo

def common_assertions(output):
    metadata = output.metadata
    freq_list = output.freq_list
    heights = output.dopbins.height
    frequencies = output.dopbins.frequency
    dop_shifts = output.dopbins.dop_shifts
    sensors = output.dopbins.signals
    assert list(output.dopbins.timepartitions.values())[-1] == len(output.dopbins.frequency)
    assert list(output.freqbins.timepartitions.values())[-1] == len(output.freqbins.frequency)

    assert len(freq_list) == metadata.nfreqs
    assert metadata.extension in ['md3', 'md4']
    assert heights.shape == frequencies.shape
    assert heights.shape[0] == sensors.shape[0]
    assert dop_shifts.shape == heights.shape

class TestCADIPyRawIntegration:
    def test_read_raw_rs(self, test_real_md3, test_real_md4, test_raw_reader):
        for test_file in [test_real_md3, test_real_md4]:
            output = test_raw_reader.read_raw_data(test_file)
            common_assertions(output)
        
        def test_read_raw_rs_othersites(self, test_raw_othersites, test_raw_reader):
            for test_file in test_raw_othersites:
                output = test_raw_reader.read_raw_data(test_file)
                metadata = output.metadata
                common_assertions(output) 
                assert metadata.datetime.tzinfo == ZoneInfo('Asia/Kolkata')
        
        def test_read_raw_rs_badfile(self, test_raw_badfile, test_raw_reader):
            output = test_raw_reader.read_raw_data(test_raw_badfile)
            metadata = output.metadata
            common_assertions(output)
            assert list(output.dopbins.timepartitions.values())[-1] == output.dopbins.signals.shape[0]

