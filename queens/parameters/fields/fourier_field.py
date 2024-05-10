"""Fourier Random fields class."""

import numpy as np
from scipy.spatial import ConvexHull  # pylint: disable=no-name-in-module
from scipy.spatial.distance import pdist

from queens.distributions.mean_field_normal import MeanFieldNormalDistribution
from queens.parameters.fields.random_fields import RandomField


class FourierRandomField(RandomField):
    """FOURIER expansion of random fields class.

    Attributes:
        mean (np.array): Mean vector at nodes
        std (float): Hyperparameter for standard-deviation of random field
        corr_length (float): Hyperparameter for the correlation length
        variability (float): Explained variance by the fourier decomposition
        trunc_threshold (int): Truncation threshold for Fourier series
        basis_dimension (int) : Dimension of the complete Fourier basis up to the truncation
                                threshold (not the latent space)
        latent_index (np.array): Index array mapping latent space variables to covariance values
        covariance_index (np.array): Array indexing the covariance values below the
                                     truncation threshold
        covariance (np.array): Fourier transformed covariance kernel
        basis (np.array): Inverse cosine transformed fourier basis
        coordinates (np.array): Vector of all coordinates in random field
        field_dimension (int): Physical dimension of the random field
        number_expansion_terms (int): Number of frequencies in all directions
        dimension (int): Dimension of latent space
        convex_hull_size (float): Eucledian distance between furthest apart coordinates in the field
    """

    def __init__(
        self,
        coords,
        mean=0.0,
        std=1.0,
        corr_length=0.3,
        variability=0.98,
        trunc_threshold=64,
    ):
        """Initialize Fourier object.

        Args:
            coords (dict): Dictionary with coordinates of discretized random field and the
                           corresponding keys
            mean (np.array): Mean vector at nodes
            std (float): Hyperparameter for standard-deviation of random field
            corr_length (float): Hyperparameter for the correlation length
            variability (float): Explained variance of by the eigen
            trunc_threshold (int): Truncation threshold for Fourier series.
        """
        super().__init__(coords)
        self.mean = mean
        self.std = std
        self.corr_length = corr_length
        self.variability = variability
        self.trunc_threshold = trunc_threshold

        self.covariance = None
        self.basis = None
        self.coordinates = self.coords['coords']

        self.field_dimension = self.coordinates.shape[1]
        if self.field_dimension == 1:
            dimension_methods_class = DimensionMethods1D
        elif self.field_dimension == 2:
            dimension_methods_class = DimensionMethods2D
        elif self.field_dimension == 3:
            dimension_methods_class = DimensionMethods3D
        else:
            raise ValueError("Only 1D, 2D or 3D fields are supported by Fourier expansion")

        # find max length in coords
        if self.field_dimension == 1:
            self.convex_hull_size = self.coordinates.max() - self.coordinates.min()

        else:
            convex_hull = ConvexHull(self.coordinates)
            hull_coords = self.coordinates[convex_hull.vertices]
            self.convex_hull_size = pdist(hull_coords).max()

        if self.corr_length / self.convex_hull_size > 0.35:
            raise ValueError("Correlation length too large, not a good approximation.")

        self.number_expansion_terms = int(np.sqrt(self.trunc_threshold)) + 1
        (
            self.covariance_index,
            self.latent_index,
            self.basis_dimension,
            self.dimension,
        ) = dimension_methods_class.get_dim(self.trunc_threshold, self.number_expansion_terms)
        self.covariance = dimension_methods_class.calculate_covariance(
            self.number_expansion_terms, self.corr_length, self.convex_hull_size
        )
        self.check_convergence()
        self.basis = dimension_methods_class.calculate_basis(
            self.coordinates,
            self.basis_dimension,
            self.number_expansion_terms,
            self.convex_hull_size,
            self.covariance,
            self.latent_index,
        )

        self.distribution = MeanFieldNormalDistribution(
            mean=0, variance=1, dimension=self.dimension
        )

    def draw(self, num_samples):
        """Draw samples from the latent representation of the random field.

        Args:
            num_samples: Number of draws of latent random samples
        Returns:
            samples (np.ndarray): Drawn samples
        """
        return self.distribution.draw(num_samples)

    def logpdf(self, samples):
        """Get joint logpdf of latent space.

        Args:
            samples (np.array): Samples for evaluating the logpdf

        Returns:
            logpdf (np.array): Logpdf of the samples
        """
        logpdf = self.distribution.logpdf(samples)
        return logpdf

    def grad_logpdf(self, samples):
        """Get gradient of joint logpdf of latent space.

        Args:
            samples (np.array): Samples for evaluating the gradient of the logpdf

        Returns:
            gradient (np.array): Gradient of the logpdf
        """
        gradient = self.distribution.grad_logpdf(samples)
        return gradient

    def expanded_representation(self, samples):
        """Expand latent representation of sample.

        Args:
            samples (np.ndarray): Latent representation of sample

        Returns:
            sample_expanded (np.ndarray): Expanded representation of samples
        """
        sample_expanded = self.mean + self.std * np.matmul(samples, self.basis.T)
        return sample_expanded

    def latent_gradient(self, upstream_gradient):
        """Gradient with respect to the latent parameters.

        Args:
            upstream_gradient (np.ndarray): Gradient with respect to all coords of the field

        Returns:
            latent_grad (np.ndarray): Gradient of the realization of the random field with
                                      respect to the latent space variables
        """
        latent_grad = self.std * np.matmul(upstream_gradient, self.basis)
        return latent_grad

    def check_convergence(self):
        """Check if truncated terms converge to variability."""
        if np.sum(self.covariance[self.covariance_index]) < self.variability:
            raise ValueError("Variability not covered, increase number of expansion terms")


