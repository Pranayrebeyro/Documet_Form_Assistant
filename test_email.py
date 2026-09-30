from email_service import send_email


success, message = send_email(
    "YOUR_TEST_EMAIL@gmail.com",
    "Document Assistant Test",
    "This is a test email from the Document & Form Assistant.",
)


print(success)
print(message)