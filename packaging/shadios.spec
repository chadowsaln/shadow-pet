Name:           shadios
Version:        1.3.0
Release:        3%{?dist}
Summary:        Interactive pixel art desktop pet companion for Linux
License:        MIT
BuildArch:      noarch

Requires:       python3
Requires:       python3-gobject
Requires:       gtk3
Requires:       cairo
Requires:       pango

%description
SHADIOS is an interactive, animated pixel-art desktop pet for Linux (GNOME / Wayland / X11).
It features full Arabic and English dialogue, music bopping, coding mode, jumping,
autonomous screen wandering, spider-man wall climbing, dynamic resizing, and autostart support.

%prep
# No prep required

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/shadios
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/metainfo
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/64x64/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/128x128/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps

install -m 755 %{_sourcedir}/shadios %{buildroot}%{_bindir}/shadios
install -m 755 %{_sourcedir}/shadios_pet.py %{buildroot}%{_datadir}/shadios/shadios_pet.py
install -m 644 %{_sourcedir}/shadios_spritesheet.png %{buildroot}%{_datadir}/shadios/shadios_spritesheet.png
install -m 644 %{_sourcedir}/io.github.shadios.pet.desktop %{buildroot}%{_datadir}/applications/io.github.shadios.pet.desktop
install -m 644 %{_sourcedir}/io.github.shadios.pet.metainfo.xml %{buildroot}%{_datadir}/metainfo/io.github.shadios.pet.metainfo.xml

install -m 644 %{_sourcedir}/icons/io.github.shadios.pet-64.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/io.github.shadios.pet.png
install -m 644 %{_sourcedir}/icons/io.github.shadios.pet-128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/io.github.shadios.pet.png
install -m 644 %{_sourcedir}/icons/io.github.shadios.pet-256.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/io.github.shadios.pet.png

%files
%{_bindir}/shadios
%{_datadir}/shadios/
%{_datadir}/applications/io.github.shadios.pet.desktop
%{_datadir}/metainfo/io.github.shadios.pet.metainfo.xml
%{_datadir}/icons/hicolor/64x64/apps/io.github.shadios.pet.png
%{_datadir}/icons/hicolor/128x128/apps/io.github.shadios.pet.png
%{_datadir}/icons/hicolor/256x256/apps/io.github.shadios.pet.png

%changelog
* Sun Oct 11 2026 SHADIOS Team - 1.3.0-3
- Extend the rappel web from the pet to the top edge of the monitor

* Sun Oct 11 2026 SHADIOS Team - 1.3.0-2
- Make the RPM build script portable and isolate temporary build files
- Align package changelog with the packaged application version
