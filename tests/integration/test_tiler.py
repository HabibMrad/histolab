# encoding: utf-8

import os

import numpy as np
import pytest

from histolab.scorer import NucleiScorer
from histolab.slide import Slide
from histolab.tiler import GridTiler, RandomTiler, ScoreTiler

from ..fixtures import SVS
from ..util import load_expectation


class DescribeRandomTiler:
    @pytest.mark.parametrize(
        "fixture_slide, expectation_path",
        [
            (
                SVS.CMU_1_SMALL_REGION,
                "tiles-location-images/cmu-1-small-region-tiles-location-random",
            ),
            (
                SVS.TCGA_CR_7395_01A_01_TS1,
                "tiles-location-images/tcga-cr-7395-01a-01-ts1-tiles-location-random",
            ),
        ],
    )
    def it_locates_tiles_on_the_slide(self, fixture_slide, expectation_path, tmpdir):
        slide = Slide(fixture_slide, os.path.join(tmpdir, "processed"))
        slide.save_scaled_image(10)
        random_tiles_extractor = RandomTiler(
            tile_size=(512, 512), n_tiles=2, level=0, seed=42, check_tissue=False
        )
        expectation = load_expectation(
            expectation_path,
            type_="png",
        )
        tiles_location_img = random_tiles_extractor.locate_tiles(slide, scale_factor=10)

        np.testing.assert_array_almost_equal(
            np.asarray(tiles_location_img), expectation
        )


class DescribeGridTiler:
    @pytest.mark.parametrize(
        "fixture_slide, expectation_path",
        [
            (
                SVS.CMU_1_SMALL_REGION,
                "tiles-location-images/cmu-1-small-region-tiles-location-grid",
            ),
            (
                SVS.TCGA_CR_7395_01A_01_TS1,
                "tiles-location-images/tcga-cr-7395-01a-01-ts1-tiles-location-grid",
            ),
        ],
    )
    def it_locates_tiles_on_the_slide(self, fixture_slide, expectation_path, tmpdir):
        slide = Slide(fixture_slide, os.path.join(tmpdir, "processed"))
        grid_tiles_extractor = GridTiler(
            tile_size=(512, 512),
            level=0,
            check_tissue=False,
        )
        expectation = load_expectation(expectation_path, type_="png")
        tiles_location_img = grid_tiles_extractor.locate_tiles(slide, scale_factor=10)

        np.testing.assert_array_almost_equal(
            np.asarray(tiles_location_img), expectation
        )


class DescribeScoreTiler:
    @pytest.mark.parametrize(
        "fixture_slide, expectation_path",
        [
            (
                SVS.CMU_1_SMALL_REGION,
                "tiles-location-images/cmu-1-small-region-tiles-location-scored",
            ),
            (
                SVS.TCGA_CR_7395_01A_01_TS1,
                "tiles-location-images/tcga-cr-7395-01a-01-ts1-tiles-location-scored",
            ),
        ],
    )
    def it_locates_tiles_on_the_slide(self, fixture_slide, expectation_path, tmpdir):
        slide = Slide(fixture_slide, os.path.join(tmpdir, "processed"))
        scored_tiles_extractor = ScoreTiler(
            scorer=NucleiScorer(),
            tile_size=(512, 512),
            n_tiles=2,
            level=0,
            check_tissue=True,
        )
        expectation = load_expectation(
            expectation_path,
            type_="png",
        )
        scored_location_img = scored_tiles_extractor.locate_tiles(
            slide, scale_factor=10
        )

        np.testing.assert_array_almost_equal(
            np.asarray(scored_location_img), expectation
        )
