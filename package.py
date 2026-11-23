"""
Standalone Portable Distribution Packager for FireBox.
Bundles FireBox into a portable zip archive and distribution bundle.
"""

import os
import shutil
import zipfile
from pathlib import Path
from firebox.version import VERSION

ROOT = Path(__file__).parent.resolve()
DIST_DIR = ROOT / "dist"
ARCHIVE_NAME = f"firebox-v{VERSION}-portable.zip"


def build_portable_package():
    """Package FireBox into a standalone portable ZIP."""
    print(f"Building FireBox v{VERSION} portable bundle...")
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = DIST_DIR / ARCHIVE_NAME

    exclude_patterns = {
        "__pycache__", ".pytest_cache", ".git", ".venv",
        "venv", ".qodo", "dist", "*.pyc", "*.bak"
    }

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for foldername, subfolders, filenames in os.walk(ROOT):
            # Prune excluded directories
            subfolders[:] = [d for d in subfolders if d not in exclude_patterns]
            rel_folder = Path(foldername).relative_to(ROOT)

            if any(p in str(rel_folder) for p in ("dist", ".git", ".pytest_cache", "__pycache__")):
                continue

            for filename in filenames:
                if filename.endswith((".pyc", ".bak", ".zip")):
                    continue
                file_path = Path(foldername) / filename
                arcname = Path("firebox") / rel_folder / filename
                zf.write(file_path, arcname)

    print(f"✔ Created portable package: {zip_path} ({zip_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    build_portable_package()
