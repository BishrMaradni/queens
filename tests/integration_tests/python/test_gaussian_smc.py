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
"""Integration test for the Sequential Monte Carlo iterator.

This test uses Gaussian likelihood.
"""

import numpy as np
from mock import patch

from queens.distributions.normal import Normal
from queens.drivers.function import Function
from queens.iterators.metropolis_hastings import MetropolisHastings
from queens.iterators.sequential_monte_carlo import SequentialMonteCarlo
from queens.main import run_iterator
from queens.models.likelihoods.gaussian import Gaussian
from queens.models.simulation import Simulation
from queens.parameters.parameters import Parameters
from queens.schedulers.pool import Pool
from queens.utils.experimental_data_reader import ExperimentalDataReader
from queens.utils.io import load_result


def test_gaussian_smc(
    tmp_path,
    target_density_gaussian_1d,
    _create_experimental_data_gaussian_1d,
    global_settings,
):
    """Test Sequential Monte Carlo with univariate Gaussian."""
    # Parameters
    x = Normal(mean=2.0, covariance=1.0)
    parameters = Parameters(x=x)

    # Setup iterator
    experimental_data_reader = ExperimentalDataReader(
        file_name_identifier="*.csv",
        csv_data_base_dir=tmp_path,
        output_label="y_obs",
    )
    mcmc_proposal_distribution = Normal(mean=0.0, covariance=1.0)
    driver = Function(parameters=parameters, function="patch_for_likelihood")
    scheduler = Pool(experiment_name=global_settings.experiment_name)
    forward_model = Simulation(scheduler=scheduler, driver=driver)
    model = Gaussian(
        noise_type="fixed_variance",
        noise_value=1.0,
        experimental_data_reader=experimental_data_reader,
        forward_model=forward_model,
    )
    iterator = SequentialMonteCarlo(
        seed=42,
        num_particles=10,
        temper_type="bayes",
        plot_trace_every=0,
        num_rejuvenation_steps=3,
        result_description={"write_results": True, "plot_results": True, "cov": False},
        mcmc_proposal_distribution=mcmc_proposal_distribution,
        model=model,
        parameters=parameters,
        global_settings=global_settings,
    )

    # Actual analysis
    # mock methods related to likelihood
    with patch.object(SequentialMonteCarlo, "eval_log_likelihood", target_density_gaussian_1d):
        with patch.object(MetropolisHastings, "eval_log_likelihood", target_density_gaussian_1d):
            run_iterator(iterator, global_settings=global_settings)

    # Load results
    results = load_result(global_settings.result_file(".pickle"))
    # note that the analytical solution would be:
    # posterior mean: [1.]
    # posterior var: [0.5]
    # posterior std: [0.70710678]
    # however, we only have a very inaccurate approximation here:
    np.testing.assert_almost_equal(results["mean"], np.array([[0.93548976]]), decimal=7)
    np.testing.assert_almost_equal(results["var"], np.array([[0.72168334]]), decimal=7)
