# Documentation

This folder contains project documentation and media files.

## 📄 Project Report

Upload the **project_report.pdf** file here:
- Full technical documentation
- Circuit diagrams and schematics
- Hardware specifications
- Test results and analysis

## 📹 Videos

Create a `videos/` subfolder and upload demonstration videos:
- System demonstration
- Eye tracking in action
- Obstacle avoidance testing
- Setup and calibration guide

## 🖼️ Images

Create a `system_images/` subfolder for:
- Hardware assembly photos
- Component close-ups
- System in operation
- Circuit board layouts

## How to Upload Files

1. **Upload PDF Report:**
   ```bash
   # Navigate to docs folder
   cd docs
   
   # Upload the PDF
   git add project_report.pdf
   git commit -m "Add project report PDF"
   git push
   ```

2. **Upload Videos:**
   ```bash
   # Create videos directory
   mkdir videos
   cd videos
   
   # Add video files
   git add demo.mp4
   git commit -m "Add demonstration video"
   git push
   ```

3. **Upload Images:**
   ```bash
   # Create images directory
   mkdir system_images
   cd system_images
   
   # Add image files
   git add *.jpg *.png
   git commit -m "Add system images"
   git push
   ```

## GitHub Web Interface

Alternatively, use GitHub's web interface:
1. Navigate to the `docs/` folder
2. Click "Add file" → "Upload files"
3. Drag and drop your files (PDF, videos, images)
4. Add a commit message
5. Click "Commit changes"

**Note:** GitHub has file size limits:
- Files up to 25 MB can be uploaded via web interface
- For larger video files, consider using Git LFS or hosting on YouTube/Vimeo and linking here

## Recommended Video Hosting

For large video files, consider hosting on:
- **YouTube** (Unlisted or Public)
- **Vimeo**
- **Google Drive** (with public sharing link)

Then add the links to the main README.md file.