class DimensionMethods1D:
    """1D FOURIER expansion helper methods."""

    @staticmethod
    def get_dim(trunc_threshold, number_expansion_terms):
        """Calculate dimension of latent space.

        Args:
            trunc_threshold (int): Truncation threshold
            number_expansion_terms (int): Number of frequencies in the expansion

        Returns:
            covariance_index (np.array): Array indexing the covariance values below the truncation
                                         limit
            latent_index (np.array): Array indexing the basis terms corresponding to valid
                                     covariance values
            basis_dimension (int): Dimension of the complete Fourier basis up to the truncation
                                   threshold
            dimension (int): Dimension of the latent space
        """
        basis_dimension = int(2 * number_expansion_terms)
        wave_numbers = (
            np.linspace(0, number_expansion_terms - 1, number_expansion_terms, dtype=int) ** 2
        )
        dim_one_wave_numbers = wave_numbers
        index = dim_one_wave_numbers
        covariance_index = index <= trunc_threshold
        latent_index = np.kron(covariance_index, np.ones(shape=(2,))).astype(bool)
        dimension = np.sum(latent_index, dtype=int)

        return covariance_index, latent_index, basis_dimension, dimension

    @staticmethod
    def calculate_covariance(number_expansion_terms, corr_length, convex_hull_size):
        """Calculate discrete fourier transform of the covariance kernel.

        Based on the kernel description of the random field, build its
        covariance matrix using the external geometry and coordinates.

        Args:
            number_expansion_terms (int): Number of frequencies
            corr_length (float): Typical length in the field
            convex_hull_size  (float): Max distance on the grid

        Returns:
            covariance (np.array): Cosine transform of covariance matrix
        """
        c_k = np.linspace(0, number_expansion_terms - 1, number_expansion_terms)
        c_k = (
            corr_length
            * np.sqrt(np.pi)
            / convex_hull_size
            * np.exp(-((c_k * np.pi * corr_length) ** 2) / (2 * convex_hull_size) ** 2)
        )
        c_k[0] = corr_length * np.sqrt(np.pi) / (2 * convex_hull_size)
        covariance = np.sqrt(c_k)
        return covariance

    @staticmethod
    def calculate_basis(
        coordinates, basis_dimension, number_expansion_terms, convex_hull_size, covariance, index
    ):
        """Calculate the fourier basis.

        Args:
            coordinates (np.array): Vector with coordinates of field
            basis_dimension (int): Dimension of the complete Fourier basis (not the latent space)
            number_expansion_terms (int): Number of frequencies
            convex_hull_size  (float): Maximum length on the mesh
            covariance (np.array): Transform of covariance matrix
            index (np.array): Array indexing valid basis terms in accordance to the truncation
                              threshold

        Returns:
            basis (np.array): Transformed and truncated fourier basis
        """
        basis = np.zeros(shape=(coordinates.shape[0], basis_dimension))
        k = (
            np.linspace(0, number_expansion_terms - 1, number_expansion_terms)
            * np.pi
            / convex_hull_size
        )
        arguements = np.outer(coordinates, k)
        cos_terms = np.multiply(np.cos(arguements), covariance)
        sin_terms = np.multiply(np.sin(arguements), covariance)

        basis[:, 0::2] = cos_terms
        basis[:, 1::2] = sin_terms
        return basis[:, index]


