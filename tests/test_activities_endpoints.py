"""Tests for the FastAPI activities endpoints.

This test suite uses the AAA (Arrange-Act-Assert) testing pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the code/endpoint being tested
- Assert: Verify the results match expectations
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Verify all activities are returned."""
        # Arrange
        # No setup needed - endpoint returns existing data
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0

    def test_get_activities_contains_expected_activities(self, client):
        """Verify specific activities are present in the response."""
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Science Club"
        ]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity in expected_activities:
            assert activity in activities

    def test_get_activities_has_correct_structure(self, client):
        """Verify each activity has required fields."""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_participants_are_emails(self, client):
        """Verify participants are stored as email strings."""
        # Arrange
        # No setup needed
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                # Basic email validation (contains @)
                assert "@" in participant


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_success(self, client):
        """Verify a new participant can sign up for an activity."""
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_signup_participant_appears_in_activity(self, client):
        """Verify signed-up participant appears in activities list."""
        # Arrange
        activity = "Programming Class"
        email = "testuser@mergington.edu"
        
        # Act - Sign up
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act - Verify in activities list
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert email in activities[activity]["participants"]

    def test_signup_duplicate_prevention(self, client):
        """Verify same email cannot sign up twice for same activity."""
        # Arrange
        activity = "Tennis Club"
        email = "duplicate@mergington.edu"
        
        # Act - First signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert - First signup should succeed
        assert response1.status_code == 200
        
        # Act - Second signup with same email
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert - Second signup should fail
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_activity_not_found(self, client):
        """Verify error when signing up for non-existent activity."""
        # Arrange
        activity = "NonexistentActivity"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_with_special_characters_in_activity_name(self, client):
        """Verify signup works with activity names containing spaces."""
        # Arrange
        activity = "Basketball Team"
        email = "basketball@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert - Should handle URL encoding correctly
        assert response.status_code == 200
        
        # Act - Verify in list
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert email in activities[activity]["participants"]

    def test_signup_multiple_different_participants(self, client):
        """Verify multiple different participants can sign up."""
        # Arrange
        activity = "Art Studio"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Act - Sign up multiple participants
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Act - Verify all are in the list
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for email in emails:
            assert email in activities[activity]["participants"]


class TestRemoveFromActivity:
    """Tests for POST /activities/{activity_name}/remove endpoint."""

    def test_remove_participant_success(self, client):
        """Verify a participant can be removed from an activity."""
        # Arrange
        activity = "Drama Club"
        email = "removeme@mergington.edu"
        
        # Act - Sign up participant
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act - Remove participant
        response = client.post(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert email in data["message"]
        assert activity in data["message"]

    def test_remove_participant_no_longer_in_list(self, client):
        """Verify removed participant is no longer in activity."""
        # Arrange
        activity = "Debate Team"
        email = "removetest@mergington.edu"
        
        # Act - Sign up
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act - Remove
        client.post(f"/activities/{activity}/remove", params={"email": email})
        
        # Act - Verify not in list
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert email not in activities[activity]["participants"]

    def test_remove_participant_not_enrolled(self, client):
        """Verify error when removing participant not enrolled."""
        # Arrange
        activity = "Science Club"
        email = "notenrolled@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_remove_from_nonexistent_activity(self, client):
        """Verify error when removing from non-existent activity."""
        # Arrange
        activity = "FakeActivity"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_remove_twice_fails_second_time(self, client):
        """Verify removing same participant twice fails on second attempt."""
        # Arrange
        activity = "Chess Club"
        email = "removeme2@mergington.edu"
        
        # Act - Sign up
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act - First removal
        response1 = client.post(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        
        # Assert - First removal succeeds
        assert response1.status_code == 200
        
        # Act - Second removal attempt
        response2 = client.post(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        
        # Assert - Second removal fails
        assert response2.status_code == 400
        data = response2.json()
        assert "not signed up" in data["detail"]


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirect(self, client):
        """Verify root endpoint redirects to index.html."""
        # Arrange
        # No setup needed
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers.get("location", "")
