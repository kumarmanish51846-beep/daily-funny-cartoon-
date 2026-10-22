# Daily Funny Cartoon Shorts — Cloud starter

This GitHub Actions starter is configured to run daily at about 8:00 AM India time. It creates a 60-second vertical cartoon-style video, a thumbnail, and copy-ready YouTube title/description/hashtags.

## Included outputs
- `funny_cartoon_short.mp4` — vertical 60-second video
- `thumbnail.jpg` — thumbnail image
- `youtube_title_description.txt` — title, description and hashtags

## Setup from an Android phone
1. Download and extract this ZIP.
2. Sign in to GitHub and create a new repository.
3. Upload the files and keep the `.github/workflows/daily-video.yml` folder structure.
4. Open the repository's Actions tab and enable workflows if asked.
5. Select **Daily Funny Cartoon Short** and tap **Run workflow** for a test.
6. When the run finishes, open it and download the artifact under **Artifacts**.
7. Extract the downloaded artifact ZIP to access the MP4, thumbnail, and metadata text file.

## Important limitations
- Uses simple original cartoon-style drawings, not full cinematic AI animation.
- Uses two different Hindi AI voices for the two characters (voice availability depends on the Edge TTS service).
- Background music is not added in this starter, avoiding music copyright issues. You can add royalty-free music later.
- This starter uses a rotating set of sample jokes. Edit `STORIES` in `make_video.py` to add more scripts.
- GitHub's free usage limits apply. Scheduled runs may be delayed; manual run is available in Actions.
- The workflow does not automatically upload to YouTube; it prepares files for you to download and upload.
- Never put passwords or API keys in your repository.
