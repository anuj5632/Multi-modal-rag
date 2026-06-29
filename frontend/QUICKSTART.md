# Quick Start Guide

Get the RAG Assistant frontend running in 5 minutes.

## Prerequisites

- Node.js 18+ installed
- pnpm package manager (or npm/yarn)
- Backend API running on `http://localhost:8000`

## Installation (2 minutes)

```bash
# Navigate to project
cd /vercel/share/v0-project

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

The app will be available at **http://localhost:3000**

## First Steps (3 minutes)

### 1. Open the App
Navigate to http://localhost:3000 - you'll see the welcome screen.

### 2. Check Connection
- Header shows "Connected" or "Disconnected"
- If disconnected, verify backend is running on `http://localhost:8000`

### 3. Upload a Document
- Drag and drop a PDF or Word document onto the upload area
- Or click to browse your files
- Wait for the upload to complete

### 4. Ask a Question
- Type a question about your document
- Click send or press Enter
- View results with source citations

### 5. Customize Settings
- Click the ⚙️ icon in the header
- Adjust model, Top K, and temperature
- Settings automatically save

## Toggle Dark Mode

Click the 🌙 icon in the header to switch between light and dark themes.

## Key Shortcuts

| Action | Shortcut |
|--------|----------|
| New line in chat | Shift + Enter |
| Send message | Enter |
| Toggle theme | Click 🌙 icon |
| Open settings | Click ⚙️ icon |
| Upload file | Click 📎 icon or drag-drop |

## Configuration

### Change Backend URL

Edit `.env.local` (create if it doesn't exist):

```env
NEXT_PUBLIC_API_URL=http://your-backend-url:8000
```

Then restart the development server.

### Change Models

Models are configured in `lib/constants.ts`:

```typescript
export const MODELS = [
  { value: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash' },
  { value: 'gpt-4o', label: 'GPT-4o' },
  { value: 'claude-sonnet', label: 'Claude Sonnet' },
]
```

## Troubleshooting

### "Disconnected" Status
- Ensure backend API is running on `http://localhost:8000`
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Run `curl http://localhost:8000/health` to verify

### Upload Fails
- Check file size (max 50MB)
- Verify file format: PDF, DOCX, PNG, JPG
- Ensure `/upload` endpoint exists on backend

### Chat Not Working
- Check backend is running
- Verify `/chat` endpoint exists and accepts POST requests
- Check browser console for errors (F12)

### Settings Not Saving
- Ensure localStorage is enabled
- Try clearing browser cache
- Check for browser privacy mode

## Mobile Testing

Resize your browser or use DevTools device emulation:

```bash
# In Chrome DevTools
Ctrl+Shift+M (or Cmd+Shift+M on Mac)
```

The app is fully responsive and works on:
- iPhone/iPad
- Android phones
- Tablets
- Desktop browsers

## Next Steps

1. **Explore Settings**: Adjust AI model and parameters
2. **Upload Documents**: Try different file types
3. **Ask Questions**: Test various query types
4. **Customize**: Edit colors and theme in `app/globals.css`
5. **Deploy**: Ready to deploy to Vercel or Docker

## Production Build

```bash
# Build for production
pnpm build

# Start production server
pnpm start
```

## Need Help?

- Check `README.md` for detailed documentation
- See `IMPLEMENTATION.md` for architecture details
- Review component code - they're well commented
- Check browser console (F12) for error messages

---

**Happy chatting! 🚀**
