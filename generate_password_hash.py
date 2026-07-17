"""
Run this once to create the ADMIN_PASSWORD_HASH value for your .env file.

Usage:
    python generate_password_hash.py

It will ask you to type a password (hidden input) and print a hash you
can paste into .env as ADMIN_PASSWORD_HASH=... — the real password is
never stored anywhere, only this hash.
"""
import getpass
from werkzeug.security import generate_password_hash

if __name__ == "__main__":
    password = getpass.getpass("Choose an admin password: ")
    confirm = getpass.getpass("Type it again to confirm: ")

    if password != confirm:
        print("\nThose passwords didn't match. Please run the script again.")
    elif len(password) < 8:
        print("\nPlease choose a password with at least 8 characters.")
    else:
        print("\nAdd this line to your .env file:\n")
        print(f"ADMIN_PASSWORD_HASH={generate_password_hash(password)}")
