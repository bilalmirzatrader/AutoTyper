# Auto Type - Password Protection

The Auto Type application now includes password protection to control access to the software. This document explains how the password protection works and how to use it.

## How Password Protection Works

When the application is launched, a login dialog will appear requesting a password. This password is validated against a secure source:

- The application connects to a Pastebin URL to fetch the correct password
- The password is stored in a JSON format with the key "access_code"
- If the entered password matches the one stored in Pastebin, the application will start
- If the password is incorrect, the application will close immediately

## Important Notes

1. **Internet Connection Required**: The application needs internet access to validate the password. If no internet connection is available, the application cannot authenticate and will not run.

2. **Password Updates**: The password can be updated by changing the content of the Pastebin file. All users will immediately be required to use the new password.

3. **Password Source**: The password is checked from: https://pastebin.com/raw/eKiZCNbX

## For Administrators

If you are the administrator responsible for maintaining this application:

1. The JSON in the Pastebin should have the following format:
   ```json
   {
     "access_code": "your_password_here"
   }
   ```

2. To update the password, simply edit the Pastebin content with a new password value.

3. You can modify the source code to point to a different Pastebin URL if needed.

## Security Considerations

This password protection method provides basic access control but is not intended as a high-security solution. The Pastebin URL is embedded in the application code, and determined users could potentially extract it.

For higher security needs, consider implementing:
- Server-side authentication
- Encryption of credentials
- Secure token-based authentication
