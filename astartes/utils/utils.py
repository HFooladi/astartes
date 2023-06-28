import sklearn
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from tabulate import tabulate

from astartes import train_val_test_split
from astartes.utils.exceptions import InvalidModelTypeError


def generate_regression_results_dict(
    sklearn_model,
    X,
    y,
    samplers=["random"],
    random_state=0,
    samplers_hopts={},
    train_size=0.8,
    val_size=0.1,
    test_size=0.1,
    print_results=False,
):
    """
    Helper function to train a sklearn model using the provided data
    and provided sampler types.

    Args:
        X (np.array, pd.DataFrame): Numpy array or pandas DataFrame of feature vectors.
        y (np.array, pd.Series): Targets corresponding to X, must be of same size.
        train_size (float, optional): Fraction of dataset to use in training set. Defaults to 0.8.
        val_size (float, optional): Fraction of dataset to use in validation set. Defaults to 0.1.
        test_size (float, optional): Fraction of dataset to use in test set. Defaults to 0.1.
        random_state (int, optional): The random seed used throughout astartes.
        samplers_hopts (dict, optional): Should be a dictionary of dictionaries with the keys specifying
                                         the sampler and the values being another dictionary with the
                                         corresponding hyperparameters. Defaults to {}.
        print_results (bool, optional): whether to print the resulting dictionary as a neat table

    Returns:
        dict: nested dictionary with the format of
            {
                sampler: {
                    'mae':{
                        'train': [],
                        'val': [],
                        'test': [],
                    },
                    'rmse':{
                        'train': [],
                        'val': [],
                        'test': [],
                    },
                    'R2':{
                        'train': [],
                        'val': [],
                        'test': [],
                    },
                },
            }
    """
    if not isinstance(sklearn_model, sklearn.base.BaseEstimator):
        raise InvalidModelTypeError("Model must be an sklearn model")

    final_dict = {}
    for sampler in samplers:
        error_dict = {
            "mae": {
                "train": [],
                "val": [],
                "test": [],
            },
            "rmse": {
                "train": [],
                "val": [],
                "test": [],
            },
            "R2": {
                "train": [],
                "val": [],
                "test": [],
            },
        }

        # obtain indices
        _, _, _, train_indices, val_indices, test_indices = train_val_test_split(
            X,
            train_size=train_size,
            val_size=val_size,
            test_size=test_size,
            sampler=sampler,
            random_state=random_state,
            hopts=samplers_hopts.get(sampler, dict()),
            return_indices=True,
        )

        # create data splits
        X_train = X[train_indices]
        X_val = X[val_indices]
        X_test = X[test_indices]

        y_train = y[train_indices]
        y_val = y[val_indices]
        y_test = y[test_indices]

        # fit the model to the training data
        sklearn_model.fit(X_train, y_train)

        # get predictions
        y_pred_train = sklearn_model.predict(X_train)
        y_pred_val = sklearn_model.predict(X_val)
        y_pred_test = sklearn_model.predict(X_test)

        # store MAEs
        train_mae = mean_absolute_error(y_train, y_pred_train)
        error_dict["mae"]["train"].append(train_mae)

        val_mae = mean_absolute_error(y_val, y_pred_val)
        error_dict["mae"]["val"].append(val_mae)

        test_mae = mean_absolute_error(y_test, y_pred_test)
        error_dict["mae"]["test"].append(test_mae)

        # store RMSEs
        train_rmse = mean_squared_error(y_train, y_pred_train, squared=False)
        error_dict["rmse"]["train"].append(train_rmse)

        val_rmse = mean_squared_error(y_val, y_pred_val, squared=False)
        error_dict["rmse"]["val"].append(val_rmse)

        test_rmse = mean_squared_error(y_test, y_pred_test, squared=False)
        error_dict["rmse"]["test"].append(test_rmse)

        # store R2
        train_R2 = r2_score(y_train, y_pred_train)
        error_dict["R2"]["train"].append(train_R2)

        val_R2 = r2_score(y_val, y_pred_val)
        error_dict["R2"]["val"].append(val_R2)

        test_R2 = r2_score(y_test, y_pred_test)
        error_dict["R2"]["test"].append(test_R2)

        final_dict[sampler] = error_dict

        if print_results:
            print(f"\nDisplaying results for {sampler} sampler")
            display_results_as_table(error_dict)

    return final_dict


def display_results_as_table(error_dict):
    """Helper function to print a dictionary as a neat tabulate"""
    headers = ["Train", "Val", "Test"]
    table = []
    for key, val in error_dict.items():
        table_tmp = [key.upper()]
        table_tmp.extend([val[0] for val in val.values()])
        table.append(table_tmp)
    print(tabulate(table, headers=headers))
