#!/bin/bash
set -e

BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PACK_DIR="$BASE_DIR/packaging"
RPMBUILD_DIR="$(mktemp -d "${TMPDIR:-/tmp}/shadios-rpmbuild.XXXXXX")"
trap 'rm -rf -- "$RPMBUILD_DIR"' EXIT

echo "=== تجهيز بيئة بناء حزمة RPM ==="
mkdir -p "$RPMBUILD_DIR"/{BUILD,RPMS,SOURCES,SPECS,SRPMS,tmp,BUILDROOT}

# نسخ الملفات والأصول إلى SOURCES
cp "$BASE_DIR/shadios_pet.py" "$RPMBUILD_DIR/SOURCES/"
cp "$BASE_DIR/shadios_spritesheet.png" "$RPMBUILD_DIR/SOURCES/"
cp "$PACK_DIR/shadios" "$RPMBUILD_DIR/SOURCES/"
cp "$PACK_DIR/io.github.shadios.pet.desktop" "$RPMBUILD_DIR/SOURCES/"
cp "$PACK_DIR/io.github.shadios.pet.metainfo.xml" "$RPMBUILD_DIR/SOURCES/"
cp -r "$PACK_DIR/icons" "$RPMBUILD_DIR/SOURCES/"

# نسخ ملف المواصفات إلى SPECS
cp "$PACK_DIR/shadios.spec" "$RPMBUILD_DIR/SPECS/"

echo "=== بدء بناء الحزمة باستخدام rpmbuild ==="
rpmbuild --define "_topdir $RPMBUILD_DIR" --define "_tmppath $RPMBUILD_DIR/tmp" --define "_buildrootdir $RPMBUILD_DIR/BUILDROOT" -bb "$RPMBUILD_DIR/SPECS/shadios.spec"

echo "=== تم بناء الحزمة بنجاح! ==="
mkdir -p "$BASE_DIR/dist"
cp "$RPMBUILD_DIR"/RPMS/noarch/*.rpm "$BASE_DIR/dist/"
echo "الحزم المنتجة متوفرة في: $BASE_DIR/dist/"
ls -la "$BASE_DIR/dist/"
