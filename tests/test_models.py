from research_explorer.models import Division, Faculty, collect_directory, normalize_directory


def test_collect_directory_uses_the_public_adapter_protocols() -> None:
    class Directory:
        def collect_divisions(self):
            return [Division("epi", "Epidemiology", "", "")]

        def collect_faculty(self, division):
            return [Faculty("ada", "Ada", "", division_ids=(division.id,))]

    directory = collect_directory(Directory())
    assert directory["faculty"][0]["id"] == "ada"


def test_normalize_directory_preserves_a_flat_directory() -> None:
    directory = normalize_directory(
        {
            "settings": {"max_publications_per_faculty": 12},
            "divisions": [{"id": "epi", "name": "Epidemiology"}],
            "faculty": [{"id": "ada", "full_name": "Ada", "division_ids": ["epi"]}],
        }
    )

    assert directory["settings"]["max_publications_per_faculty"] == 12
    assert directory["faculty"][0]["division_ids"] == ["epi"]


def test_normalize_directory_migrates_legacy_nested_profiles() -> None:
    directory = normalize_directory(
        {
            "network": {"max_works_per_researcher": 8},
            "organizations": [
                {
                    "id": "epi",
                    "name": "Epidemiology",
                    "researchers": [{"id": "ada", "full_name": "Ada", "collect_works": False}],
                }
            ],
        }
    )

    assert directory["divisions"] == [
        {"id": "epi", "name": "Epidemiology", "source_url": "", "faculty_url": "", "summary": ""}
    ]
    assert directory["faculty"][0]["collect_publications"] is False
