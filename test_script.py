import requests

# FQDN for the authentication microservice
BASE_URL = ("http://travelator-auth-09."
            "g7hmghc2bjgaafhb.uksouth.azurecontainer.io:5000")


def test_register_and_login():
    # To register a user, pass email and
    # password to the /register path as shown below
    register_data = {
        "email": "testuser10@example.com",
        "password": "admin"
    }

    register_response = requests.post(
        f"{BASE_URL}/register",
        json=register_data
    )

    print(
        "Registration Response:",
        register_response.status_code,
        register_response.json()
    )

    # To log in a user, pass the email and
    # password to the /login path and CAPTURE THE JWT TOKEN
    login_data = {
        "email": "testuser10@example.com",
        "password": "admin"
    }

    login_response = requests.post(f"{BASE_URL}/login", json=login_data)
    print("Login Response:", login_response.status_code, login_response.json())

    if login_response.status_code == 200:
        # That's how you get the token from the response
        token = login_response.json().get('token')

        # To validate a session add the token TO
        # THE HEADER as show below and get the response
        headers = {"Authorization": f"Bearer {token}"}
        validate_response = requests.get(
            f"{BASE_URL}/validate",
            headers=headers
        )

        print(
            "Validation Response:",
            validate_response.status_code,
            validate_response.json()
        )

        # To log out the user add the token to
        # the header to remove it from the cache
        logout_response = requests.post(
            f"{BASE_URL}/logout",
            headers=headers
        )
        print(
            "Logout Response:",
            logout_response.status_code,
            logout_response.json()
        )


if __name__ == "__main__":
    test_register_and_login()
