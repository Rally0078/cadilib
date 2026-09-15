from cadilib.utils.pandasutils import PandasUtils
import copy
class TestPandasUtils:
    def test_create_pandas(self, mock_data, expected_column_names):
        df_dopbins, df_freqbins = PandasUtils.create_pandas_from_arrays(mock_data, radar_type='cadi')

        expected_columns = copy.deepcopy(expected_column_names)
        for i in range(mock_data.metadata.noofreceivers):
            expected_columns.append(f"sensor{i+1} real")
            expected_columns.append(f"sensor{i+1} imag")
        assert (df_dopbins.columns == expected_columns).all()
        assert len(df_dopbins) == len(mock_data.dopbins.frequency)
