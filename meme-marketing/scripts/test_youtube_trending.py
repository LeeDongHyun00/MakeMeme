import unittest
from datetime import datetime, timezone

import youtube_trending as yt

NOW = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)


def make_item(video_id, published_at, **statistics):
    return {
        "id": video_id,
        "snippet": {
            "title": f"title {video_id}",
            "channelTitle": "channel",
            "publishedAt": published_at,
        },
        "statistics": statistics,
    }


class ComputeMetricsTest(unittest.TestCase):
    def test_normalizes_views_by_hours_since_publish(self):
        item = make_item("a", "2026-11-20T02:00:00Z", viewCount="1000000", likeCount="50000", commentCount="2000")
        row = yt.compute_metrics(item, NOW)
        self.assertEqual(row["hours_since_publish"], 10.0)
        self.assertEqual(row["views_per_hour"], 100000)
        self.assertEqual(row["like_rate"], 0.05)
        self.assertEqual(row["comment_rate"], 0.002)

    def test_hidden_like_count_yields_none_instead_of_zero(self):
        item = make_item("b", "2026-11-19T12:00:00Z", viewCount="2400")
        row = yt.compute_metrics(item, NOW)
        self.assertIsNone(row["likes"])
        self.assertIsNone(row["like_rate"])
        self.assertEqual(row["views_per_hour"], 100)

    def test_just_published_video_uses_one_hour_floor(self):
        item = make_item("c", "2026-11-20T11:59:00Z", viewCount="500")
        row = yt.compute_metrics(item, NOW)
        self.assertEqual(row["views_per_hour"], 500)

    def test_zero_views_does_not_divide_by_zero(self):
        item = make_item("d", "2026-11-20T02:00:00Z", viewCount="0", likeCount="0")
        row = yt.compute_metrics(item, NOW)
        self.assertIsNone(row["like_rate"])


class BuildRowsTest(unittest.TestCase):
    def test_ranks_fast_recent_video_above_older_video_with_more_views(self):
        old = make_item("old", "2026-11-14T12:00:00Z", viewCount="3000000")
        fresh = make_item("fresh", "2026-11-20T06:00:00Z", viewCount="600000")
        rows = yt.build_rows([old, fresh], NOW)
        self.assertEqual([row["video_id"] for row in rows], ["fresh", "old"])

    def test_table_escapes_pipe_in_title(self):
        item = make_item("e", "2026-11-20T02:00:00Z", viewCount="10")
        item["snippet"]["title"] = "a | b"
        table = yt.format_table(yt.build_rows([item], NOW))
        self.assertIn("a / b", table)


if __name__ == "__main__":
    unittest.main()
