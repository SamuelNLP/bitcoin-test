import warnings

import graphviz
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.metrics import f1_score
from sklearn.tree import export_graphviz
from sklearn.metrics import classification_report
from sklearn.metrics import roc_curve, auc

warnings.filterwarnings('ignore')

import pandas as pd
from sqlalchemy import create_engine


# functions imported in notebook
def import_data_from_database(table: str):
    # connection to database
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/bitcoin_test')

    con = engine.connect()

    # get data_fusion
    rs = con.execute('SELECT * FROM {}'.format(table))
    df = pd.DataFrame(rs.fetchall())
    df.columns = rs.keys()

    # df.drop(columns=['month', 'day_of_month', 'b_loss_usd'], inplace=True)
    #
    # # categorize week days
    # df['weekday'] = pd.Categorical(df['date_'].dt.weekday_name, categories=['Monday', 'Tuesday', 'Wednesday',
    #                                                                         'Thursday', 'Friday', 'Saturday',
    #                                                                         'Sunday'], ordered=True)

    # sort by date_ and assign date_ as index
    df.set_index('date_', inplace=True)
    df.sort_index(inplace=True)

    return df


# give bool cols in df
def non_bool_cols(df):
    return [col for col in df if
            not df[col].dropna().value_counts().index.isin([0, 1]).all()]


def plot_decision_tree(clf, feature_names, class_names=None):
    # This function requires the pydotplus module and assumes it's been installed.
    # In some cases (typically under Windows) even after running conda install, there is a problem where the
    # pydotplus module is not found when running from within the notebook environment.  The following code
    # may help to guarantee the module is installed in the current notebook environment directory.
    #
    # import sys; sys.executable
    # !{sys.executable} -m pip install pydotplus
    warnings.filterwarnings('ignore')

    export_graphviz(clf, out_file="adspy_temp.dot", feature_names=feature_names, class_names=class_names, filled=True,
                    impurity=False)
    with open("adspy_temp.dot") as f:
        dot_graph = f.read()
    # Alternate method using pydotplus, if installed.
    # graph = pydotplus.graphviz.graph_from_dot_data(dot_graph)
    # return graph.create_png()
    return graphviz.Source(dot_graph)


def plot_class_regions(clf, X, y, X_test, y_test, title, subplot, target_names=None, plot_decision_regions=True, report=True):
    warnings.filterwarnings('ignore')

    numClasses = np.amax(y) + 1
    color_list_light = ['#FFFFAA', '#EFEFEF', '#AAFFAA', '#AAAAFF']
    color_list_bold = ['#EEEE00', '#000000', '#00CC00', '#0000CC']
    cmap_light = ListedColormap(color_list_light[0:numClasses])
    cmap_bold = ListedColormap(color_list_bold[0:numClasses])

    h = 0.03
    k = 0.5
    x_plot_adjust = 0.1
    y_plot_adjust = 0.1
    plot_symbol_size = 50

    x_min = np.min([X[:, 0].min(), X_test[:, 0].min()])
    x_max = np.max([X[:, 0].max(), X_test[:, 0].max()])
    y_min = np.min([X[:, 1].min(), X_test[:, 1].min()])
    y_max = np.max([X[:, 1].max(), X_test[:, 1].max()])
    x2, y2 = np.meshgrid(np.arange(x_min - k, x_max + k, h), np.arange(y_min - k, y_max + k, h))

    P = clf.predict(np.c_[x2.ravel(), y2.ravel()])
    P = P.reshape(x2.shape)

    if plot_decision_regions:
        subplot.contourf(x2, y2, P, cmap=cmap_light, alpha=0.8)

    subplot.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap_bold, s=plot_symbol_size, edgecolor='black')
    subplot.set_xlim(x_min - x_plot_adjust, x_max + x_plot_adjust)
    subplot.set_ylim(y_min - y_plot_adjust, y_max + y_plot_adjust)

    if (X_test is not None):
        subplot.scatter(X_test[:, 0], X_test[:, 1], c=y_test, cmap=cmap_bold, s=plot_symbol_size, marker='^',
                        edgecolor='black')
        train_score = f1_score(y, clf.predict(X), average='macro')
        test_score = f1_score(y_test, clf.predict(X_test), average='macro')
        title = title + "\nTrain f1 score = {:.2f}, Test f1 score = {:.2f}".format(train_score, test_score)

    subplot.set_title(title)

    if (target_names is not None):
        legend_handles = []
        for i in range(0, len(target_names)):
            patch = mpatches.Patch(color=color_list_bold[i], label=target_names[i])
            legend_handles.append(patch)
        subplot.legend(loc=0, handles=legend_handles)

    if report:
        print(classification_report(y_test, clf.predict(X_test)))


