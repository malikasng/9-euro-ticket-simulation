import numpy as np
from scipy.spatial.distance import cdist


def rbf(distances, epsilon):
    '''
    Function which computes the Radial Basis Function
    :param x: input data
    :type x: numpy.ndarray
    :param x_l: center of the basis function, chosen as a random point
    :type x_l: numpy.ndarray
    :param epsilon: bandwidth
    :type epsilon: float
    :return: radial basis function values
    :rtype: numpy.ndarray
    '''
    return np.exp(- distances **2 / epsilon ** 2)


def find_nonlinear_approx(x, f_x, L, eps, single=False, start=None):
    '''
    Function which computes the nonlinear approximation
    :param x: input data
    :type x: numpy.ndarray
    :param f_x: target labels
    :type f_x: numpy.ndarray
    :param L: number of values taken from the input dataset
    :type L: int
    :param eps: parameter to compute epsilon
    :type eps: float
    :return: range of input, nonlinear function, epsilon value
    :rtype: numpy.ndarray, numpy.ndarray, float
    '''
    # Get indices of random first L elements
    random_indices = np.random.permutation(x.shape[0])[0:L]

    # Get the values at those indices
    random_x_vals = np.array([x[i] for i in random_indices])
    
    if single:
        # Make a start point and f_x two-dimensional from one-dimensional
        start = start.reshape(1, -1)
        f_x = f_x.reshape(1, -1)
        distances = cdist(start, random_x_vals)
    else:
        distances = cdist(x, random_x_vals)

    
    # Choose epsilon similar to Diffusion Maps
    epsilon = eps * np.max(distances)

    # Compute the radial basis functions
    # phi_funcs = rbf(x,random_x_vals,epsilon)
    phi_funcs = rbf(distances, epsilon)

    # Compute least squares
    A, residuals, rank, sing_vals = np.linalg.lstsq(phi_funcs, f_x, rcond=1e-10)

    # Get the range of values from dataset x
    x_range = np.array([np.linspace(np.min(x),np.max(x),x.shape[0])]).T
    distances_range = cdist(x_range, random_x_vals)
    phi_funcs_range = rbf(distances_range, epsilon)

    # Compute the nonlinear function values
    nonlinear_func = phi_funcs.dot(A)
    plot_func = phi_funcs_range.dot(A)
    if single:
        nonlinear_func = phi_funcs.dot(A)
        nonlinear_func = nonlinear_func[0]
        return nonlinear_func

    return x_range, nonlinear_func, plot_func, epsilon
