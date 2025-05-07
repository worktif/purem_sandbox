"""
Business Source License 1.1

Copyright (C) 2025 Raman Marozau, raman@worktif.com
Use of this software is governed by the Business Source License included in the LICENSE.TXT file and at www.mariadb.com/bsl11.

Change Date: Never
On the date above, in accordance with the Business Source License, use of this software will be governed by the open source license specified in the LICENSE file.
Additional Use Grant: Free for personal and non-commercial research use only.

SPDX-License-Identifier: BUSL-1.1
"""

import sys

from src.benchmarks_analysis import BenchmarksAnalysis

if __name__ == "__main__":
    test_id = sys.argv[1]
    platform = sys.argv[2]
    print(f"Working with file: {test_id}")

    BenchmarksAnalysis(test_id, platform).run()