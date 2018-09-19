import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sns.set()


# define ecdf
def ecdf(data):
    """Compute ECDF for a one-dimensional array of measurements."""
    # Number of data points: n
    n = len(data)

    # x-data for the ECDF: x
    x = np.sort(data)

    # y-data for the ECDF: y
    y = np.arange(1, n + 1) / n

    return x, y


def hist_ecdf(data, name: str, ecdf_theor=True, percentiles=(2.5, 25, 50, 75, 97.5), plot_percentiles=True,
              xlog_scale=False, savefig=True, pathsave='./images/'):
    # compute ECDF and histogram
    data = data.dropna()

    # percentiles
    percentiles = np.array(percentiles)
    ptiles_data = np.percentile(data, percentiles)

    # histogram
    n_bins = int(np.sqrt(len(data)))

    plt.figure()
    plt.hist(data, bins=n_bins, density=True)
    plt.xlabel(name)
    plt.title('Histogram of {}'.format(name))

    if savefig:
        plt.savefig(pathsave + '/' + name + '_hist.png')

    x_real, y_real = ecdf(data)

    plt.figure()
    plt.plot(x_real, y_real, marker='.', linestyle='none')

    if ecdf_theor:
        # calculate theoretical normal values
        samples = np.random.normal(np.mean(data), np.std(data), size=10000)

        x_theor, y_theor = ecdf(samples)
        plt.plot(x_theor, y_theor)

    plt.xlabel(name)
    plt.ylabel('ECDF')
    plt.title('ECDF of {}'.format(name))

    if xlog_scale:
        plt.xscale('log')

    if plot_percentiles:
        plt.plot(ptiles_data, percentiles / 100, marker='D', color='red',
                 linestyle='none')
        for id_ in range(len(percentiles)):
            plt.gca().text(ptiles_data[id_], percentiles[id_] / 100 - 0.1, str(np.round(ptiles_data[id_], 2)),
                           ha='left')

    if savefig:
        plt.savefig(pathsave + '/' + name + '_ecdf.png')
