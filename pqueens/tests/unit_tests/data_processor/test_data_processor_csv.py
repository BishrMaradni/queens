"""Tests for post post csv routine."""

import re

import numpy as np
import pandas as pd
import pytest

import pqueens.data_processor.data_processor_csv_data
from pqueens.data_processor.data_processor_csv_data import DataProcessorCsv


@pytest.fixture(scope="session")
def dummy_csv_file(tmp_path_factory):
    """Create dummy csv-file for tests."""
    dummy_data = """# structure problem, writing nodal data of node 26
# control information: nodal coordinates   x = 1.13276e-15    y = 18.5    z = 1
#
#     step            time             d_x             d_y             d_z
         1    2.000000e-02    4.399840e-02    6.487949e-01    0.000000e+00
         2    4.000000e-02    6.820325e-02    1.150965e+00    0.000000e+00
         3    6.000000e-02    7.717940e-02    1.542656e+00    0.000000e+00
         4    8.000000e-02    7.964939e-02    1.860496e+00    0.000000e+00
         5    1.000000e-01    7.997493e-02    2.128853e+00    0.000000e+00
         6    1.200000e-01    8.005790e-02    2.362839e+00    0.000000e+00
         7    1.400000e-01    8.061949e-02    2.571953e+00    0.000000e+00
         8    1.600000e-01    8.184129e-02    2.762376e+00    0.000000e+00
         9    1.800000e-01    8.367777e-02    2.938276e+00    0.000000e+00
        10    2.000000e-01    8.600778e-02    3.102564e+00    0.000000e+00"""
    tmp_dir = tmp_path_factory.mktemp("data")
    dummy_data_processor_path = tmp_dir / 'dummy_csvfile.csv'
    with open(dummy_data_processor_path, 'w') as csv_file:
        csv_file.write(dummy_data)

    return dummy_data_processor_path


@pytest.fixture()
def default_raw_data():
    """Default raw data for tests."""
    index = [
        0.02000,
        0.04000,
        0.06000,
        0.08000,
        0.10000,
        0.12000,
        0.14000,
        0.16000,
        0.18000,
        0.20000,
    ]
    data = [
        0.64879,
        1.15097,
        1.54266,
        1.86050,
        2.12885,
        2.36284,
        2.57195,
        2.76238,
        2.93828,
        3.10256,
    ]
    raw_data = pd.DataFrame(data, index=index, columns=['d_x'])
    raw_data.index.name = 'step'
    return raw_data


@pytest.fixture()
def default_data_processor():
    """Default post post csv class for unit tests."""
    post_file_name_identifier = 'dummy_prefix*dummypostfix'
    file_options_dict = {}
    filter_type = 'entire_file'
    files_to_be_deleted_regex_lst = []
    driver_name = 'driver'
    header_row = 0
    use_cols_lst = [0, 2, 3]
    skip_rows = 1
    index_column = 0
    use_rows_lst = []
    filter_range = []
    filter_target_values = [1, 2]
    filter_tol = 2.0

    pp = pqueens.data_processor.data_processor_csv_data.DataProcessorCsv(
        post_file_name_identifier,
        file_options_dict,
        files_to_be_deleted_regex_lst,
        driver_name,
        filter_type,
        header_row,
        use_cols_lst,
        skip_rows,
        index_column,
        use_rows_lst,
        filter_range,
        filter_target_values,
        filter_tol,
    )
    return pp


@pytest.mark.unit_tests
def test_init():
    """Test the init method."""
    post_file_name_identifier = 'dummy_prefix*dummypostfix'
    file_options_dict = {}
    filter_type = 'entire_file'
    files_to_be_deleted_regex_lst = []
    driver_name = 'driver'
    header_row = 0
    use_cols_lst = [0, 2, 3]
    skip_rows = 1
    index_column = 0
    use_rows_lst = []
    filter_range = []
    filter_target_values = [1, 2]
    filter_tol = 2.0

    my_data_processor = DataProcessorCsv(
        post_file_name_identifier,
        file_options_dict,
        files_to_be_deleted_regex_lst,
        driver_name,
        filter_type,
        header_row,
        use_cols_lst,
        skip_rows,
        index_column,
        use_rows_lst,
        filter_range,
        filter_target_values,
        filter_tol,
    )

    assert my_data_processor.driver_name == driver_name
    assert my_data_processor.file_options_dict == file_options_dict
    assert my_data_processor.files_to_be_deleted_regex_lst == files_to_be_deleted_regex_lst
    assert my_data_processor.filter_range == filter_range
    assert my_data_processor.filter_target_values == filter_target_values
    assert my_data_processor.filter_tol == filter_tol
    assert my_data_processor.filter_type == filter_type
    assert my_data_processor.header_row == header_row
    assert my_data_processor.index_column == index_column
    assert my_data_processor.post_file_name_identifier == post_file_name_identifier
    assert my_data_processor.post_file_path is None
    np.testing.assert_array_equal(my_data_processor.data_processor_data, np.empty(shape=0))
    assert my_data_processor.raw_file_data is None
    assert my_data_processor.skip_rows == skip_rows
    assert my_data_processor.use_cols_lst == use_cols_lst
    assert my_data_processor.use_rows_lst == use_rows_lst


