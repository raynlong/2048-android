[app]

# (str) Title of your application
title = 2048

# (str) Package name
package.name = game2048

# (str) Package domain (needed for android/ios packaging)
package.domain = com.game

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (list) List of inclusions using pattern matching
source.include_patterns = src/*.py

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests,bin,venv,.git

# (list) List of exclusions using pattern matching
source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 1.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.1

# p4a settings for reliability
p4a.branch = develop
p4a.ndk_version = 26d

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (str) Presplash background color (RGB like #FFFFFF or named color)
presplash.color = #FAF8EF

# (str) Icon of the application
# icon.filename = %(source.dir)s/icon.png

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/presplash.png

# (str) Application font (used by Kivy to render text)
# android.fonts = DroidSansFallback.ttf,DroidSans-Bold.ttf

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86_64
android.archs = arm64-v8a

# (int) Minimum API required
android.minapi = 23

# (int) Android SDK version to use
android.sdk = 33

# (int) Android NDK version to use
# Using p4a.ndk_version above instead; comment out android.ndk
# android.ndk = 25b

# (int) Android SDK tools version
# android.sdk_tools = 26.1.1

# (bool) Use the AndroidX support library
android.use_androidx = True

# (list) Permissions
android.permissions = INTERNET, VIBRATE

# (list) Features required (empty to auto-detect)
android.features = android.hardware.touchscreen

# (bool) If True, then skip trying to update the SDK/NDK/ANT
android.skip_update = False

# (bool) If True, then automatically accept SDK license agreements
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy
android.entrypoint = org.kivy.android.PythonActivity

# (list) Java classes to add as activities to the manifest
# android.add_activity =

# (list) Java files to compile & add
# android.add_src =

# (str) OUYA Console category (auto vs game)
# android.ouya.category = game

# (str) Filename of the custom AndroidManifest
# android.manifest.custom =

# (str) Additional Java archives
# android.add_jars =

# (list) Android libraries to include
# android.add_libs_armeabi_v7a =
# android.add_libs_arm64_v8a =

# (bool) Enable AndroidX
# android.use_androidx =

# (bool) Copy libraries instead of making libpacks
# android.copy_libs =

# (list) The Android project metadata keys to set
# android.meta_data =

# (list) Scheme list for URL handling
# android.url_scheme =

# (list) Services to run in background
# android.services =

# (str) The logcat filter
# android.logcat_filters = *:S python:D

# (bool) If True, then show error messages as a Toast
# android.show_loading_icon = True

# (str) Gradle build tool version
# android.gradle_version = 8.2.1

# (str) Android Gradle plugin version
# android.agp_version = 8.2.0

# (bool) Automated packaging
# android.release = True

# (str) Keystore for release builds
# android.release.keystore =
# android.release.keystore_alias =
# android.release.keystore_pass =
# android.release.key_pass =

#
# iOS specific
#

# (str) Path to custom Info.plist
# ios.info_plist =

# (str) Bundle identifier
# ios.bundle_identifier = org.test.myapp

# (str) The executable name
# ios.executable_name = myapp

# (str) The bundle name
# ios.bundle_name = My App

# (str) The bundle version
# ios.bundle_version = 1.0

# (list) The frameworks to link
# ios.frameworks = UIKit,CoreGraphics

# (bool) Allow iPad support (default: False)
# ios.allow_ipad = False

# (list) Icons
# ios.icons = icon-57.png,icon-60.png,icon-72.png,icon-76.png


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 1

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, default is under the source dir
# build_dir = %(source.dir)s/.buildozer

# (str) Path to the build output (i.e. .apk, .ipa) storage
# bin_dir = %(source.dir)s/bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as a option to the list.
#    Let's take [app] / source.exclude_patterns.
#    Instead of doing:
#
#        [app]
#        source.exclude_patterns = license,data/audio/*.wav,data/images/original/*
#
#    This can be translated into:
#
#        [app]
#        source.exclude_patterns = license
#                                 data/audio/*.wav
#                                 data/images/original/*
#


#    -----------------------------------------------------------------------------
#    Profiles
#
#    You can extend section / key with a profile
#    For example, you want to deploy a demo version of your application without
#    HD content. You could first change the title to add "(demo)" in the name
#    and extend the excluded directories to remove the HD content.
#
#        [app@demo]
#        title = My Application (demo)
#
#        [app:source.exclude_patterns@demo]
#        images/hd/*
#
#    Then, invoke the command line with the "demo" profile:
#
#        buildozer --profile demo android debug
