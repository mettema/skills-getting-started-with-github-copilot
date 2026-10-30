"""Tests for the Mergington High School activities API.

All tests follow the AAA (Arrange-Act-Assert) pattern.
"""

from src.app import activities


class TestRoot:
    def test_root_redirects_to_static_index(self, client):
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client):
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == len(activities)

    def test_get_activities_includes_expected_fields(self, client):
        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        for details in data.values():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details


class TestSignup:
    def test_signup_adds_participant(self, client):
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity}"
        assert email in activities[activity]["participants"]

    def test_signup_returns_404_for_unknown_activity(self, client):
        # Arrange
        activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_rejects_duplicate_email(self, client):
        # Arrange
        activity = "Chess Club"
        email = activities[activity]["participants"][0]

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
        assert activities[activity]["participants"].count(email) == 1


class TestUnregister:
    def test_unregister_removes_participant(self, client):
        # Arrange
        activity = "Chess Club"
        email = activities[activity]["participants"][0]

        # Act
        response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity}"
        assert email not in activities[activity]["participants"]

    def test_unregister_returns_404_for_unknown_activity(self, client):
        # Arrange
        activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_returns_400_for_email_not_signed_up(self, client):
        # Arrange
        activity = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"


class TestSignupUnregisterFlow:
    def test_signup_then_unregister_then_signup_again(self, client):
        # Arrange
        activity = "Basketball Club"
        email = "flowstudent@mergington.edu"

        # Act - sign up
        signup_response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert - signed up
        assert signup_response.status_code == 200
        assert email in activities[activity]["participants"]

        # Act - unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister", params={"email": email}
        )

        # Assert - removed
        assert unregister_response.status_code == 200
        assert email not in activities[activity]["participants"]

        # Act - sign up again
        resignup_response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert - signed up again
        assert resignup_response.status_code == 200
        assert email in activities[activity]["participants"]
