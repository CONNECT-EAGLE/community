"""Check real directory behavior for external records and empty launch state."""

import unittest

from build_directory import render


class DirectoryTests(unittest.TestCase):
    def test_empty_registry_does_not_invent_projects(self):
        result = render([])
        self.assertIn("Accepted registry entries: **0**", result)
        self.assertIn("## Community infrastructure", result)
        self.assertIn("No accepted registry entries in this category yet.", result)

    def test_record_keeps_ownership_status_and_escapes_markdown(self):
        project = {
            "project": {"name": "A | B [link]", "description": "<img src=x>"},
            "eagle": {"mission": ["VSWIR", "TIR"]},
            "project_type": "software",
            "status": "active",
            "maintainers": [{"name": "Researcher"}],
            "repository": "https://github.com/researcher/example",
            "collaboration": {"open": True},
        }
        result = render([project])
        self.assertIn("A &#124; B \\[link\\]", result)
        self.assertIn("&lt;img src=x&gt;", result)
        self.assertIn("| active | Researcher |", result)
        for section in [
            "Active projects",
            "Tools",
            "VSWIR",
            "TIR",
            "Multi-sensor / supporting EO",
            "Open for collaboration",
        ]:
            body = result.split(f"## {section}\n", 1)[1].split("\n## ", 1)[0]
            self.assertIn("https://github.com/researcher/example", body)

    def test_archived_record_is_not_advertised_as_available_work(self):
        project = {
            "project": {"name": "Past project", "description": "Historical"},
            "eagle": {"mission": ["TIR"]},
            "project_type": "research",
            "status": "archived",
            "repository": "https://github.com/owner/history",
            "collaboration": {"open": True},
        }
        result = render([project])
        for section in ["Active projects", "Open for collaboration"]:
            body = result.split(f"## {section}\n", 1)[1].split("\n## ", 1)[0]
            self.assertNotIn("Past project", body)
        self.assertIn("Confirm with maintainer", result)


if __name__ == "__main__":
    unittest.main()
