import requests


BASE_URL = (
    "https://auth.voya-trips.com"
)

BASE_URL = (
    "http://127.0.0.1:5050"
)


# Create a session to persist cookies across requests
session = requests.Session()


def test_register_and_login():
    # Register a user
    register_data = {
        "email": "testuser21@example.com",
        "password": "Admin123?"
    }

    register_response = session.post(
        f"{BASE_URL}/register", json=register_data
    )

    print(
        "Registration Response:",
        register_response.status_code,
        register_response.json()
    )

    # Log in a user
    login_data = {"email": "testuser21@example.com", "password": "Admin123?"}

    login_response = session.post(f"{BASE_URL}/login", json=login_data)
    print("Login Response:", login_response.status_code)

    if login_response.status_code == 200:
        # Validate session
        validate_response = session.get(f"{BASE_URL}/validate")
        print(
            "Validation Response:",
            validate_response.status_code,
        )

        # Log out the user
        logout_response = session.post(f"{BASE_URL}/logout")
        print(
            "Logout Response:",
            logout_response.status_code,
        )


if __name__ == "__main__":
    test_register_and_login()
