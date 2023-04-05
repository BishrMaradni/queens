"""Test Sobol indices estimation for Sobol G function."""
import pickle

import numpy as np

from pqueens import run


def test_sobol_indices_sobol(inputdir, tmp_path):
    """Test Sobol Index iterator with Sobol G-function.

    Including first, second and total order indices. The test should
    converge to the analytical solution defined in the Sobol G-function
    implementation (see *sobol.py*).
    """
    run(inputdir / 'sobol_indices_sobol.yml', tmp_path)

    result_file = tmp_path / 'xxx.pickle'
    with open(result_file, 'rb') as handle:
        results = pickle.load(handle)

    expected_result = dict()

    expected_result["S1"] = np.array(
        [
            0.0223308716,
            0.1217603520,
            0.0742536887,
            0.0105281513,
            0.0451664441,
            0.0103643039,
            -0.0243893613,
            -0.0065963022,
            0.0077115277,
            0.0087332959,
        ]
    )
    expected_result["S1_conf"] = np.array(
        [
            0.0805685374,
            0.3834399385,
            0.0852274149,
            0.0455336021,
            0.0308612621,
            0.0320150143,
            0.0463744331,
            0.0714009860,
            0.0074505447,
            0.0112548095,
        ]
    )

    expected_result["ST"] = np.array(
        [
            0.7680857789,
            0.4868735760,
            0.3398667460,
            0.2119195462,
            0.2614132922,
            0.3189091311,
            0.6505384437,
            0.2122730632,
            0.0091166496,
            0.0188473672,
        ]
    )

    expected_result["ST_conf"] = np.array(
        [
            0.3332995622,
            0.6702803374,
            0.3789328006,
            0.1061256016,
            0.1499369465,
            0.2887465421,
            0.4978127348,
            0.7285189769,
            0.0088588230,
            0.0254845356,
        ]
    )

    expected_result["S2"] = np.array(
        [
            [
                np.nan,
                0.1412835702,
                -0.0139270230,
                -0.0060290464,
                0.0649029079,
                0.0029081424,
                0.0711209478,
                0.0029761017,
                -0.0040965718,
                0.0020644536,
            ],
            [
                np.nan,
                np.nan,
                -0.0995909726,
                -0.0605137390,
                -0.1084396644,
                -0.0723118849,
                -0.0745624634,
                -0.0774015700,
                -0.0849434447,
                -0.0839125029,
            ],
            [
                np.nan,
                np.nan,
                np.nan,
                -0.0246418033,
                -0.0257497932,
                -0.0193201341,
                -0.0077236185,
                -0.0330585164,
                -0.0345501232,
                -0.0302764363,
            ],
            [
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                0.0311150448,
                0.0055202682,
                0.0033339784,
                -0.0030970794,
                -0.0072451869,
                -0.0063212065,
            ],
            [
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                0.0028320819,
                -0.0104508084,
                -0.0052688338,
                -0.0078624231,
                -0.0076410622,
            ],
            [
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                0.0030222662,
                0.0027860256,
                0.0028227848,
                0.0035368873,
            ],
            [
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                0.0201030574,
                0.0210914390,
                0.0202893663,
            ],
            [
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                0.0078664740,
                0.0106712221,
            ],
            [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, -0.0102325515],
            [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ]
    )

    expected_result["S2_conf"] = np.array(
        [
            [
                np.nan,
                0.9762064146,
                0.1487396176,
                0.1283905049,
                0.2181870269,
                0.1619544753,
                0.1565960033,
                0.1229244812,
                0.1309522579,
                0.1455652199,
            ],
            [
                np.nan,
                np.nan,
                0.3883751512,
                0.3554957308,
                0.3992635683,
                0.4020261874,
                0.3767426554,
                0.3786542992,
                0.3790355847,
                0.3889345096,
            ],
            [
                np.nan,
                np.nan,
                np.nan,
                0.0758005266,
                0.0737757790,
                0.0738589320,
                0.1032391772,
                0.0713230587,
                0.0806156892,
                0.0847106864,
            ],
            [
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                0.1018303925,
                0.1047654360,
                0.0683036422,
                0.0874356406,
                0.1080467182,
                0.1046926153,
            ],
            [
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                0.0415102405,
                0.0337889266,
                0.0301212961,
                0.0355450299,
                0.0353899382,
            ],
            [
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                0.0392075204,
                0.0454072312,
                0.0464493854,
                0.0440356854,
            ],
            [
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                0.0825175719,
                0.0821124198,
                0.0790512360,
            ],
            [
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                0.0685979162,
                0.0668528158,
            ],
            [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 0.0295934940],
            [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        ]
    )
    np.testing.assert_allclose(results["sensitivity_indices"]["S1"], expected_result["S1"])
    np.testing.assert_allclose(
        results["sensitivity_indices"]["S1_conf"], expected_result["S1_conf"]
    )

    np.testing.assert_allclose(results["sensitivity_indices"]["ST"], expected_result["ST"])
    np.testing.assert_allclose(
        results["sensitivity_indices"]["ST_conf"], expected_result["ST_conf"]
    )

    np.testing.assert_allclose(results["sensitivity_indices"]["S2"], expected_result["S2"])
    np.testing.assert_allclose(
        results["sensitivity_indices"]["S2_conf"], expected_result["S2_conf"]
    )
