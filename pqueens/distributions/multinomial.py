"""Multinomial distribution."""
import numpy as np
from scipy.stats import multinomial

from pqueens.distributions.distributions import DiscreteDistribution


class MultinomialDistribution(DiscreteDistribution):
    """Multinomial distribution."""

    def __init__(self, n_trials, probabilities):
        """Initialize discrete uniform distribution.

        Args:
            probabilities (np.ndarray): Probabilities associated to all the events in the sample
                                        space
            n_trials (int): Number of trials, i.e. the value to which every multivariate sample
                            adds up to.
        """
        if not isinstance(n_trials, int) or n_trials <= 0:
            raise ValueError(f"n_trials was set to {n_trials} needs to be a positive integer.")

        self.n_trials = n_trials

        # we misuse the sample_space attribute of the base class to store the number of trials
        sample_space = np.ones((len(probabilities), 1)) * self.n_trials
        super().__init__(probabilities, sample_space, dimension=len(probabilities))
        self.scipy_multinomial = multinomial(self.n_trials, self.probabilities)

    @staticmethod
    def _compute_mean_and_covariance(probabilities, sample_space):
        """Compute the mean value and covariance of the mixture model.

        Args:
            probabilities (np.ndarray): Probabilities associated to all the events in the sample
                                        space
            sample_space (np.ndarray): Samples, i.e. possible outcomes of sampling the distribution

        Returns:
            mean (np.ndarray): Mean value of the distribution
            covariance (np.ndarray): Covariance of the distribution
        """
        n_trials = sample_space[0]
        mean = n_trials * probabilities
        covariance = n_trials * (np.diag(probabilities) - np.outer(probabilities, probabilities))
        return mean, covariance

    def draw(self, num_draws=1):
        """Draw samples.

        Args:
            num_draws (int, optional): Number of draws
        """
        return np.random.multinomial(self.n_trials, self.probabilities, size=num_draws)

    def logpdf(self, x):
        """Log of the probability mass function.

        Args:
            x (np.ndarray): Positions at which the log pdf is evaluated
        """
        return self.scipy_multinomial.logpmf(x)

    def pdf(self, x):
        """Probability mass function.

        Args:
            x (np.ndarray): Positions at which the pdf is evaluated
        """
        return self.scipy_multinomial.pmf(x)

    def cdf(self, x):  # pylint: disable=invalid-name
        """Cumulative distribution function.

        Args:
            x (np.ndarray): Positions at which the cdf is evaluated
        """
        super().check_1d()

    def ppf(self, q):  # pylint: disable=invalid-name
        """Percent point function (inverse of cdf - quantiles).

        Args:
            q (np.ndarray): Quantiles at which the ppf is evaluated
        """
        super().check_1d()
