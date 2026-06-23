from password_utils import (
    hash_password,
    verify_password
)

password = "MyPassword123"

hashed = hash_password(password)

print("Hash:")
print(hashed)

print(
    verify_password(
        "MyPassword123",
        hashed
    )
)

print(
    verify_password(
        "wrongpassword",
        hashed
    )
)