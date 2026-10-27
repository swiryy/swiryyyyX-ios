#!/usr/bin/env python3
"""Build the pinned experimental swiryyyyX port; device output remains unsigned."""
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def run(*args, cwd=None):
    subprocess.run(args, cwd=cwd, check=True)


def main():
    versions = json.loads((HERE / 'versions.json').read_text())
    configuration = os.environ.get('SWIRIX_CONFIGURATION', 'debug_sim_arm64')
    if configuration not in ('debug_sim_arm64', 'release_arm64'):
        sys.exit('Unsupported build configuration')
    device_build = configuration == 'release_arm64'
    pin = (HERE / 'UPSTREAM_COMMIT').read_text().strip()
    if not re.fullmatch(r'[0-9a-f]{40}', pin):
        sys.exit('Invalid upstream commit pin')
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        sys.exit('This baseline job requires an Apple Silicon macOS runner')
    actual = subprocess.check_output(['xcodebuild', '-version'], text=True).splitlines()[0]
    if actual != f"Xcode {versions['xcode']}":
        sys.exit(f"Expected Xcode {versions['xcode']}; found {actual}")
    if int(platform.mac_ver()[0].split('.')[0]) < int(versions['macos']):
        sys.exit(f"Expected macOS {versions['macos']} or later")
    api_id = os.environ.get('TELEGRAM_API_ID', '')
    api_hash = os.environ.get('TELEGRAM_API_HASH', '')
    if not api_id.isdigit() or int(api_id) <= 0 or not re.fullmatch(r'[0-9a-fA-F]{32}', api_hash):
        sys.exit('Set the owner TELEGRAM_API_ID and TELEGRAM_API_HASH Actions secrets')
    root = Path(os.environ['RUNNER_TEMP']) / 'swiryyyyx-swiftgram'
    if root.exists():
        sys.exit('Build destination already exists; refusing to overwrite it')
    run('git', 'init', str(root))
    run('git', 'remote', 'add', 'origin', 'https://github.com/Swiftgram/Telegram-iOS.git', cwd=root)
    run('git', 'fetch', '--depth=1', 'origin', pin, cwd=root)
    run('git', 'checkout', '--detach', 'FETCH_HEAD', cwd=root)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    if head != pin:
        sys.exit('Upstream checkout does not match pin')
    run('git', 'submodule', 'update', '--init', '--recursive', '--jobs', '4', cwd=root)
    patch = HERE / 'swiryyyyX-ios.patch'
    run('git', 'apply', '--check', str(patch), cwd=root)
    run('git', 'apply', str(patch), cwd=root)
    tests = Path(os.environ['RUNNER_TEMP']) / 'swirix-hidden-tests'
    run('swiftc', '-swift-version', '5',
        str(root / 'Swiftgram/SGSimpleSettings/Sources/SwirixHiddenChats.swift'),
        str(root / 'Tests/SwirixHiddenChatsTests.swift'), '-o', str(tests))
    run(str(tests))
    # Use the existing provisioning switch for simulator and unsigned device
    # archives. Device output must be re-signed by the owner before installation.
    make_path = root / 'build-system/Make/Make.py'
    make_source = make_path.read_text()
    start = make_source.index('\ndef build(bazel, arguments):')
    anchor = '    bazel_command_line.set_configuration(arguments.configuration)'
    position = make_source.index(anchor, start)
    make_source = (make_source[:position] +
                   "    bazel_command_line.set_disable_provisioning_profiles()\n"
                   "    if os.environ.get('SWIRIX_REPOSITORY_CACHE'):\n"
                   "        bazel_command_line.common_args.append('--repository_cache=' + os.environ['SWIRIX_REPOSITORY_CACHE'])\n"
                   "    if arguments.configuration == 'release_arm64':\n"
                   "        bazel_command_line.common_args.append('--features=disable_legacy_signing')\n"
                   "        bazel_command_line.common_args.append('--//Telegram:disableExtensions')\n\n" +
                   make_source[position:])
    make_path.write_text(make_source)
    if configuration == 'release_arm64':
        # The pinned ios_application rule embeds a profile even when its
        # existing disable_legacy_signing feature disables archive signing.
        # Omit that embedding only for this explicitly unsigned CI archive.
        rules_path = root / 'build-system/bazel-rules/rules_apple/apple/internal/ios_rules.bzl'
        rules_source = rules_path.read_text()
        profile_anchor = ("    if platform_prerequisites.platform.is_device:\n"
                          "        processor_partials.append(\n"
                          "            partials.provisioning_profile_partial(")
        application_start = rules_source.index('def _ios_application_impl(')
        application_end = rules_source.index('\ndef ', application_start + 1)
        application_source = rules_source[application_start:application_end]
        if application_source.count(profile_anchor) != 1:
            sys.exit('Unsigned archive profile rule anchor changed')
        application_source = application_source.replace(
            profile_anchor,
            profile_anchor.replace('platform.is_device:',
                                   'platform.is_device and "disable_legacy_signing" not in features:'),
            1)
        rules_path.write_text(rules_source[:application_start] + application_source + rules_source[application_end:])
    config = json.loads((root / 'build-system/template_minimal_development_configuration.json').read_text())
    config.update(bundle_id='ua.swiryyyyx.client', api_id=api_id, api_hash=api_hash,
                  team_id='', app_specific_url_scheme='swiryyyyx', sg_config='')
    config_path = root / 'build-system/swiryyyyx-ci.json'
    config_path.touch(mode=0o600)
    config_path.write_text(json.dumps(config))
    try:
        run(sys.executable, '-u', 'build-system/Make/Make.py',
            '--cacheDir=' + str(Path(os.environ['RUNNER_TEMP']) / 'swiryyyyx-bazel-cache'),
            'build', '--configurationPath=' + str(config_path), '--xcodeManagedCodesigning',
            '--configuration=' + configuration, '--buildNumber=' + os.environ.get('GITHUB_RUN_NUMBER', '1'),
            cwd=root)
    finally:
        config_path.unlink(missing_ok=True)
    import shutil
    artifacts = Path(os.environ['RUNNER_TEMP']) / 'swiryyyyx-artifacts'
    artifacts.mkdir()
    archive = root / 'bazel-bin/Telegram/Swiftgram.ipa'
    if device_build:
        import plistlib
        import zipfile
        with zipfile.ZipFile(archive) as package:
            plists = [name for name in package.namelist() if name.startswith('Payload/') and name.endswith('.app/Info.plist') and name.count('/') == 2]
            if len(plists) != 1:
                sys.exit('Device archive has no unique application Info.plist')
            metadata = plistlib.loads(package.read(plists[0]))
            if metadata.get('CFBundleSupportedPlatforms') != ['iPhoneOS'] or metadata.get('CFBundleIdentifier') != 'ua.swiryyyyx.client':
                sys.exit('Archive is not the expected swiryyyyX iPhone application')
        shutil.copyfile(archive, artifacts / 'swiryyyyX-unsigned.ipa')
        print('Unsigned iPhone IPA compiled; owner signing and real-device validation remain pending.')
    else:
        shutil.copyfile(archive, artifacts / 'swiryyyyX-simulator.zip')
        print('Experimental simulator port compiled; this archive cannot be installed on iPhone.')


if __name__ == '__main__':
    main()
