import requests

# FQDN for the authentication microservice
BASE_URL = ("http://travelator-auth-09."
            "g7hmghc2bjgaafhb.uksouth.azurecontainer.io:5000")

session = requests.Session()


def test_register_and_login():
    # Register a user
    register_data = {
        "email": "testuser12@example.com",
        "password": "admin"
    }

    register_response = session.post(
        f"{BASE_URL}/register",
        json=register_data
    )

    print(
        "Registration Response:",
        register_response.status_code,
        register_response.json()
    )

    # Log in a user
    login_data = {
        "email": "testuser12@example.com",
        "password": "admin"
    }

    login_response = session.post(f"{BASE_URL}/login", json=login_data)
    print("Login Response:", login_response.status_code, login_response.json())

    if login_response.status_code == 200:
        # Validate session
        validate_response = session.get(f"{BASE_URL}/validate")
        print(
            "Validation Response:",
            validate_response.status_code,
            validate_response.json()
        )

        # Log out the user
        logout_response = session.post(f"{BASE_URL}/logout")
        print(
            "Logout Response:",
            logout_response.status_code,
            logout_response.json()
        )


if __name__ == "__main__":
    test_register_and_login()
