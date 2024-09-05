"""Integration test for the classification iterator."""

import numpy as np
from sklearn.neural_network._multilayer_perceptron import MLPClassifier

from queens.distributions.uniform import UniformDistribution
from queens.drivers.function_driver import FunctionDriver
from queens.interfaces.job_interface import JobInterface
from queens.iterators.classification import ClassificationIterator
from queens.main import run_iterator
from queens.models.simulation_model import SimulationModel
from queens.parameters.parameters import Parameters
from queens.schedulers.pool_scheduler import PoolScheduler
from queens.utils.classifier import ActiveLearningClassifier
from queens.utils.io_utils import load_result


def test_classification_iterator(tmp_path, global_settings):
    """Integration test for the classification iterator."""

    def classification_function(x):
        """Classification function.

        Classes are defined in the following way:
        1 or True if the value of x is larger than a threshold.
        0 or False if the value of x is smaller than equal to a threshold.

        Args:
            x (np.array): unclassified data
        Returns:
             classified data (np.array)
        """
        return x > 80

    # Parameters
    x1 = UniformDistribution(lower_bound=-2, upper_bound=2)
    x2 = UniformDistribution(lower_bound=-2, upper_bound=2)
    parameters = Parameters(x1=x1, x2=x2)

    # Setup iterator
    classifier_obj = MLPClassifier()
    classifier = ActiveLearningClassifier(n_params=2, batch_size=4, classifier_obj=classifier_obj)
    driver = FunctionDriver(function="rosenbrock60")
    scheduler = PoolScheduler(experiment_name=global_settings.experiment_name)
    interface = JobInterface(parameters=parameters, scheduler=scheduler, driver=driver)
    model = SimulationModel(interface=interface)
    iterator = ClassificationIterator(
        num_sample_points=10000,
        num_model_calls=12,
        random_sampling_frequency=2,
        seed=42,
        result_description={
            "write_results": True,
            "plotting_options": {
                "plot_bool": False,
                "plotting_dir": tmp_path,
                "plot_name": "neural_classifier_convergence_plot",
                "save_bool": True,
            },
        },
        classification_function=classification_function,
        classifier=classifier,
        model=model,
        parameters=parameters,
        global_settings=global_settings,
    )

    # Actual analysis
    run_iterator(iterator, global_settings=global_settings)

    # Load results
    results = load_result(global_settings.result_file(".pickle"))

    expected_results_classified = np.ones((12, 1))
    expected_results_classified[-2:] = 0
    expected_samples = np.array(
        [
            [-1.08480734, -0.7215275],
            [0.47755988, -1.70552695],
            [1.2057831, -0.18745467],
            [-0.82740908, -1.73532511],
            [-0.60210352, 1.98595546],
            [-0.66345435, 1.99530424],
            [-0.46880494, 1.98952451],
            [-0.31552438, 1.98624568],
            [-0.86489638, -0.2715313],
            [1.87330784, 1.77265221],
            [0.88234568, 0.14938235],
            [0.3827193, 0.81934479],
        ]
    )
    obtained_results = results["classified_outputs"]
    obtained_samples = results["input_samples"]
    np.testing.assert_array_almost_equal(expected_samples, obtained_samples)
    np.testing.assert_array_equal(expected_results_classified, obtained_results)
