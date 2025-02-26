#
# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (c) 2024-2025, QUEENS contributors.
#
# This file is part of QUEENS.
#
# QUEENS is free software: you can redistribute it and/or modify it under the terms of the GNU
# Lesser General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version. QUEENS is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details. You
# should have received a copy of the GNU Lesser General Public License along with QUEENS. If not,
# see <https://www.gnu.org/licenses/>.
#
"""Test for the Latin Hyper Cube iterator.

The test is based on the high-fidelity Branin function.
"""

import pytest

from queens.distributions.uniform import Uniform
from queens.drivers.function import Function
from queens.iterators.latin_hypercube_sampling import LatinHypercubeSampling
from queens.main import run_iterator
from queens.models.simulation import Simulation
from queens.parameters.parameters import Parameters
from queens.schedulers.pool_scheduler import PoolScheduler
from queens.utils.io_utils import load_result


@pytest.mark.max_time_for_test(20)
def test_branin_latin_hyper_cube(global_settings):
    """Test case for latin hyper cube iterator."""
    # Parameters
    x1 = Uniform(lower_bound=-5, upper_bound=10)
    x2 = Uniform(lower_bound=0, upper_bound=15)
    parameters = Parameters(x1=x1, x2=x2)

    # Setup iterator
    driver = Function(parameters=parameters, function="branin78_hifi")
    scheduler = PoolScheduler(experiment_name=global_settings.experiment_name)
    model = Simulation(scheduler=scheduler, driver=driver)
    iterator = LatinHypercubeSampling(
        seed=42,
        num_samples=1000,
        num_iterations=10,
        result_description={"write_results": True, "plot_results": False},
        model=model,
        parameters=parameters,
        global_settings=global_settings,
    )

    # Actual analysis
    run_iterator(iterator, global_settings=global_settings)

    # Load results
    results = load_result(global_settings.result_file(".pickle"))

    assert results["mean"] == pytest.approx(53.17279969296224)
    assert results["var"] == pytest.approx(2581.6502630157715)
