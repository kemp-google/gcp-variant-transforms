# Copyright 2017 Google Inc.  All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for vcf_to_bq script."""

import collections
import unittest

from gcp_variant_transforms import vcf_to_bq
from gcp_variant_transforms.options.variant_transform_options import MergeOptions
from gcp_variant_transforms.vcf_to_bq import _get_variant_merge_strategy
from gcp_variant_transforms.libs.variant_merge import move_to_calls_strategy


class VcfToBqTest(unittest.TestCase):
  """Tests cases for the ``vcf_to_bq`` script."""

  def _create_mock_args(self, **args):
    return collections.namedtuple('MockArgs', args.keys())(*args.values())

  def test_no_merge_strategy(self):
    args = self._create_mock_args(
        variant_merge_strategy=MergeOptions.NONE,
        info_keys_to_move_to_calls_regex=None,
        copy_quality_to_calls=None,
        copy_filter_to_calls=None)
    self.assertEqual(_get_variant_merge_strategy(args), None)

  def test_invalid_merge_strategy_raises_error(self):
    args = self._create_mock_args(
        variant_merge_strategy='NotAMergeStrategy',
        info_keys_to_move_to_calls_regex=None,
        copy_quality_to_calls=None,
        copy_filter_to_calls=None)
    with self.assertRaises(ValueError):
      _ = _get_variant_merge_strategy(args)

  def test_valid_merge_strategy(self):
    args = self._create_mock_args(
        variant_merge_strategy=MergeOptions.MOVE_TO_CALLS,
        info_keys_to_move_to_calls_regex=None,
        copy_quality_to_calls=None,
        copy_filter_to_calls=None)
    self.assertIsInstance(_get_variant_merge_strategy(args),
                          move_to_calls_strategy.MoveToCallsStrategy)

  def test_invalid_annotation_output_directory_raises_error(self):
    known_args = self._create_mock_args(annotation_output_dir='*')
    pipeline_args = []
    with self.assertRaisesRegexp(ValueError, 'directory .* already exists'):
      vcf_to_bq._validate_annotation_pipeline_args(known_args, pipeline_args)

  def test_invalid_annotation_missing_flags_raises_error(self):
    known_args = self._create_mock_args(annotation_output_dir='dummy')
    pipeline_args = []
    with self.assertRaisesRegexp(ValueError, 'Could not .* pipeline flags'):
      vcf_to_bq._validate_annotation_pipeline_args(known_args, pipeline_args)

  def test_valid_annotation_flags(self):
    known_args = self._create_mock_args(annotation_output_dir='dummy')
    pipeline_args_1 = ['--num_workers', '2']
    vcf_to_bq._validate_annotation_pipeline_args(known_args, pipeline_args_1)

    pipeline_args_2 = ['--max_num_workers', '2']
    vcf_to_bq._validate_annotation_pipeline_args(known_args, pipeline_args_2)
