{ pkgs, lib, ... }:

let
  # Native shared libraries that the pip-installed PyQt6 / Qt6 wheels load at
  # runtime but do NOT bundle themselves (GL drivers, the X11/XCB stack, glib,
  # ...). Without these on LD_LIBRARY_PATH you get errors like:
  #   ImportError: libGL.so.1: cannot open shared object file
  runtimeLibs = with pkgs; [
    stdenv.cc.cc.lib        # libstdc++
    libGL                   # libGL.so.1  <- the lib missing in the traceback
    glib
    zlib
    zstd                    # libzstd.so.1 (needed by Qt6 QtCore)
    bzip2                   # libbz2.so.1
    brotli                  # libbrotlidec.so.1
    harfbuzz                # libharfbuzz.so.0
    krb5                    # libgssapi_krb5.so.2
    libxkbfile              # libxkbfile.so.1
    fontconfig
    freetype
    dbus
    libxkbcommon
    libdrm
    expat
    pango
    cairo
    wayland

    # QtWebEngine (pyqt6-webengine) extras
    nss
    nspr
    cups
    alsa-lib
    systemd                 # libudev.so.1
    libgbm                  # libgbm.so.1 (WebEngine GPU)
    libxshmfence            # libxshmfence.so.1 (WebEngine GPU)
    libpulseaudio           # libpulse.so.0 (QtMultimedia audio)
    vulkan-loader           # libvulkan.so.1 (WebEngine RHI; falls back to GL)

    # X11 / XCB stack required by Qt's "xcb" platform plugin
    xorg.libX11
    xorg.libXext
    xorg.libXrender
    xorg.libXi
    xorg.libXrandr
    xorg.libXcursor
    xorg.libXcomposite
    xorg.libXdamage
    xorg.libXfixes
    xorg.libXtst
    xorg.libXScrnSaver
    xorg.libxcb
    xorg.xcbutil
    libxcb-image
    libxcb-keysyms
    libxcb-render-util
    libxcb-wm
    libxcb-cursor           # libxcb-cursor.so.0 (hard requirement for Qt 6)
  ];
in
{
  # Use a Nix-provided CPython so the libs above are ABI-compatible with it,
  # and let uv resolve/install the project deps from uv.lock. The default
  # nixpkgs python3 is already 3.13.x, which satisfies requires-python>=3.13,
  # so we don't pin a version (pinning would require the nixpkgs-python input).
  languages.python = {
    enable = true;
    uv.enable = true;
  };

  # Make uv target the interpreter devenv provides rather than fetching its own
  # standalone build.
  env.UV_PYTHON_PREFERENCE = "only-system";
  env.UV_PYTHON_DOWNLOADS = "never";

  # The actual fix for the libGL.so.1 / xcb errors.
  env.LD_LIBRARY_PATH = lib.makeLibraryPath runtimeLibs;

  enterShell = ''
    echo "mnemosyne devenv ready."
    echo "  uv sync          # install deps into .venv"
    echo "  uv run mnemosyne # launch the app"
  '';
}