class DimensionMethods2D:
    """2D FOURIER expansion helper methods."""

    @staticmethod
    def get_dim(trunc_threshold, number_expansion_terms):
        """Calculate dimension of latent space.

        Args:
            trunc_threshold (int): Truncation threshold
            number_expansion_terms (int): Number of frequencies in the expansion

        Returns:
            covariance_index (np.array): Array indexing the covariance values below the truncation
                                         limit
            latent_index (np.array): Array indexing the basis terms corresponding to valid
                                     covariance values
            basis_dimension (int): Dimension of the complete Fourier basis up to the truncation
                                   threshold
            dimension (int): Dimension of the latent space
        """
        basis_dimension = int(4 * (number_expansion_terms) ** 2)
        wave_numbers = (
            np.linspace(0, number_expansion_terms - 1, number_expansion_terms, dtype=int) ** 2
        )
        dim_one_wave_numbers = np.kron(wave_numbers, np.ones(shape=(number_expansion_terms,)))
        dim_two_wave_numbers = np.kron(np.ones(shape=(number_expansion_terms,)), wave_numbers)
        index = dim_one_wave_numbers + dim_two_wave_numbers
        covariance_index = index <= trunc_threshold
        latent_index = np.kron(covariance_index, np.ones(shape=(4,))).astype(bool)

        dimension = np.sum(latent_index, dtype=int)

        return covariance_index, latent_index, basis_dimension, dimension

    @staticmethod
    def calculate_covariance(number_expansion_terms, corr_length, convex_hull_size):
        """Calculate discrete fourier transform of the covariance kernel.

        Based on the kernel description of the random field, build its
        covariance matrix using the external geometry and coordinates.

        Args:
            number_expansion_terms (int): Number of frequencies
            corr_length (float): Typical length in the field
            convex_hull_size  (float): Max distance on the grid

        Returns:
            covariance (np.array): Cosine transform of covariance matrix
        """
        c_k = np.linspace(0, number_expansion_terms - 1, number_expansion_terms)
        c_k = (
            corr_length
            * np.sqrt(np.pi)
            / convex_hull_size
            * np.exp(-((c_k * np.pi * corr_length) ** 2) / (2 * convex_hull_size) ** 2)
        )
        c_k[0] = corr_length * np.sqrt(np.pi) / (2 * convex_hull_size)
        cov_vector = np.kron(c_k, c_k)
        covariance = np.sqrt(cov_vector)
        return covariance

    @staticmethod
    def calculate_basis(
        coordinates, basis_dimension, number_expansion_terms, convex_hull_size, covariance, index
    ):
        """Calculate the fourier basis.

        Args:
            coordinates (np.array): Vector with coordinates of field
            basis_dimension (int): Dimension of the complete Fourier basis (not the latent space)
            number_expansion_terms (int): Number of frequencies
            convex_hull_size  (float): Maximum length on the mesh
            covariance (np.array): Transform of covariance matrix
            index (np.array): Array indexing valid basis terms in accordance to the truncation
                              threshold

        Returns:
            basis (np.array): Transformed and truncated fourier basis
        """
        basis = np.zeros(shape=(coordinates.shape[0], basis_dimension))
        k = (
            np.linspace(0, number_expansion_terms - 1, number_expansion_terms)
            * np.pi
            / convex_hull_size
        )
        arguements = [np.outer(coordinates[:, 0], k), np.outer(coordinates[:, 1], k)]

        cosine_x0 = np.cos(arguements[0])
        cosine_x1 = np.cos(arguements[1])
        sin_x0 = np.sin(arguements[0])
        sin_x1 = np.sin(arguements[1])

        terms = np.zeros(shape=(4, len(coordinates), len(covariance)))
        for i in range(len(coordinates)):
            terms[:, i, :] = np.array(
                [
                    np.kron(cosine_x0[i, :], cosine_x1[i, :]),
                    np.kron(sin_x0[i, :], sin_x1[i, :]),
                    np.kron(cosine_x0[i, :], sin_x1[i, :]),
                    np.kron(sin_x0[i, :], cosine_x1[i, :]),
                ]
            )

        terms = np.multiply(terms, covariance)

        basis[:, 0::4] = terms[0]
        basis[:, 1::4] = terms[1]
        basis[:, 2::4] = terms[2]
        basis[:, 3::4] = terms[3]

        return basis[:, index]


