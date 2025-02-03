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
"""Unit tests for the finite difference model."""

import numpy as np
import pytest
from mock import Mock

from queens.models.differentiable_simulation_model_fd import DifferentiableSimulationModelFD
from queens.models.model import Model
from queens.utils.valid_options_utils import InvalidOptionError


# ------------------ some fixtures ------------------------------- #
@pytest.fixture(name="default_fd_model")
def fixture_default_fd_model():
    """A default finite difference model."""
    model_obj = DifferentiableSimulationModelFD(
        scheduler=Mock(),
        driver=Mock(),
        finite_difference_method="2-point",
    )
    return model_obj


# ------------------ actual unit tests --------------------------- #
def test_init():
    """Test the init method of the finite difference model."""
    scheduler = Mock()
    driver = Mock()
    finite_difference_method = "3-point"
    step_size = 1e-6
    bounds = [-10, np.inf]

    model_obj = DifferentiableSimulationModelFD(
        scheduler=scheduler,
        driver=driver,
        finite_difference_method=finite_difference_method,
        step_size=step_size,
        bounds=bounds,
    )
    assert model_obj.scheduler == scheduler
    assert model_obj.driver == driver
    assert model_obj.finite_difference_method == finite_difference_method
    assert model_obj.step_size == step_size
    np.testing.assert_equal(model_obj.bounds, np.array(bounds))

    with pytest.raises(InvalidOptionError):
        DifferentiableSimulationModelFD(
            scheduler=scheduler,
            driver=driver,
            finite_difference_method="invalid_method",
            step_size=step_size,
        )


def test_evaluate(default_fd_model):
    """Test the evaluation method."""
    default_fd_model.scheduler.evaluate = lambda x, driver: {
        "result": np.sum(x**2, axis=1, keepdims=True)
    }
    samples = np.random.random((3, 2))

    expected_mean = np.sum(samples**2, axis=1, keepdims=True)
    expected_grad = 2 * samples[:, np.newaxis, :]

    response = default_fd_model.evaluate(samples)
    assert len(response) == 1
    np.testing.assert_array_equal(response["result"], expected_mean)
    assert len(default_fd_model.response) == 1
    np.testing.assert_array_equal(default_fd_model.response["result"], expected_mean)

    Model.evaluate_and_gradient_bool = False
    response = default_fd_model.evaluate(samples)
    assert len(response) == 1
    np.testing.assert_array_equal(response["result"], expected_mean)
    assert len(default_fd_model.response) == 1
    np.testing.assert_array_equal(default_fd_model.response["result"], expected_mean)

    Model.evaluate_and_gradient_bool = True
    response = default_fd_model.evaluate(samples)
    np.testing.assert_array_almost_equal(expected_mean, response["result"], decimal=5)
    np.testing.assert_array_almost_equal(expected_grad, response["gradient"], decimal=5)

    default_fd_model.scheduler.evaluate = lambda x, driver: {
        "result": np.array([np.sum(x**2, axis=1), np.sum(2 * x**2, axis=1)]).T
    }
    samples = np.random.random((3, 4))

    expected_grad = np.swapaxes(np.array([2 * samples, 4 * samples]), 0, 1)
    expected_mean = np.array([np.sum(samples**2, axis=1), np.sum(2 * samples**2, axis=1)]).T
    response = default_fd_model.evaluate(samples)
    np.testing.assert_array_almost_equal(expected_mean, response["result"], decimal=5)
    np.testing.assert_array_almost_equal(expected_grad, response["gradient"], decimal=4)
    Model.evaluate_and_gradient_bool = False


def test_grad(default_fd_model):
    """Test grad method."""
    np.random.seed(42)
    samples = np.random.random((2, 4, 3))
    default_fd_model.response = {
        "result": np.sum(samples**2, axis=2, keepdims=True),
        "gradient": 2 * samples,
    }
    upstream_gradient = np.random.random((2, 1))
    expected_grad = np.sum(
        upstream_gradient[:, :, np.newaxis] * default_fd_model.response["gradient"], axis=1
    )
    grad_out = default_fd_model.grad(samples, upstream_gradient)
    np.testing.assert_almost_equal(expected_grad, grad_out)
