# SHADIOS

SHADIOS is an animated Arabic and English desktop pet for Linux, written in Python with GTK 3.

## Build an RPM on Fedora

Install the RPM build tools and the application's runtime libraries:

```bash
sudo dnf install rpm-build python3-gobject gtk3 cairo pango
```

Build the package from the project directory:

```bash
bash packaging/build_rpm.sh
```

The resulting package is written to `dist/`. Install it with:

```bash
sudo dnf install ./dist/shadios-1.3.0-3.fc44.noarch.rpm
```

Then launch **SHADIOS** from the desktop application menu or run `shadios` in a terminal.

## Repository

The Git remote is `https://github.com/chadowsaln/shadow-pet.git`. The remote currently has no advertised branches, so this working tree is not based on an existing remote revision.
