"""Test Sobol indices estimation for borehole function."""

import numpy as np

from queens.distributions.uniform import UniformDistribution
from queens.drivers.function_driver import FunctionDriver
from queens.interfaces.job_interface import JobInterface
from queens.iterators.sobol_index_iterator import SobolIndexIterator
from queens.main import run_iterator
from queens.models.simulation_model import SimulationModel
from queens.parameters.parameters import Parameters
from queens.schedulers.pool_scheduler import PoolScheduler
from queens.utils.io_utils import load_result


def test_sobol_indices_borehole(global_settings):
    """Test case for Sobol Index iterator."""
    # Parameters
    rw = UniformDistribution(lower_bound=0.05, upper_bound=0.15)
    r = UniformDistribution(lower_bound=100, upper_bound=50000)
    tu = UniformDistribution(lower_bound=63070, upper_bound=115600)
    hu = UniformDistribution(lower_bound=990, upper_bound=1110)
    tl = UniformDistribution(lower_bound=63.1, upper_bound=116)
    hl = UniformDistribution(lower_bound=700, upper_bound=820)
    l = UniformDistribution(lower_bound=1120, upper_bound=1680)
    kw = UniformDistribution(lower_bound=9855, upper_bound=12045)
    parameters = Parameters(rw=rw, r=r, tu=tu, hu=hu, tl=tl, hl=hl, l=l, kw=kw)

    # Setup iterator
    driver = FunctionDriver(function="borehole83_lofi")
    scheduler = PoolScheduler(experiment_name=global_settings.experiment_name, num_workers=2)
    interface = JobInterface(parameters=parameters, scheduler=scheduler, driver=driver)
    model = SimulationModel(interface=interface)
    iterator = SobolIndexIterator(
        seed=42,
        calc_second_order=True,
        num_samples=1024,
        confidence_level=0.95,
        num_bootstrap_samples=1000,
        result_description={"write_results": True, "plot_results": False},
        model=model,
        parameters=parameters,
        global_settings=global_settings,
    )

    # Actual analysis
    run_iterator(iterator, global_settings=global_settings)

    # Load results
    results = load_result(global_settings.result_file(".pickle"))

    expected_first_order_indices = np.array(
        [
            0.8275788005095177,
            3.626326582692376e-05,
            1.7993448562887368e-09,
            0.04082350205109995,
            -1.0853339811788176e-05,
            0.0427473897346278,
            0.038941629762778956,
            0.009001905983634081,
        ]
    )

    np.testing.assert_allclose(results["sensitivity_indices"]["S1"], expected_first_order_indices)
