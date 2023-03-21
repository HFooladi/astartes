import warnings
from typing import List

import numpy as np

from astartes.utils.exceptions import MoleculesNotInstalledError

try:
    """
    aimsim depends on sklearn_extra, which uses a version checking technique that is due to
    be deprecated in a version of Python after 3.11, so it is throwing a deprecation warning
    We ignore this warning since we can't do anything about it (sklearn_extra seems to be
    abandonware) and in the future it will become an error that we can deal with.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)
        from aimsim.chemical_datastructures import Molecule
except ImportError:  # pragma: no cover
    raise MoleculesNotInstalledError(
        """To use molecule featurizer, install astartes with pip install astartes[molecules]."""
    )


from astartes import train_test_split, train_val_test_split

from astartes.main import DEFAULT_RANDOM_STATE


def train_val_test_split_molecules(
    smiles: List[str],
    y: np.array = None,
    labels: np.array = None,
    train_size: float = 0.8,
    val_size: float = 0.1,
    test_size: float = 0.1,
    sampler: str = "random",
    random_state: int = DEFAULT_RANDOM_STATE,
    hopts: dict = {},
    fingerprint: str = "morgan_fingerprint",
    fprints_hopts: dict = {},
    return_indices: bool = False,
):
    """Deterministic train_test_splitting of SMILES strings.

    Args:
        smiles (List[str]): List of SMILES strings representing molecules or reactions.
        y (np.array, optional): Targets corresponding to SMILES, must be of same size. Defaults to None.
        labels (np.array, optional): Labels corresponding to SMILES, must be of same size. Defaults to None.
        train_size (float, optional): Fraction of dataset to use in training set. Defaults to 0.8.
        val_size (float, optional): Fraction of dataset to use in validation set. Defaults to 0.1.
        test_size (float, optional): Fraction of dataset to use in test set. Defaults to 0.1.
        sampler (str, optional): Sampler to use, see IMPLEMENTED_INTER/EXTRAPOLATION_SAMPLERS. Defaults to "random".
        random_state (int, optional): The random seed used throughout astartes.
        hopts (dict, optional): Hyperparameters for the sampler used above. Defaults to {}.
        fingerprint (str, optional): Molecular fingerprint to be used from AIMSim. Defaults to "morgan_fingerprint".
        fprints_hopts (dict, optional): Hyperparameters for AIMSim featurization. Defaults to {}.
        return_indices (bool, optional): True to return indices of train/test instead of values. Defaults to False.

    Returns:
        np.array: X, y, and labels train/val/test data, or indices.
    """
    X = _featurize(smiles, fingerprint, fprints_hopts)
    return train_val_test_split(
        X,
        y=y,
        labels=labels,
        test_size=test_size,
        val_size=val_size,
        train_size=train_size,
        sampler=sampler,
        random_state=random_state,
        hopts=hopts,
        return_indices=return_indices,
    )


def train_test_split_molecules(
    smiles: List[str],
    y: np.array = None,
    labels: np.array = None,
    train_size: float = 0.75,
    test_size: float = None,
    sampler: str = "random",
    random_state: int = DEFAULT_RANDOM_STATE,
    hopts: dict = {},
    fingerprint: str = "morgan_fingerprint",
    fprints_hopts: dict = {},
    return_indices: bool = False,
):
    """Deterministic train/test splitting of SMILES strings.

    Args:
        smiles (List[str]): List of SMILES strings representing molecules or reactions.
        y (np.array, optional): Targets corresponding to SMILES, must be of same size. Defaults to None.
        labels (np.array, optional): Labels corresponding to SMILES, must be of same size. Defaults to None.
        train_size (float, optional): Fraction of dataset to use in training (test+train~1). Defaults to 0.75.
        test_size (float, optional): Fraction of dataset to use in test set. Defaults to None.
        sampler (str, optional): Sampler to use, see IMPLEMENTED_INTER/EXTRAPOLATION_SAMPLERS. Defaults to "random".
        random_state (int, optional): The random seed used throughout astartes.
        hopts (dict, optional): Hyperparameters for the sampler used above. Defaults to {}.
        fingerprint (str, optional): Molecular fingerprint to be used from AIMSim. Defaults to "morgan_fingerprint".
        fprints_hopts (dict, optional): Hyperparameters for AIMSim featurization. Defaults to {}.
        return_indices (bool, optional): True to return indices of train/test instead of values. Defaults to False.

    Returns:
        np.array: X, y, and labels train/test data, or indices.
    """
    # turn the smiles into an input X
    X = _featurize(smiles, fingerprint, fprints_hopts)

    # call train test split with this input
    return train_test_split(
        X,
        y=y,
        labels=labels,
        test_size=test_size,
        train_size=train_size,
        sampler=sampler,
        random_state=random_state,
        hopts=hopts,
        return_indices=return_indices,
    )


def _featurize(smiles, fingerprint, fprints_hopts):
    """Call AIMSim's Molecule to featurize the SMILES string according to the arguments.

    Args:
        smiles (str): SMILES string.
        fingerprint (str): The molecular fingerprint to be used.
        fprints_hopts (dict): Hyperparameters for AIMSim.

    Returns:
        np.array: X array (featurized SMILES)
    """
    X = []
    for smile in smiles:
        mol = Molecule(mol_smiles=smile)
        mol.descriptor.make_fingerprint(
            mol.mol_graph,
            fingerprint,
            fingerprint_params=fprints_hopts,
        )
        X.append(mol.descriptor.to_numpy())
    return np.array(X)