class DimensionMethods3D:
    """3D FOURIER expansion helper methods."""

    @staticmethod
    def get_dim(trunc_threshold, number_expansion_terms):
        """Calculate dimension of latent space.

        Args:
            trunc_threshold (int): Truncation threshold
            number_expansion_terms (int): Number of frequencies in the expansion

        Returns:
            covariance_index (np.array): Array indexing the covariance values below the truncation
                                         limit
            latent_index (np.array): Array indexing the basis terms corresponding to valid
                                     covariance values
            basis_dimension (int): Dimension of the complete Fourier basis up to the truncation
                                   threshold
            dimension (int): Dimension of the latent space
        """
        basis_dimension = int(8 * (number_expansion_terms) ** 3)
        wave_numbers = (
            np.linspace(0, number_expansion_terms - 1, number_expansion_terms, dtype=int) ** 2
        )
        dim_one_wave_numbers = np.kron(wave_numbers, np.ones(shape=(number_expansion_terms**2,)))
        dim_two_wave_numbers = np.kron(
            np.kron(np.ones(shape=(number_expansion_terms,)), wave_numbers),
            np.ones(shape=(number_expansion_terms,)),
        )
        dim_three_wave_numbers = np.kron(
            np.ones(shape=(number_expansion_terms**2,)), wave_numbers
        )
        index = dim_one_wave_numbers + dim_two_wave_numbers + dim_three_wave_numbers
        covarance_index = index <= trunc_threshold
        latent_index = np.kron(covarance_index, np.ones(shape=(8,))).astype(bool)

        dimension = np.sum(latent_index, dtype=int)
        return covarance_index, latent_index, basis_dimension, dimension

    @staticmethod
    def calculate_covariance(number_expansion_terms, corr_length, convex_hull_size):
        """Calculate discrete fourier transform of the covariance kernel.

        Based on the kernel description of the random field, build its
        covariance matrix using the external geometry and coordinates.

        Args:
            number_expansion_terms (int): Number of frequencies
            corr_length (float): Typical length in the field
            convex_hull_size  (float): Max distance on the grid

        Returns:
            covariance (np.array): Cosine transform of covariance matrix
        """
        c_k = np.linspace(0, number_expansion_terms - 1, number_expansion_terms)
        c_k = (
            corr_length
            * np.sqrt(np.pi)
            / convex_hull_size
            * np.exp(-((c_k * np.pi * corr_length) ** 2) / (2 * convex_hull_size) ** 2)
        )
        c_k[0] = corr_length * np.sqrt(np.pi) / (2 * convex_hull_size)
        cov_vector = np.kron(c_k, c_k)
        cov_vector3d = np.kron(c_k, cov_vector)
        covariance = np.sqrt(cov_vector3d)
        return covariance

    @staticmethod
    def calculate_basis(
        coordinates, basis_dimension, number_expansion_terms, convex_hull_size, covariance, index
    ):
        """Calculate the fourier basis.

        Args:
            coordinates (np.array): Vector with coordinates of field
            basis_dimension (int): Dimension of the complete Fourier basis (not the latent space)
            number_expansion_terms (int): Number of frequencies
            convex_hull_size  (float): Maximum length on the mesh
            covariance (np.array): Transform of covariance matrix
            index (np.array): Array indexing valid basis terms in accordance to the truncation
                              threshold

        Returns:
            basis (np.array): Transformed and truncated fourier basis
        """
        basis = np.zeros(shape=(coordinates.shape[0], basis_dimension))
        k = (
            np.linspace(0, number_expansion_terms - 1, number_expansion_terms)
            * np.pi
            / convex_hull_size
        )

        arguements = [
            np.outer(coordinates[:, 0], k),
            np.outer(coordinates[:, 1], k),
            np.outer(coordinates[:, 2], k),
        ]

        cosine_x0 = np.cos(arguements[0])
        cosine_x1 = np.cos(arguements[1])
        cosine_x2 = np.cos(arguements[2])
        sin_x0 = np.sin(arguements[0])
        sin_x1 = np.sin(arguements[1])
        sin_x2 = np.sin(arguements[2])

        terms = np.zeros(shape=(8, len(coordinates), len(covariance)))
        for i in range(len(coordinates)):
            terms[:, i, :] = np.array(
                [
                    np.kron(
                        np.kron(cosine_x0[i, :], cosine_x1[i, :]),
                        cosine_x2[i, :],
                    ),
                    np.kron(
                        np.kron(sin_x0[i, :], sin_x1[i, :]),
                        cosine_x2[i, :],
                    ),
                    np.kron(
                        np.kron(cosine_x0[i, :], sin_x1[i, :]),
                        cosine_x2[i, :],
                    ),
                    np.kron(
                        np.kron(sin_x0[i, :], cosine_x1[i, :]),
                        cosine_x2[i, :],
                    ),
                    np.kron(
                        np.kron(cosine_x0[i, :], cosine_x1[i, :]),
                        sin_x2[i, :],
                    ),
                    np.kron(
                        np.kron(sin_x0[i, :], sin_x1[i, :]),
                        sin_x2[i, :],
                    ),
                    np.kron(
                        np.kron(cosine_x0[i, :], sin_x1[i, :]),
                        sin_x2[i, :],
                    ),
                    np.kron(
                        np.kron(sin_x0[i, :], cosine_x1[i, :]),
                        sin_x2[i, :],
                    ),
                ]
            )

        terms = np.multiply(terms, covariance)

        basis[:, 0::8] = terms[0]
        basis[:, 1::8] = terms[1]
        basis[:, 2::8] = terms[2]
        basis[:, 3::8] = terms[3]
        basis[:, 4::8] = terms[4]
        basis[:, 5::8] = terms[5]
        basis[:, 6::8] = terms[6]
        basis[:, 7::8] = terms[7]

        return basis[:, index]
