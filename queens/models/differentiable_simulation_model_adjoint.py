"""Adjoint model."""

import logging

from queens.models.simulation_model import SimulationModel
from queens.utils.config_directories import current_job_directory
from queens.utils.io_utils import write_to_csv
from queens.utils.logger_settings import log_init_args

_logger = logging.getLogger(__name__)


class DifferentiableSimulationModelAdjoint(SimulationModel):
    """Adjoint model.

    Attributes:
        adjoint_file (str): Name of the adjoint file that contains the evaluated derivative of the
                            functional w.r.t. to the simulation output.
        gradient_interface (obj): Interface object for the adjoint simulation run.
    """

    @log_init_args
    def __init__(
        self,
        interface,
        gradient_interface,
        adjoint_file="adjoint_grad_objective.csv",
    ):
        """Initialize model.

        Args:
            interface (obj): Interface object for forward simulation run
            gradient_interface (obj): Interface object for the adjoint simulation run.
            adjoint_file (str): Name of the adjoint file that contains the evaluated derivative of
                                the functional w.r.t. to the simulation output.
        """
        super().__init__(interface)
        self.gradient_interface = gradient_interface
        self.adjoint_file = adjoint_file

    def evaluate(self, samples):
        """Evaluate model with current set of input samples.

        Args:
            samples (np.ndarray): Input samples

        Returns:
            response (dict): Response of the underlying model at input samples
        """
        self.response = self.interface.evaluate(samples)
        return self.response

    def grad(self, samples, upstream_gradient):
        r"""Evaluate gradient of model w.r.t. current set of input samples.

        Consider current model f(x) with input samples x, and upstream function g(f). The provided
        upstream gradient is :math:`\frac{\partial g}{\partial f}` and the method returns
        :math:`\frac{\partial g}{\partial f} \frac{df}{dx}`.

        Args:
            samples (np.array): Input samples
            upstream_gradient (np.array): Upstream gradient function evaluated at input samples
                                          :math:`\frac{\partial g}{\partial f}`

        Returns:
            gradient (np.array): Gradient w.r.t. current set of input samples
                                 :math:`\frac{\partial g}{\partial f} \frac{df}{dx}`
        """
        num_samples = samples.shape[0]
        # get last job_ids
        last_job_ids = [
            self.interface.latest_job_id - num_samples + i + 1 for i in range(num_samples)
        ]
        experiment_dir = self.gradient_interface.scheduler.experiment_dir

        # write adjoint data for each sample to adjoint files in old job directories
        for job_id, grad_objective in zip(last_job_ids, upstream_gradient):
            job_dir = current_job_directory(experiment_dir, job_id)
            adjoint_file_path = job_dir.joinpath(self.adjoint_file)
            write_to_csv(adjoint_file_path, grad_objective.reshape(1, -1))

        # evaluate the adjoint model
        gradient = self.gradient_interface.evaluate(samples)['result']
        return gradient
