# encoding: utf-8

# ------------------------------------------------------------------------
# Copyright 2020 All Histolab Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------

import operator
from abc import abstractmethod

import numpy as np

from .filters import image_filters as imf
from .filters import morphological_filters as mof
from .filters.util import mask_difference
from .tile import Tile

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class Scorer(Protocol):
    """General scorer object

    .. automethod:: __call__
    """

    @abstractmethod
    def __call__(self, tile: Tile) -> float:
        raise NotImplementedError


class RandomScorer(Scorer):
    """Implement a Scorer that returns a random float score between 0 and 1.

    .. automethod:: __call__
    """

    def __call__(self, tile: Tile) -> float:
        """Return the random score associated with the tile.

        Parameters
        ----------
        tile : Tile
            The tile to calculate the score from.

        Returns
        -------
        float
            Random score ranging between 0 and 1.
        """
        return np.random.random()


class NucleiScorer(Scorer):
    r"""This class implements an hybrid algorithm that combines thresholding and
    morphological operations to segment nuclei on H&E-stained histological images.

    The NucleiScorer class defines the score of a given tile t as:

    .. math::

        s_t = N_t\cdot \mathrm{tanh}(T_t) \mathrm{, } \; 0\le s_t<1

    where :math:`N_t` is the nuclei ratio on t, computed as number of white pixels on
    the segmented mask over the tile size, and :math:`T_t` the fraction of tissue in t.

    Notice that we introduced the hyperbolic tangent to bound the weight of the tissue
    ratio over the nuclei ratio.
    """

    def __call__(self, tile: Tile) -> float:
        """Return the nuclei score associated with the tile.

        Parameters
        ----------
        tile : Tile
            The tile to calculate the score from.

        Returns
        -------
        float
            Nuclei score
        """

        filters_raw_nuclei = imf.Compose(
            [imf.HematoxylinChannel(), imf.YenThreshold(operator.gt)]
        )
        filters_nuclei_cleaner = imf.Compose(
            [imf.HematoxylinChannel(), imf.YenThreshold(operator.gt), mof.WhiteTopHat()]
        )

        mask_raw_nuclei = np.array(tile.apply_filters(filters_raw_nuclei).image)
        mask_nuclei_clean = np.array(tile.apply_filters(filters_nuclei_cleaner).image)

        mask_nuclei = mask_difference(mask_raw_nuclei, mask_nuclei_clean)
        nuclei_ratio = np.count_nonzero(mask_nuclei) / mask_nuclei.size

        return nuclei_ratio * np.tanh(tile.tissue_ratio)