def util_classifier_simple(clf_template, clf_name, X_train, y_train, X_test, y_test, C, report=False):
    warnings.filterwarnings('ignore')

    _, subaxes = plt.subplots(1, 1, figsize=(10, 10))

    clf = clf_template(C=C).fit(X_train, y_train)
    title = '{}, C = {:.2f}'.format(clf_name, C)

    plot_class_regions(clf, X_train, y_train,
                       X_test, y_test, title,
                       subaxes, report=report)

    y_score_lr = clf.decision_function(X_test)
    fpr_lr, tpr_lr, thresholds = roc_curve(y_test, y_score_lr)
    roc_auc_lr = auc(fpr_lr, tpr_lr)

    plt.figure(figsize=[10, 10])
    plt.xlim([-0.01, 1.00])
    plt.ylim([-0.01, 1.01])
    closest_zero = np.argmin(np.abs(thresholds))
    closest_zero_p = fpr_lr[closest_zero]
    closest_zero_r = tpr_lr[closest_zero]
    plt.plot(closest_zero_p, closest_zero_r, 'o', markersize=12, fillstyle='none', c='r', mew=3)
    plt.plot(fpr_lr, tpr_lr, lw=3, label='ROC curve (area = {:0.2f})'.format(roc_auc_lr))
    plt.xlabel('False Positive Rate', fontsize=16)
    plt.ylabel('True Positive Rate', fontsize=16)
    plt.title('ROC', fontsize=16)
    plt.legend(loc='lower right', fontsize=13)
    plt.plot([0, 1], [0, 1], color='navy', lw=3, linestyle='--')
    plt.axes().set_aspect('equal')
    plt.show()

def util_classifier(clf_template, clf_name, X_train, y_train, X_test, y_test, C, gamma=None, report=False):
    warnings.filterwarnings('ignore')

    if gamma is None:
        fig, subaxes = plt.subplots(len(C), 1, figsize=(10, 20))

        for this_C, subplot in zip(C, subaxes):
            clf = clf_template(C=this_C).fit(X_train, y_train)
            title = '{}, C = {:.2f}'.format(clf_name, this_C)

            plot_class_regions(clf, X_train, y_train,
                               X_test, y_test, title,
                               subplot, report=report)

    else:
        fig, subaxes = plt.subplots(len(gamma), len(C), figsize=(20, 15))

        for this_gamma, this_axis in zip(gamma, subaxes):

            for this_C, subplot in zip(C, this_axis):
                title = 'gamma = {:.2f}, C = {:.2f}'.format(this_gamma, this_C)
                clf = clf_template(kernel='rbf', gamma=this_gamma,
                          C=this_C).fit(X_train, y_train)
                plot_class_regions(clf, X_train, y_train,
                                   X_test, y_test, title,
                                   subplot, report=report)
                plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)


def plot_validation_curve(train_scores, test_scores, param_name, param_range, clf_name):
    # This code based on scikit-learn validation_plot example
    #  See:  http://scikit-learn.org/stable/auto_examples/model_selection/plot_validation_curve.html
    plt.figure(figsize=(10, 7))

    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.title('Validation Curve with {}'.format(clf_name))
    plt.xlabel(param_name)
    plt.ylabel('Score')
    plt.ylim(0.0, 1.1)
    lw = 2

    plt.semilogx(param_range, train_scores_mean, label='Training score',
                color='darkorange', lw=lw)

    plt.fill_between(param_range, train_scores_mean - train_scores_std,
                    train_scores_mean + train_scores_std, alpha=0.2,
                    color='darkorange', lw=lw)

    plt.semilogx(param_range, test_scores_mean, label='Cross-validation score',
                color='navy', lw=lw)

    plt.fill_between(param_range, test_scores_mean - test_scores_std,
                    test_scores_mean + test_scores_std, alpha=0.2,
                    color='navy', lw=lw)

    plt.legend(loc='best')
    plt.show()


