from research_explorer import Division, Faculty, Publication


def test_directory_records_are_immutable_and_keep_cross_division_membership() -> None:
    division = Division("epidemiology", "Epidemiology", "https://example.edu", "https://example.edu/faculty")
    faculty = Faculty("u123", "Ada Example", "https://example.edu/ada", (division.id, "general-medicine"))
    publication = Publication("p1", "A public study", faculty_ids=(faculty.id,), division_ids=faculty.division_ids)

    assert faculty.division_ids == ("epidemiology", "general-medicine")
    assert publication.faculty_ids == ("u123",)
