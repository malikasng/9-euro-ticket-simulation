import numpy as np


class RBF:
    """ Radial Basis function
        phi(x) = exp(-(|x_l - x|/eps)**2)
    """

    def __init__(self, L, eps=1.0):
        """ Initialize radial basis function
            
        Args:
            L (int): No of basis functions
            eps (float, optional): epsilon value. Defaults to 1.0.
        """

        self.L = L
        self.eps = eps
        self.centers = None
        self.weights = None

    def radial_basis(self, center, data_point):
        """_summary_

        Args:
            center (array): Array of randomly initialised centers
            data_point (array): A single data point

        Returns:
            array: Returns phi(x) according to radial basis function
        """

        return np.exp(-(self.eps*np.linalg.norm(center-data_point))**2)

    def interpolate(self, x):
        """_summary_

        Args:
            x (_type_): _description_

        Returns:
            _type_: _description_
        """

        matrix = np.zeros((len(x), self.L))

        for data_point_arg, data_point in enumerate(x):
            for center_arg, center in enumerate(self.centers):
                matrix[data_point_arg, center_arg] = self.radial_basis(
                        center, data_point)
        return matrix

    def select_centers(self, y):
        """_summary_

        Args:
            y (_type_): _description_

        Returns:
            _type_: _description_
        """

        random_args = np.random.choice(len(y), self.L)
        centers = y[random_args]
        return centers

    def fit(self, x, y):
        """_summary_

        Args:
            x (_type_): _description_
            y (_type_): _description_
        """

        self.centers = self.select_centers(x)
        matrix = self.interpolate(x)
        self.weights, residuals, rank, sing_vals = np.linalg.lstsq(matrix,  y, rcond=1e-10)

    def predict(self, x):
        """_summary_

        Args:
            x (_type_): _description_

        Returns:
            _type_: _description_
        """
        
        matrix = self.interpolate(x)
        predictions = np.dot(matrix, self.weights)
        return predictions