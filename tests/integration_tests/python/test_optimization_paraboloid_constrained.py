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
"""Integration test for the Optimization iterator.

This test uses different solution algorithms.
"""

import numpy as np
import pytest

from queens.distributions.free_variable import FreeVariable
from queens.drivers.function_driver import FunctionDriver
from queens.iterators.optimization_iterator import OptimizationIterator
from queens.main import run_iterator
from queens.models.simulation_model import SimulationModel
from queens.parameters.parameters import Parameters
from queens.schedulers.pool_scheduler import PoolScheduler
from queens.utils.io_utils import load_result


@pytest.fixture(name="algorithm", params=["COBYLA", "SLSQP"])
def fixture_algorithm(request):
    """Different optimization algorithms."""
    return request.param


def test_optimization_paraboloid_constrained(algorithm, global_settings):
    """Test different solution algorithms in optimization iterator.

    COBYLA: constrained but unbounded

    SLSQP:  constrained and bounded
    """
    # Parameters
    x1 = FreeVariable(dimension=1)
    x2 = FreeVariable(dimension=1)
    parameters = Parameters(x1=x1, x2=x2)

    # Setup iterator
    driver = FunctionDriver(parameters=parameters, function="paraboloid")
    scheduler = PoolScheduler(experiment_name=global_settings.experiment_name)
    model = SimulationModel(scheduler=scheduler, driver=driver)
    iterator = OptimizationIterator(
        initial_guess=[2.0, 0.0],
        algorithm=algorithm,
        result_description={"write_results": True, "plot_results": True},
        bounds=[[0.0, 0.0], float("inf")],
        constraints={
            "cons1": {"type": "ineq", "fun": "lambda x:  x[0] - 2 * x[1] + 2"},
            "cons2": {"type": "ineq", "fun": "lambda x: -x[0] - 2 * x[1] + 6"},
            "cons3": {"type": "ineq", "fun": "lambda x: -x[0] + 2 * x[1] + 2"},
        },
        model=model,
        parameters=parameters,
        global_settings=global_settings,
    )

    # Actual analysis
    run_iterator(iterator, global_settings=global_settings)

    # Load results
    results = load_result(global_settings.result_file(".pickle"))

    np.testing.assert_allclose(results.x, np.array([+1.4, +1.7]), rtol=1.0e-4)
    np.testing.assert_allclose(results.fun, np.array(+0.8), atol=1.0e-07)
