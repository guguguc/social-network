import matplotlib.pyplot as plt
import numpy as np


def linear_bezier(p1, p2) -> np.ndarray:
    p1 = np.array(p1).reshape(1, 2)
    p2 = np.array(p2).reshape(1, 2)
    t1 = np.linspace(0, 1, 100).reshape(100, 1)
    t2 = 1 - t1
    return t2 * p1 + t1 * p2


def quadratic_bezier(p1, p2, p3):
    t = np.linspace(0, 1, 100).reshape(100, 1)
    _p1 = linear_bezier(p1, p2)
    _p2 = linear_bezier(p2, p3)
    return (1 - t) * _p1 + t * _p2


def plot_circle(p, color='red'):
    plt.plot(p[0], p[1], 'o', color=color)


def plot_line(p1, p2, color='green'):
    plt.plot([p1[0], p2[0]], [p1[1], p2[1]], '--', color=color)


if __name__ == '__main__':
    p1 = (1, 3)
    p2 = (2, 6)
    p3 = (3, 5)
    plot_circle(p1)
    plot_circle(p2)
    plot_circle(p3)
    plot_line(p1, p2)
    plot_line(p2, p3)
    p = quadratic_bezier(p1, p2, p3)
    x, y = p[:, 0], p[:, 1]
    plt.plot(x, y)
    plt.show()