@pytest.mark.unit_tests
def test_check_valid_filter_options_entire_file():
    """Test checking of valid filter options."""
    DataProcessorCsv._check_valid_filter_options({'type': 'entire_file'})

    with pytest.raises(
        TypeError,
        match="For the filter type `entire_file`, you have to provide a dictionary of type "
        f"{DataProcessorCsv.expected_filter_entire_file}.",
    ):
        DataProcessorCsv._check_valid_filter_options({'type': 'entire_file', 'tolerance': 0})


@pytest.mark.unit_tests
def test_check_valid_filter_options_by_range():
    """Test checking of valid filter by range options."""
    DataProcessorCsv._check_valid_filter_options(
        {'type': 'by_range', 'range': [1.0, 2.0], 'tolerance': 1.0}
    )
    with pytest.raises(
        TypeError,
        match=re.escape(
            "For the filter type `by_range`, you have to provide "
            f"a dictionary of type {DataProcessorCsv.expected_filter_by_range}."
        ),
    ):
        DataProcessorCsv._check_valid_filter_options({'type': 'by_range', 'range': [1.0, 2.0]})


@pytest.mark.unit_tests
def test_check_valid_filter_options_by_row_index():
    """Test checking of valid filter by row index options."""
    DataProcessorCsv._check_valid_filter_options({'type': 'by_row_index', 'rows': [1, 2]})
    with pytest.raises(
        TypeError,
        match=re.escape(
            "For the filter type `by_row_index`, you have to provide "
            f"a dictionary of type {DataProcessorCsv.expected_filter_by_row_index}."
        ),
    ):
        DataProcessorCsv._check_valid_filter_options(
            {'type': 'by_row_index', 'rows': [1, 2], 'tolerance': 1.0}
        )


@pytest.mark.unit_tests
def test_check_valid_filter_options_by_target_values():
    """Test checking of valid filter by target values."""
    DataProcessorCsv._check_valid_filter_options(
        {'type': 'by_target_values', 'target_values': [1.0, 2.0, 3.0], 'tolerance': 1.0}
    )
    with pytest.raises(
        TypeError,
        match=re.escape(
            "For the filter type `by_target_values`, you have to provide "
            f"a dictionary of type {DataProcessorCsv.expected_filter_by_target_values}."
        ),
    ):
        DataProcessorCsv._check_valid_filter_options(
            {'type': 'by_target_values', 'target_values': [1.0, 2.0, 3.0]}
        )


@pytest.mark.unit_tests
def test_from_config_create_data_processor(mocker):
    """Test the config method."""
    mp = mocker.patch(
        'pqueens.data_processor.data_processor_csv_data.DataProcessorCsv.__init__',
        return_value=None,
    )

    post_file_name_identifier = 'dummy_prefix*dummypostfix'
    files_to_be_deleted_regex_lst = []
    driver_name = 'driver'
    header_row = 0
    use_cols_lst = [0, 2, 3]
    skip_rows = 1
    index_column = 0
    filter_type = 'by_row_index'
    use_rows_lst = [1, 3, 4]
    filter_range = []
    filter_target_values = []
    filter_tol = 0.0

    file_options_dict = {
        'header_row': header_row,
        'use_cols_lst': use_cols_lst,
        'skip_rows': skip_rows,
        'use_rows_lst': use_rows_lst,
        'index_column': index_column,
        'files_to_be_deleted_regex_lst': files_to_be_deleted_regex_lst,
        "filter": {"type": filter_type, "rows": use_rows_lst},
    }

    config = {
        'driver': {
            'driver_params': {
                'data_processor': {
                    'post_file_name_identifier': post_file_name_identifier,
                    'file_options_dict': file_options_dict,
                }
            }
        }
    }

    DataProcessorCsv.from_config_create_data_processor(
        config,
        driver_name,
    )
    mp.assert_called_once_with(
        post_file_name_identifier,
        file_options_dict,
        files_to_be_deleted_regex_lst,
        driver_name,
        filter_type,
        header_row,
        use_cols_lst,
        skip_rows,
        index_column,
        use_rows_lst,
        filter_range,
        filter_target_values,
        filter_tol,
    )


