# Patches for Submodules

This directory contains patches that are automatically applied to git submodules during devcontainer setup.

## dndtemplate-submodule-fonts.patch

**Target**: `dungeonsheets/modules/DND-5e-LaTeX-Character-Sheet-Template/dndtemplate.sty`

**Purpose**: Fix font path resolution when MSavage's template is used as a submodule.

**Issue**: The original template uses `Path=template/fonts/` which is a relative path that only works when compiling from the repository root directory. When used as a submodule, XeLaTeX cannot find the fonts.

**Solution**: Use `\currfiledir` to create an absolute path from the .sty file location. This makes the template work both as a standalone repository and as a submodule.

**Original**:
```latex
\newfontfamily\entryfont{Kalam}[Path=template/fonts/,Extension=.ttf,UprightFont=Kalam-Regular,BoldFont=Kalam-Bold]
```

**Patched**:
```latex
\newfontfamily\entryfont{Kalam}[Path=\currfiledir template/fonts/,Extension=.ttf,UprightFont=Kalam-Regular,BoldFont=Kalam-Bold]
```

**Upstream**: This change could potentially be contributed back to the matsavage repository to make it more submodule-friendly.
