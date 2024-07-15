"""Integration test for GPflow based GP model."""
import numpy as np
import pytest

from queens.distributions.uniform import UniformDistribution
from queens.interfaces.direct_python_interface import DirectPythonInterface
from queens.iterators.monte_carlo_iterator import MonteCarloIterator
from queens.main import run_iterator
from queens.models.simulation_model import SimulationModel
from queens.models.surrogate_models.gp_approximation_gpflow import GPFlowRegressionModel
from queens.parameters.parameters import Parameters
from queens.utils.io_utils import load_result


def test_gpflow_surrogate_branin(
    tmp_path,
    expected_mean,
    expected_variance,
    expected_posterior_samples,
    _initialize_global_settings,
):
    """Test case for GPflow based GP model."""
    # Parameters
    x1 = UniformDistribution(lower_bound=-5, upper_bound=10)
    x2 = UniformDistribution(lower_bound=0, upper_bound=15)
    parameters = Parameters(x1=x1, x2=x2)

    # Setup QUEENS stuff
    interface = DirectPythonInterface(function="branin78_hifi", parameters=parameters)
    model = SimulationModel(interface=interface)
    training_iterator = MonteCarloIterator(
        seed=42,
        num_samples=20,
        model=model,
        parameters=parameters,
        global_settings=_initialize_global_settings,
    )
    model = GPFlowRegressionModel(
        train_likelihood_variance=False,
        number_restarts=5,
        number_training_iterations=1000,
        number_posterior_samples=3,
        seed_posterior_samples=42,
        dimension_lengthscales=2,
        plotting_options={
            "plot_booleans": [False, False],
            "plotting_dir": "dummy",
            "plot_names": ["1D", "2D"],
            "save_bool": [False, False],
        },
        training_iterator=training_iterator,
    )
    iterator = MonteCarloIterator(
        seed=44,
        num_samples=10,
        result_description={
            "write_results": True,
            "plot_results": False,
            "bayesian": False,
            "num_support_points": 10,
            "estimate_all": False,
        },
        model=model,
        parameters=parameters,
        global_settings=_initialize_global_settings,
    )

    # Actual analysis
    run_iterator(iterator, global_settings=_initialize_global_settings)

    # Load results
    result_file = tmp_path / "dummy_experiment_name.pickle"
    results = load_result(result_file)

    np.testing.assert_array_almost_equal(
        results["raw_output_data"]["result"], expected_mean, decimal=3
    )
    np.testing.assert_array_almost_equal(
        results["raw_output_data"]["variance"], expected_variance, decimal=2
    )
    np.testing.assert_array_almost_equal(
        results["raw_output_data"]["post_samples"], expected_posterior_samples, decimal=2
    )


@pytest.fixture(name="expected_mean")
def fixture_expected_mean():
    """Expected mean."""
    expected_mean = np.array(
        [
            [127.97233506],
            [39.73551321],
            [47.00641347],
            [28.88934819],
            [22.40199886],
            [150.69211917],
            [104.25630329],
            [92.22700928],
            [50.69060622],
            [22.18886383],
        ]
    )
    return expected_mean


@pytest.fixture(name="expected_variance")
def fixture_expected_variance():
    """Expected variance."""
    expected_variance = np.array(
        [
            [788.8004288],
            [1.8365012],
            [2.25043994],
            [4.24878946],
            [1.97026586],
            [174.50881662],
            [14.06623098],
            [8.34025715],
            [0.95922611],
            [0.33420735],
        ]
    )
    return expected_variance


@pytest.fixture(name="expected_posterior_samples")
def fixture_expected_posterior_samples():
    """Expected posterior samples."""
    expected_posterior_samples = np.array(
        [
            [1.890, 0.136, 2.294, -0.231, 0.461, 4.178, 0.695, 0.284, -0.265, 1.990],
            [0.375, -0.206, 1.942, 3.694, -0.037, 2.271, -0.222, 0.584, 3.734, 0.643],
            [0.444, 3.226, 0.662, 0.309, -0.227, 1.903, 2.412, -0.030, 2.387, -0.266],
        ]
    )
    return expected_posterior_samples.transpose()
