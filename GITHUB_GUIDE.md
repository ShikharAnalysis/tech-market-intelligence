# Upload and share

The package is ready for a new repository. It has not been uploaded to your GitHub account, and no account access was used.

## Browser upload

1. Sign in to GitHub and create a repository named `tech-market-intelligence`.
2. Suggested description: `Technology market opportunity analysis using USAspending data, Python, SQL and an interactive decision dashboard.`
3. Extract the ZIP locally. Upload the **contents** of the project folder so `README.md` and `index.html` sit at repository root. Use **Add file → Upload files** or the new repository's existing-file upload link.
4. Preserve folders. Commit with a message such as `Add reproducible market opportunity analysis`.
5. Check that `src`, `sql`, `data`, `docs`, `reports` and `.github/workflows` are present. Hidden folders can be missed by manual file selection.
6. Open README and confirm its result chart renders. The Actions tab should show the validation workflow if `.github/workflows/validate.yml` was included.

GitHub browser upload supports up to 100 files at once and 25 MiB per file at the time of preparation. This package fits those limits. If your browser fails to retain folders, use GitHub Desktop or Git.

## Git command-line alternative

Install Git and create an empty repository on GitHub without initializing additional files. In the local project folder:

```bash
git init
git add .
git commit -m "Add reproducible market opportunity analysis"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/tech-market-intelligence.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual username. Authenticate through Git's supported sign-in flow. These commands assume a new local folder and empty remote; do not use force-push to resolve a different setup.

## Optional GitHub Pages dashboard

After upload, open repository **Settings → Pages**. Select **Deploy from a branch**, choose `main` and `/(root)`, then save. After deployment, use the URL GitHub shows; it is normally `https://YOUR_USERNAME.github.io/tech-market-intelligence/`.

The `index.html` file is the dashboard entry point. The included `.nojekyll` file allows straightforward static-file serving. The Pages deployment is separate from the analysis validation workflow. Verify the final link in a private browser window before adding it to your resume.

## Final portfolio checks

- Readme opens with the correct result chart and working relative links.
- Dashboard opens, charts render and controls work.
- Source code and real data provenance are visible.
- Personal interpretation is written in your own words.
- You can explain the main calculations and limitations.
- Do not invent a deployed URL before GitHub supplies one.

Official references: [uploading files](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository) and [configuring Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site). Interface and plan availability can change.
