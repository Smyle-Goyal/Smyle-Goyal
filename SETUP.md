# Smyle's Flower Contribution Garden 🌸

This is a GitHub profile README starter based on the profile layout you shared. It keeps the typing banner, badges, About section, technology icons and links, but replaces the contribution snake with a flower garden.

## Files

- `README.md` — profile page content
- `scripts/generate_flowers.py` — gets the contribution calendar through GitHub GraphQL and draws the SVG flowers
- `.github/workflows/update-flowers.yml` — refreshes the garden daily and commits the updated SVG
- `assets/flower-contributions.svg` — generated image displayed in the profile README

## Setup

1. Create or open the special profile repository named **`Smyle-Goyal`**. It must be public and the repository name must exactly match your GitHub username.
2. Copy these files into the root of that repository, preserving the folders.
3. In the repository, open **Settings → Secrets and variables → Actions → New repository secret**.
4. Name the secret `PROFILE_TOKEN`. Use a GitHub Personal Access Token (classic) with the `read:user` scope. Keep the token private; never paste it into `README.md` or commit it.
5. Open **Actions**, enable workflows if GitHub asks, select **Bloom the contribution garden**, then choose **Run workflow**.
6. Wait for the run to finish. It should create/update `assets/flower-contributions.svg`. The README image will then appear on your profile.
7. Edit the placeholder email and LinkedIn URL in `README.md`.

## Flower stages

- No contributions: quiet soil dot
- 1 contribution: sprout
- 2–3 contributions: bud
- 4+ contributions: blooming flower; higher counts get a larger bloom / alternate petal color

The garden shows GitHub's contribution calendar for the last year. GitHub's calendar can include activity from repositories according to your contribution visibility and GitHub's own counting rules.

## Troubleshooting

- **`Bad credentials` / HTTP 401:** recreate the token and update the `PROFILE_TOKEN` repository secret.
- **Resource not accessible by personal access token:** check the token's `read:user` permission and that the secret name is exactly `PROFILE_TOKEN`.
- **Image is broken:** confirm `assets/flower-contributions.svg` exists on the `main` branch and the README image path is exactly `./assets/flower-contributions.svg`.
- **Workflow does not run on schedule:** scheduled actions may be delayed; run it manually from the Actions tab. GitHub can disable scheduled workflows in inactive repositories.
- **The image doesn't update:** check the Actions run log and the generated SVG diff.

## Run locally (optional)

Set environment variables `GITHUB_USERNAME=Smyle-Goyal` and `PROFILE_TOKEN=<your token>`, then run:

```bash
python scripts/generate_flowers.py
```

No third-party Python packages are required.
