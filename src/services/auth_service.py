
class Auth_Service:
    def login(self, username: str, password: str):
        # Placeholder for actual authentication logic
        if username == "" and password == "":
            return "", "account_id_123"
        else:
            raise ValueError("Invalid username or password")