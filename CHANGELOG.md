# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2026-06-17

### Added
- Driver `ydotool` for GNOME Wayland (auto when `WAYLAND_DISPLAY` + `ydotool` in PATH)
- Env override `URISYS_HIM_DRIVER`
- Tests `tests/test_him_driver.py`

### Changed
- `_driver` — domyślnie `pyautogui` na X11; Wayland → `ydotool` gdy dostępny

## [0.1.2] - 2026-06-16

### Docs
- Update README.md

## [0.1.1] - 2026-06-16

### Docs
- Update README.md

### Other
- Update uv.lock

