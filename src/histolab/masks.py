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
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import List

import numpy as np

import histolab

from .filters.compositions import FiltersComposition
from .types import Region
from .util import (
    lazyproperty,
    polygon_to_mask_array,
    region_coordinates,
    regions_from_binary_mask,
)


class BinaryMask(ABC):
    """Generic object for binary masks.

    This object can be used to create a custom binary mask object.

    Example:
        >>> from histolab.slide import Slide
        >>> class MyCustomMask(BinaryMask):
        ...     def _mask(self, slide):
        ...         my_mask = np.array([0,1])
        ...         return my_mask
        >>> binary_mask = MyCustomMask()
        >>> slide = Slide("path/to/slide") # doctest: +SKIP
        >>> binary_mask(slide) # doctest: +SKIP
    """

    def __call__(self, slide):
        return self._mask(slide)

    @lazyproperty
    @abstractmethod
    def _mask(self, slide):  # pragma: no cover
        # This property will be supplied by the inheriting classes individually
        pass  # pragma: no cover


class BiggestTissueBoxMask(BinaryMask):
    """Object that represents the box containing the largest contiguous tissue area."""

    @lru_cache(maxsize=100)
    def _mask(self, slide) -> np.ndarray:
        """Return the thumbnail box mask containing the largest contiguous tissue area.

        Parameters
        ----------
        slide : Slide
            The Slide from which to compute the extraction mask

        Returns
        -------
        mask: np.ndarray
            Binary mask of the box containing the largest contiguous tissue area.
            The dimensions are those of the thumbnail.
        """
        thumb = slide.thumbnail
        filters = FiltersComposition(histolab.slide.Slide).tissue_mask_filters
        thumb_mask = filters(thumb)
        regions = regions_from_binary_mask(thumb_mask)
        biggest_region = self._regions(regions, n=1)[0]
        biggest_region_coordinates = region_coordinates(biggest_region)
        thumb_bbox_mask = polygon_to_mask_array(thumb.size, biggest_region_coordinates)
        return thumb_bbox_mask

    @staticmethod
    def _regions(regions: List[Region], n: int = 1) -> List[Region]:
        """Return the biggest ``n`` regions.

        Parameters
        ----------
        regions : List[Region]
            List of regions
        n : int, optional
            Number of regions to return, by default 1

        Returns
        -------
        List[Region]
            List of ``n`` biggest regions

        Raises
        ------
        ValueError
            If ``n`` is not between 1 and the number of elements of ``regions``
        """
        if n < 1:
            raise ValueError(f"Number of regions must be greater than 0, got {n}.")
        if n > len(regions):
            raise ValueError(
                f"n should be smaller than the number of regions [{len(regions)}], "
                f"got {n}"
            )

        sorted_regions = sorted(regions, key=lambda r: r.area, reverse=True)
        return sorted_regions[:n]


class TissueMask(BinaryMask):
    """Object that represent the tissue area mask."""

    @lru_cache(maxsize=100)
    def _mask(self, slide) -> np.ndarray:
        """Return the thumbnail binary mask of the tissue area.

        Parameters
        ----------
        slide : Slide
            The Slide from which to compute the extraction mask

        Returns
        -------
        mask: np.ndarray
            Binary mask of the tissue area. The dimensions are those of the thumbnail.
        """
        thumb = slide.thumbnail
        filters = FiltersComposition(histolab.slide.Slide).tissue_mask_filters
        thumb_mask = filters(thumb)
        return thumb_mask
