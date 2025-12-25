# Coordinate Converter - Vercel Deployment

This is a Flask-based coordinate converter application prepared for deployment on Vercel.

## Project Structure

```
.
├── api/
│   └── index.py          # Vercel serverless function (Flask app)
├── templates/
│   └── index.html        # Frontend template
├── converters.py         # Coordinate conversion logic
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
└── app.py               # Original Flask app (for local development)
```

## Local Development

To run locally:

```bash
pip install -r requirements.txt
python app.py
```

The app will be available at `http://localhost:5000`

## Deployment to Vercel

### Option 1: Using Vercel CLI

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Deploy:
   ```bash
   vercel
   ```

3. Follow the prompts to complete deployment.

### Option 2: Using Git Integration

1. Push your code to GitHub, GitLab, or Bitbucket
2. Import your repository in the Vercel dashboard
3. Vercel will automatically detect the configuration and deploy

## Features

- WGS84 to Minna Datum conversion
- WGS84 to UTM conversion
- Minna Datum to WGS84 conversion
- Minna UTM to WGS84 conversion
- Minna Geographic to UTM conversion
- Interactive map visualization
- GPS location support
- DMS (Degrees, Minutes, Seconds) input support

## Dependencies

- Flask >= 2.3.0
- pyproj >= 3.6.0

## Notes

- The `api/index.py` file is the entry point for Vercel's serverless functions
- Templates are automatically found via the configured template folder path
- The `converters.py` module is imported from the parent directory

