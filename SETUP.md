# Publish the profile

Create a **public** repository named **FireFlamingo** under the FireFlamingo account, using the `main` branch. Upload `README.md`, `assets/`, `scripts/`, and `.github/` with their directory structure intact. The root README then appears on the account overview.

The ready-made SVGs work immediately. The included GitHub Actions workflow refreshes the calendar daily at approximately 03:23 UTC; it can also be run from **Actions → Refresh contribution trace → Run workflow**. Scheduled runs can be delayed by GitHub. Scheduled workflows in inactive public repositories may be disabled after 60 days; re-enable from Actions if needed. No personal access token or third-party statistics service is required. Repository policy must allow the workflow to write repository contents.

The profile deliberately uses only the account handle. It does not include a personal-site URL, email, or legal-name metadata. Existing account fields, pinned repositories, linked repository content, and commit authors are outside this README's control.

## Animation

GitHub READMEs support images, not arbitrary page JavaScript. The SVG wordmark resolves from hexadecimal characters into FireFlamingo, while a wireframe flamingo draws itself. The identity reveal plays once; a small copper trace continues moving in the background. The calendar's copper sweep reveals real daily activity once when its image loads, in about three seconds. Browsers and GitHub's image caching control whether it replays on navigation. The README cannot animate GitHub's own contribution calendar below the profile.

All artwork uses the specified charcoal, warm white, muted gray, and copper palette, including when GitHub is in light mode. Graphics include descriptive alternative text and a `prefers-reduced-motion` override. Without animation support, the finished graphic remains visible. No remote fonts, scripts, or tracking images are used.

This is GitHub's **public contribution calendar**, including commits, issues, pull requests, and reviews, not a commits-only counter. It uses the latest 365 available days. The public GitHub calendar is fetched directly; its HTML format is not a versioned API. The generator validates dates, counts, and intensity levels and fails instead of publishing fabricated or empty data if that format changes. Existing graphics remain available when refresh fails.

## Edit and regenerate

Edit the visual project descriptions, colors, layout, animation timings, and handle in `scripts/build_assets.py`. Update the matching alternative text in `README.md`. Project cards are individual linked SVG images so the colors carry over to the actual GitHub profile. GitHub still controls the surrounding page background and native text styling.

The README intentionally uses one HTML paragraph with adjacent images and `align="top"`. Keep the image tags together without whitespace or blank lines between them: GitHub paragraph margins and inline-image baselines otherwise introduce visible seams. The SVG generator includes all charcoal padding. Section order is identity, contributions, selected projects, working stack, and footer.

```sh
python scripts/build_assets.py
```

Python 3.10+ is sufficient, with no packages to install. `assets/contributions.json` contains the actual public counts used by the graphic.

## Content sources

Project descriptions were checked against the public Pcap-Analyzer and hashing-login READMEs, and Commit's web landing page, directory tree, and extension manifest. Tool interests were supplied by the owner's portfolio. Competition results were omitted at the owner's request. Descriptions do not assert independent security audits or certifications for these projects. The IEEE phishing repository had only a title at the time of review, so it was not promoted as a finished project.

[GitHub profile README requirements](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme)
