# Frontend Configuration Guide

## Changing the Backend URL

To change the backend API URL, you only need to modify **ONE file**:

### File: `lib/api.ts`

```typescript
// Line 2-3: Change this URL to match your backend deployment
export const API_BASE_URL = 'http://localhost:8000';
```

### Examples:

**Local Development:**
```typescript
export const API_BASE_URL = 'http://localhost:8000';
```

**Production Deployment:**
```typescript
export const API_BASE_URL = 'https://your-backend.com';
```

**Different Port:**
```typescript
export const API_BASE_URL = 'http://localhost:8001';
```

That's it! All API calls throughout the application will automatically use this URL.

## Environment Variables (Alternative)

For more flexibility, you can also use environment variables. Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Then update `lib/api.ts`:

```typescript
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

Remember to restart your dev server after changing environment variables!

