# Google OAuth API-Only Setup Instructions

## 1. Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing one
3. Enable "Google+ API" or "People API"
4. Go to "Credentials" → "Create OAuth 2.0 Client ID"
5. Choose "Web application"
6. Add authorized JavaScript origins:
   - `http://localhost:3000` (your React frontend)
   - `http://localhost:8000` (your Django backend)
7. Copy the Client ID

## 2. Update Django Settings

In `core/authentication.py`, line 67, replace:
```python
CLIENT_ID = "your-google-client-id.apps.googleusercontent.com"
```
With your actual Google Client ID.

## 3. API Usage

Your React frontend can now use Google OAuth like this:

### Frontend (React) Integration:
```bash
npm install @google-cloud/local-auth google-auth-library
```

```jsx
import { GoogleAuth } from 'google-auth-library';

const handleGoogleLogin = async () => {
  try {
    // Get Google ID token from Google Sign-In
    const response = await gapi.auth2.getAuthInstance().signIn();
    const id_token = response.getAuthResponse().id_token;
    
    // Send to your Django backend
    const apiResponse = await fetch('http://localhost:8000/api/google-auth/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ id_token })
    });
    
    const result = await apiResponse.json();
    
    if (result.success) {
      // Store the API token
      localStorage.setItem('authToken', result.token);
      console.log('User:', result);
      // result contains: user_id, username, email, name, picture, token
    }
  } catch (error) {
    console.error('Google login failed:', error);
  }
};
```

## 4. Available Endpoints

### Manual Registration (existing)
```
POST /api/register/
{
  "username": "user123",
  "email": "user@example.com", 
  "password": "password123"
}
```

### Manual Login (existing)  
```
POST /api/login/
{
  "username": "user123",
  "password": "password123"
}
```

### Google OAuth (new)
```
POST /api/google-auth/
{
  "id_token": "google_id_token_from_frontend"
}
```

Response:
```json
{
  "success": true,
  "user_id": 123,
  "username": "user@example.com",
  "email": "user@example.com",
  "name": "John Doe",
  "picture": "https://lh3.googleusercontent.com/...",
  "token": "abc123...",
  "auth_method": "google",
  "created": true
}
```

## 5. Using the Token

All subsequent API calls should include the token:
```javascript
headers: {
  'Authorization': 'Token ' + localStorage.getItem('authToken')
}
```

## Benefits

✅ **Pure API** - No HTML pages, perfect for separate frontend  
✅ **Same token system** - Google and manual users get same API tokens  
✅ **Auto account creation** - New Google users automatically get accounts  
✅ **User choice** - Frontend can offer both login methods  
✅ **Secure** - Google handles authentication, you just verify tokens
