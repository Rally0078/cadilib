from zoneinfo import ZoneInfo
class TestSiteInfo:
    def test_siteinfo(self, test_site_dict, date_site_dict):
        sitenames, obs_datetimes, expected_zones = date_site_dict
        for site, obs_dt, expected_zone in zip(sitenames, obs_datetimes, expected_zones):
            assert expected_zone == test_site_dict.from_file(site).get_tzinfo(obs_dt)
    
    def test_raw_md4_TIR_LT(self, mock_raw_file_TIR_LT, test_py_rs_readers):
        for test_raw_reader in test_py_rs_readers:
            output = test_raw_reader.read_raw_data(mock_raw_file_TIR_LT)
            metadata = output.metadata
            assert metadata.datetime.tzinfo == ZoneInfo('Asia/Kolkata')

    def test_raw_md4_TIR_UT(self, mock_raw_file_TIR_UT, test_py_rs_readers):
        for test_raw_reader in test_py_rs_readers:
            output = test_raw_reader.read_raw_data(mock_raw_file_TIR_UT)
            metadata = output.metadata
            assert metadata.datetime.tzinfo == ZoneInfo(key='UTC')