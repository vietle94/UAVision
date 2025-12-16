import numpy as np
from numpy.typing import NDArray


def calculate_binedges(midbin: NDArray[np.float64]) -> NDArray[np.float64]:
    """
    calculate bin edges from mid bin
    midbin: mid bin array
    return: binedges array
    """
    binedges = np.append(
        np.append(
            midbin[0] - (-midbin[0] + midbin[1]) / 2, (midbin[:-1] + midbin[1:]) / 2
        ),
        (midbin[-1] - midbin[-2]) / 2 + midbin[-1],
    )
    return binedges


def calculate_midbin(binedges: NDArray[np.float64]) -> NDArray[np.float64]:
    """
    calculate midbin from bin edges
    binedges: binedges array
    return: midbin array
    """

    midbin = (binedges[1:] + binedges[:-1]) / 2
    return midbin
