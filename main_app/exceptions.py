class OTPExpiredException(Exception):
    def __init__(self, message="Expired or invalid OTP provided."):
        self.message = message
        super().__init__(self.message)
