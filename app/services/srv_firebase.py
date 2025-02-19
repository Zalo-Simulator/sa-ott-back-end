import firebase_admin
from firebase_admin import credentials, auth


class FireBaseService:
    def __init__(self):
        self.cred = credentials.Certificate(
            "app/config/zalo-simulator-firebase-adminsdk-fbsvc-e5177bee4c.json"
        )
        firebase_admin.initialize_app(self.cred)

    def login_with_phone(phone_number: str):
        try:
            # Tạo hoặc lấy user với số điện thoại
            user = auth.get_user_by_phone_number(phone_number)
            print(f"✅ User found: {user.uid}")

        except firebase_admin.auth.UserNotFoundError:
            # Nếu chưa có, tạo mới user
            user = auth.create_user(phone_number=phone_number)
            print(f"🆕 User created: {user.uid}")

        return user
