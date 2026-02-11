# TODO - Module Restructuring

## New Dashboard Module (User Session) ✅
- [x] Created `modules/dashboard/dashboard.py` with DashboardModule class
- [x] Left section: User info display
- [x] Middle section: Image display (optional, from constructor)
- [x] Right section: Time logged in + current date/time (real-time updates)

## Rename Existing Dashboard to System Status ✅
- [x] Renamed `modules/dashboard/dashboard.py` → `modules/system_status/system_status.py`
- [x] Moved `modules/dashboard/widgets.py` → `modules/system_status/widgets.py`
- [x] Created `modules/system_status/__init__.py`
- [x] Renamed `DashboardModule` → `SystemStatusModule` in renamed file

## Update Imports and Registration ✅
- [x] Updated `modules/system_status/__init__.py` (created with proper imports)
- [x] Updated `modules/__init__.py` imports
- [x] Updated `main.py` to register both modules

## Core App Enhancements ✅
- [x] Window size - Now dynamically sized to 80% of screen (min 800x600)
- [x] Module toggle menu - Added "Modules" menu with checkboxes
- [x] Menu rebuilds navigation when toggling modules

## Remaining Tasks
- [x] Test application functionality
- [x] Verify all modules load correctly