@pytest.mark.unit_tests
def test_get_raw_data_from_file_with_index(
    dummy_csv_file, default_data_processor, default_raw_data
):
    """Test get raw data from file with index."""
    default_data_processor.header_row = 0
    default_data_processor.use_cols_lst = [1, 3]
    default_data_processor.skip_rows = 3
    default_data_processor.index_column = 0
    default_data_processor.post_file_path = dummy_csv_file

    default_data_processor._get_raw_data_from_file()

    pd.testing.assert_frame_equal(default_data_processor.raw_file_data, default_raw_data)


@pytest.mark.unit_tests
def test_get_raw_data_from_file_without_index(dummy_csv_file, default_data_processor):
    """Test get raw data from file without setting index."""
    default_data_processor.header_row = 0
    default_data_processor.use_cols_lst = [1, 3]
    default_data_processor.skip_rows = 3
    default_data_processor.index_column = False
    default_data_processor.post_file_path = dummy_csv_file

    default_data_processor._get_raw_data_from_file()

    expected_values = [
        [0.02000, 0.64879],
        [0.04000, 1.15097],
        [0.06000, 1.54266],
        [0.08000, 1.86050],
        [0.10000, 2.12885],
        [0.12000, 2.36284],
        [0.14000, 2.57195],
        [0.16000, 2.76238],
        [0.18000, 2.93828],
        [0.20000, 3.10256],
    ]
    expected_raw_data = pd.DataFrame(
        expected_values, index=np.arange(0, 10), columns=['step', 'd_x']
    )

    pd.testing.assert_frame_equal(default_data_processor.raw_file_data, expected_raw_data)


@pytest.mark.unit_tests
def test_filter_entire_file(default_data_processor, default_raw_data):
    """Test filter entire file."""
    default_data_processor.filter_type = 'entire_file'
    default_data_processor.raw_file_data = default_raw_data

    default_data_processor._filter_and_manipulate_raw_data()

    expected_data = np.array(
        [0.64879, 1.15097, 1.54266, 1.86050, 2.12885, 2.36284, 2.57195, 2.76238, 2.93828, 3.10256]
    ).reshape((10, 1))

    np.testing.assert_allclose(expected_data, default_data_processor.data_processor_data)


@pytest.mark.unit_tests
def test_filter_by_range(default_data_processor, default_raw_data):
    """Test filter by range."""
    default_data_processor.filter_type = 'by_range'
    default_data_processor.filter_range = [0.06, 0.12]
    default_data_processor.filter_tol = 1e-2
    default_data_processor.raw_file_data = default_raw_data

    default_data_processor._filter_and_manipulate_raw_data()

    expected_data = np.array([1.54266, 1.86050, 2.12885, 2.36284]).reshape((4, 1))

    np.testing.assert_allclose(expected_data, default_data_processor.data_processor_data)


@pytest.mark.unit_tests
def test_filter_by_target_values(default_data_processor, default_raw_data):
    """Test filter by target values."""
    default_data_processor.filter_type = 'by_target_values'
    default_data_processor.filter_target_values = [0.06, 0.10, 0.18]
    default_data_processor.filter_tol = 1e-2
    default_data_processor.raw_file_data = default_raw_data

    default_data_processor._filter_and_manipulate_raw_data()

    expected_data = np.array([1.54266, 2.12885, 2.93828]).reshape((3, 1))

    np.testing.assert_allclose(expected_data, default_data_processor.data_processor_data)


@pytest.mark.unit_tests
def test_filter_by_row_index(default_data_processor, default_raw_data):
    """Test filter by row index."""
    default_data_processor.filter_type = 'by_row_index'
    default_data_processor.use_rows_lst = [0, 5, 8]
    default_data_processor.raw_file_data = default_raw_data

    default_data_processor._filter_and_manipulate_raw_data()

    expected_data = np.array([0.64879, 2.36284, 2.93828]).reshape((3, 1))

    np.testing.assert_allclose(expected_data, default_data_processor.data_processor_data)
