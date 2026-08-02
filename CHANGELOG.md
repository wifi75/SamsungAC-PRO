# Changelog

## [9.3.1-pro] - 2026-08-02

### Changed
- **Faster-feeling switches**: legacy 2878 switches (Purify, Auto Clean, Beep, Display) now update the toggle in Home Assistant immediately, before the command round-trip to the device completes, matching the optimistic-update behavior the climate entity already had. If the device rejects the command or is unreachable, the toggle is reverted to its previous state instead of being left showing the wrong value.

## [9.3.0-pro] - 2026-08-02

Stable release consolidating the `9.2.1-pro.1` through `9.2.1-pro.7` line.

### Fixed
- **False "persistently offline" on session collision**: a brief network blip no longer forces a fully working AC unavailable within ~20-30 seconds; stale-session recovery now waits appropriately, and commands fail fast instead of hanging for up to 20 seconds during that recovery window.
- **Root cause of spurious authentication failures**: the device's post-greeting `InvalidateAccount` handshake message - a normal "please authenticate" step - is no longer misread as a failed login when it arrives as a separate TCP segment over a flaky Wi-Fi link.
- **Capability-aware legacy controls**: Display and Beep switches are now exposed only when the device actually reports `AC_ADD_LIGHT` / `AC_ADD_VOLUME`.
- **Filter reset state**: `0` and `240` are now treated as valid idle states while the accepted reset command remains `On`.
- **Rejected command handling**: Samsung `Status="Fail"` responses now return their error code immediately instead of causing a 20-second timeout and forced reconnection.
- **Legacy AC Turbo preset**: `AC_FUN_COMODE=TurboMode` is recognized in the legacy `special` preset mapping, preventing Home Assistant from immediately correcting an infrared-activated Turbo/Boost state back to `off`.
- **Legacy timeout diagnostics**: 2878 command timeouts now include the affected command summary; connection-close timeouts after a command timeout are logged at debug instead of warning level.

### Added
- **Capability diagnostics (`AC_ADD2_OPTIONCODE`)**: decodes the device's capability bitmask (heating availability, horizontal swing, Quiet, Turbo/SoftCool, Fahrenheit, SPi/purify, humidity sensor, inverter, power-usage logging) into a `capabilities` block in the Home Assistant diagnostics download.
- **Legacy Display switch**, **Legacy Beep switch** and a **Filter reset button** for port-2878 units.
- **SamsungAC-PRO branding**: original Home Assistant/HACS icon assets and repository-level `brand` directory.

## [9.2.1-pro.7] - 2026-08-02

### Added
- **Capability diagnostics (`AC_ADD2_OPTIONCODE`)**: decode the device's single-integer capability bitmask (heating availability, horizontal swing, Quiet, Turbo/SoftCool, Fahrenheit, SPi/purify, humidity sensor, inverter, power-usage logging, etc.) into a readable `capabilities` block in the Home Assistant diagnostics download. The bitmask table is ported from the official Samsung app and cross-checked against the independently reverse-engineered [porech/pysamsung-dplug](https://github.com/porech/pysamsung-dplug) project. This is diagnostics-only for now (does not change which controls are shown) and lays the groundwork for gating entities on real hardware capability instead of attribute presence.

## [9.2.1-pro.6] - 2026-08-02

### Fixed
- **Root cause of the false "InvalidateAccount" auth failure**: the device always follows its greeting with a separate `<Update Type="InvalidateAccount"/>` push meaning "authenticate on this connection" - a normal handshake step, not an error. When that push arrived as its own TCP segment instead of bundled with the greeting (common over a flaky Wi-Fi link), the legacy 2878 handler left it unread in the socket buffer and misread it as the response to its own AuthToken command, misdiagnosing a completely healthy reconnect as a stale-session collision. The handshake now explicitly drains this push before sending AuthToken, so this no longer happens; the lenient session-collision backoff from pro.5 remains as a safety net for genuine collisions.

## [9.2.1-pro.5] - 2026-08-02

### Fixed
- **False "persistently offline" on session collision**: When the device replies `InvalidateAccount` (a stale session left over from a previous connection still needs to expire), the legacy 2878 handler now waits a fixed 30s per attempt and tolerates up to 6 consecutive collisions before forcing Home Assistant to mark the entity unavailable, instead of sharing the same fast 3-retry exponential backoff used for genuine connection failures. Previously, a brief network blip could trip the offline flag within ~20-30 seconds while the AC was still fully functional and about to reconnect on its own.
- **Early session-collision detection**: The stale-session collision is now also recognized when the device signals `InvalidateAccount` in its very first greeting message (before the auth command is even sent), so a connection drop right after that greeting still gets the lenient 30s backoff instead of the aggressive one.
- **Command fast-fail during session collision**: Home Assistant service calls (turn on/off, set temperature, etc.) issued while a session collision is being waited out now fail immediately instead of blocking for up to 20 seconds.

## [9.2.1-pro.4] - 2026-07-11

### Fixed
- **Legacy timeout diagnostics**: 2878 command timeouts now include the affected command summary, making it easier to identify whether a climate, fan, preset, switch, or polling command caused the timeout.
- **Socket cleanup noise**: Connection-close timeouts after a command timeout are now logged at debug level instead of warning level.
- **Legacy availability handling**: Older 2878 modules now require one additional failed reconnect before Home Assistant marks the unit as persistently offline.

## [9.2.1-pro.3] - 2026-07-11

### Fixed
- **Capability-aware legacy controls**: Display and Beep are now exposed only when the device reports `AC_ADD_LIGHT` or `AC_ADD_VOLUME`, preventing unsupported controls on older firmware.
- **Filter reset state**: Values `0` and `240` are now treated as valid idle states while the accepted reset command remains `On`.
- **Rejected command handling**: Samsung `Status="Fail"` responses now return their error code immediately instead of causing a 20-second timeout and forced reconnection.

## [9.2.1-pro.2] - 2026-07-11

### Added
- **Legacy Display switch**: Added native control of the indoor-unit display light through `AC_ADD_LIGHT`.
- **Legacy Beep switch**: Added native beep mute/unmute control through the protocol-correct `AC_ADD_VOLUME` attribute.
- **Filter reset button**: Added a momentary Home Assistant button that sends `AC_ADD_CLEAR_FILTER_ALARM=On` to reset the filter-cleaning timer.
- **HACS brand assets**: Added the SamsungAC-PRO icon to the repository-level `brand` directory while retaining the local Home Assistant integration assets.

## [9.2.1-pro.1] - 2026-07-11

### Fixed
- **Legacy AC Turbo preset**: Recognize `AC_FUN_COMODE=TurboMode` in the legacy `special` preset mapping, preventing Home Assistant from immediately correcting an infrared-activated Turbo/Boost state back to `off`.

### Added
- **SamsungAC-PRO branding**: Added original Home Assistant and HACS icon assets, project ownership information, and links to the SamsungAC-PRO repository.
- **Turbo/Boost documentation**: Documented the difference between the full Samsung Boost preset and the separate Turbo fan-speed command on legacy port 2878 devices.

## [9.2.1] - 2026-03-03

### Changed
- **Core Stability**: Refactored YAML loading mechanism (`controller_yaml_init.py`) to run safely in Home Assistant's thread pool via `hass.async_add_executor_job`, eliminating Event Loop blocking.
- **HA Standards**: Added `strict_typing: true`, `iot_class: local_polling`, and official `"quality_scale": "gold"` to `manifest.json`.
- **Code Harmonization (DRY)**: Refactored `config_flow.py` to consolidate Samsung schema generation into a unified, parametric base helper (`_get_base_samsung_schema`), reducing boilerplate duplication.
- **Log Refinement**: Downgraded state auto-correction and UI flicker notifications to `DEBUG` level to eliminate information noise in the Home Assistant logs.
- **Encapsulation & Architecture (V7 Audit)**: Created robust public APIs (`last_poll_data`, `connection_diagnostics`) in `controller_yaml.py` and replaced all internal private attribute accesses across `diagnostics.py` and `switch.py`.
- **Hygienic Codebase (V7 Audit)**: Performed a full-scope repository purge of development artifacts: deleted persistent `split_controller.py` build script, eradicated milestone scaffolding blocks, relocated nested inline imports, and cleansed internal `[DIAG]` test prints.

### Fixed
- **Socket Memory Leak (CRITICAL)**: Added explicit `wait_closed()` instructions in `connection_raw.py` to prevent File Descriptor exhaustion and RAM leaks on persistent disconnections.
- **Session Resource Leak**: Fixed `aiohttp.ClientSession` memory leak in `__init__.py` by safely awaiting graceful session teardowns during integration unloads.
- **Asymmetric Unload**: Restructured `async_unload_entry` layout (`__init__.py`) to brutally stop `polling` tasks and network loops *before* attempting HA platform teardown, solving teardown race conditions.
- **Exponential Backoff Spam**: Repaired `samsung_2878.py` fallback loops to ensure reconnect delay times properly increment, preventing the integration from spamming unreachable routers.
- **Dynamic Retry Backoff**: Enhanced `properties.py` with a true exponential backoff algorithm (1s to 15s) for asynchronous retries, replacing static delays and improving recovery responsiveness.
- **Config Flow 500 Errors**: Fixed unhandled exceptions (`AuthError`) causing API crashes during AC device pairing by gracefully mapping them to visible UI alerts.
- **Jinja2 High CPU Usage**: Optimized `Template.render()` validation in `properties.py` using per-poll in-memory caching to eliminate redundant CPU evaluation iterations.
- **Deepcopy RAM Spikes**: Replaced expensive `copy.deepcopy` calls in `controller_yaml_state.py` with fast C-level `json.loads(json.dumps())` combinations to optimize optimistic device state construction.
- **Event Loop Blocking**: Rewrote the fallback reconnect loops in `connection_request.py` to remove `time.sleep()`, using a custom `RetryNextAttempt` exception to delegate waits to the `asyncio` event loop.
- **Exception UX**: Migrated custom exceptions to inherit securely from `HomeAssistantError` and properly implemented the native `ConfigEntryNotReady` backoff manager.
- **Diagnostic Entities**: Mapped nested hardware sensors like `Alarms`, `Filter`, and `Energy` directly to Home Assistant's `entity_category: diagnostic` platform standard, purging "magic string" inference logic.
- **Test Determinism**: Refactored `test_integration.py` to replace hardcoded `asyncio.sleep` calls with dynamic `async_timeout` poll loops, ensuring the test suite is stable across different hardware speeds.
- **Strict Typing Fixes**: Injected missing `Dict[str, Any]` type hints in `__init__.py` to satisfy strict MyPy auditing requirements.

## [9.2.0] - 2026-03-02

### Added
- **Config Flow UX (Connection Test)**: Added a mandatory pre-flight connection test step in the configuration flow that validates the IP and Token against the physical AC unit before the integration is created.
- **Config Flow UX (Port Fallback)**: Added seamless auto-detection when pairing. The integration silently falls back to the alternative protocol port and retries if the user selects the wrong port.
- **YAML Hot-Reload Service**: Added a native `climate_ip.reload` service that purges the internal YAML schema cache and applies mapping changes instantly without restarting Home Assistant.
- **Translations**: Added full native localization support for French (`fr.json`) and German (`de.json`). Created a canonical `strings.json` as the source of truth for all UI translations.
- **Ping Gate**: Implemented fast ICMP connectivity pre-checks before TCP reconnections for all devices, bypassing slow socket timeouts when the AC is offline at the network level.
- **HA Repair Issues**: Automatic creation of Home Assistant Repair Issues when a device repeatedly fails to connect. The issue resolves itself upon successful reconnection.
- **Diagnostic Enhancements**: Secured diagnostic exports using an allowlist approach to guarantee sensitive tokens are never exported, and added visibility of the Keep-Alive fallback state.

### Changed
- **Network Ping Optimization**: Replaced crude OS-level `ping` subprocess calls with lightning-fast, native `icmplib.async_ping`. Gracefully falls back to datagram sockets to reduce File Descriptor exhaustion during disconnects.
- **SSL Configuration Persistence**: The integration now permanently saves the last successful SSL configuration (`cert`, `cipher_name`, `verify_mode`) to allow instant reconnection after a Home Assistant restart.
- **TLS Protocol Tolerance**: Made TLS connections more lenient for older Samsung devices that require lower security levels.
- **urllib3 Context**: Scoped the workaround for Samsung's malformed HTTP headers strictly to this integration's requests, preventing cross-contamination with other Home Assistant integrations.
- **Log Refinement & Error Messages**: Improved connection error logs to be human-readable and downgraded expected structural disconnect logs (`Timeout` and `ConnectionError`) to prevent log spam when a device is powered off.
- **Code Refactoring & Modernization**: Significantly refactored `controller_yaml.py`, modernized integration registration syntax (`domain=DOMAIN`), standardized exception handling with `CannotConnect`, and bumped minimum required Home Assistant version to "2024.1.0".

### Fixed
- **Connection Keep-Alive Hang**: Fixed a structural bug where the integration would hang for 10 seconds waiting after the AC finished responding due to malformed headers. The solution safely strips illegal characters and proactively falls back to `Connection: close` on protocol violations.
- **Critical TLS Hang (AC Port 8888/2878)**: Samsung AC firmware hangs indefinitely when receiving a TLS 1.3 Client Hello. Fixed by capping all SSL context creation strictly at `TLSv1_2`.
- **Connection Cleanup Logging**: Fixed a bug where `ConnectionRequest` session cleanup logic would repeatedly log redundant closure messages during garbage collection. 
- **Config Flow Timeout**: Fixed a bug where port 2878 devices would unconditionally time out during connection testing.
- **SSL Context Handling**: Fixed local listener socket configuration to properly handle server-side handshake requests, and resolved Python `ValueError` exceptions caused by conflicting `check_hostname` assignments.
- **Embedded Command Execution**: Fixed nested YAML commands with parameters (like auto power-on) being silently skipped on older devices.
- **Reconnect Jitter**: Added random jitter to exponential backoffs to prevent "thundering herd" reconnects.
- **Task Tracking**: Fixed orphaned background threads during integration unload.
- **Performance & Data Types**: Fixed sensor definitions by converting YAML strings into native `SensorStateClass` enums, resolved fragile template parameter evaluations, and eliminated redundant string searches.

## [9.0.12] - 2026-02-23

### Added
- **Independent Native Temperature Units**: Added two separate configuration options (`Native Current Temperature Unit` and `Native Target Temperature Unit`) accessible from the integration's Options Flow. This allows devices that report temperatures in Fahrenheit to be correctly converted and displayed in the Home Assistant global unit (Celsius or Fahrenheit), independently for current and target temperatures. New constants `CONF_TEMP_NATIVE_CURRENT` and `CONF_TEMP_NATIVE_TARGET` added to `const.py`.

### Fixed
- **Connection Stability**: Fixed a critical bug in `protocol_8888.py` (RAW connection engine) where a missing `Content-Length` header from the AC would cause the raw socket read fallback loop to hang indefinitely, triggering 30-second `Transient connection failure` timeouts in Home Assistant. The read loop now uses an absolute 5.0-second deadline via `asyncio.wait_for` to guarantee execution.
- **Temperature Display**: Fixed a decimal precision bug in the Home Assistant thermostat card where fractional temperatures (e.g. `20.56°C`) were shown instead of integers. Fixed by explicitly rounding in `convert_dev_to_hass` in `properties.py` and overriding `temperature_unit` in `climate.py` to prevent Home Assistant frontend from applying secondary floating-point conversions. Core climate attributes are also filtered from `extra_state_attributes` to prevent raw values silently overwriting the rounded integers.
- **Switch Validation**: Fixed a bug in `controller_yaml.py` where `device_state` passed to switch `validation_template` was incorrectly typed as a `ClimateIPDeviceState` object instead of a raw dictionary, causing `purify` and `auto_clean` switches to always fail validation and not appear in Home Assistant.
- **YAML Config**: Added `validation_template` to all switches in `samsung_2878.yaml` and `samsungrac.yaml` to correctly hide controls not supported by the device.
- **Logs**: Fixed `beep` (and other unsupported switches) triggering spurious state auto-correction warnings by ensuring properties failing validation are skipped during post-update discrepancy checks.
- **Log Cleanup**: Removed verbose `DEBUG` log statements across `switch.py`, `sensor.py`, `samsung_2878.py`, `controller_yaml.py`, and `properties.py` to reduce log noise.

## [9.0.11] - 2026-02-17

### Fixed
- **Connection Stability (CRITICAL)**:
    - Fixed a regression in 9.0.10 where the `device_id` was not being correctly populated for single-device configurations.
    - Ensured `DUID` is explicitly passed to command templates in `properties.py` to prevent empty DUIDs, resolving timeouts for 2878 devices.
- **Sensor Reliability**: Added safe navigation to the `outdoor_temperature` sensor template in `samsung_2878.yaml` to prevent Jinja2 errors ("dict object has no attribute") during initial connection or partial state updates.
- **Connection Robustness**:
    - Fixed a `NoneType` error that could occur when the connection was closed unexpectedly (e.g., device offline), ensuring proper cleanup and reconnection attempts.
    - Handled `InvalidateAccount` response gracefully during handshake (session collision), triggering a clean retry instead of an error log.
- **Native Switches**:
    - Introduced `switch` platform for `purify` and `auto_clean` controls, replacing the deprecated `switch.template` workarounds.
    - Added dedicated `switches` section to `samsung_2878.yaml` and `samsungrac.yaml` for better configuration management.

## [9.0.10] - 2026-02-17

### Added
- **Polling Control**: Added `Enable Polling` option in configuration flow (default: True). Users can now disable periodic status updates to prevent IP bans on sensitive 2878 devices.
- **Connection**: Added support for **Anonymous TLS** connections (Cipher Suite D: `ALL:@SECLEVEL=0`) for devices that do not require a certificate.
- **Emulator**: Added `--no-cert` flag to `emulator_2878.py` to simulate devices requiring Anonymous TLS.
- **Native Switches**: Introduced `switch` platform for `purify` and `auto_clean` controls, replacing the deprecated `switch.template` workarounds.

### Fixed
- **SSL Compatibility**:
    - Prioritized Anonymous Cipher Suite (Suite D) when no certificate is provided, speeding up connection.
    - Fixed `ValueError` when using `ssl.CERT_NONE` by ensuring `server_hostname` is always passed to `asyncio.open_connection`.
- **Config Flow**: Added `Enable Polling` checkbox to Options Flow for existing installations.
- **Coordinator**: Updated coordinator to respect the polling setting, disabling automatic updates if unchecked.
- **Lifecycle Management**: Improved connection cleanup during reloads to prevent "zombie" connections.

## [9.0.9] - 2026-02-12

### Added
- **Sensors**: Added `auto_clean` and `purify` sensors to `samsungrac.yaml` (8888) and `samsung_2878.yaml` (2878) to monitor these states.

### Fixed
- **Token Acquisition**: Replaced `aiohttp` server with a custom Raw TCP server in `token_acquirer_8888.py` to handle devices with malformed headers (missing `Content-Length`).
- **FilterTime Scaling**: Corrected `FilterTime` value in `samsungrac.yaml` (8888) by dividing by 10.
- **Connection Stability**: Implemented TCP Keep-Alive for port 2878 to prevent zombie connections after router reboots.
- **Service Restoration**: Restored `climate_ip.set_property` service to allow control of custom attributes like `purify` and `auto_clean`.

## [9.0.8] - 2026-02-11

### Fixed
- **Outdoor Temperature**: Changed logic for 8888-port devices to subtract 55 from the raw value and use Celsius units, matching the behavior of 2878-port devices.

## [9.0.7] - 2026-02-11

### Added
- **Sensors (8888 Protocol)**:
    - Added native support for `outdoor_temperature` sensor in `samsungrac.yaml` (8888 models).
    - Added `filter_clean_alarm`, `filter_time`, and `filter_alarm_time` sensors.
    - Implemented logic to expose unwrapped device state in `controller_yaml.py` to allow sensor templates to access nested data easily.

### Changed
- **SSL Security**:
    - Updated `samsung_smartthings_hvac.yaml` and `samsung_smartthings_dhw.yaml` to enforce `insecure_ssl: false` and `verify: True` for secure connections to SmartThings Cloud.
- **Internal**:
    - Updated `sensor.py` to use the new exposed device state for validation, fixing the "missing sensor" issue on 8888 devices.

## [9.0.6] - 2026-01-07

### Added
- **Connection Engines**:
    - Implemented `asyncio.Lock` in `connection_aiohttp.py` and `connection_raw.py` to serialize requests and properly share SSL contexts.
    - Added SSL optimizations (`OP_NO_TICKET`, `OP_NO_COMPRESSION`) in `protocol_8888.py` for low-resource devices.
    - Added tolerant header parsing in `connection_request_tls_auto.py`.
- **Config Flow**:
    - Added connection method selector (`aiohttp`, `requests`, `raw`) in `config_flow.py`.
    - Defined explicit device types for SmartThings HVAC and DHW in `const.py`.
- **Sensors**: Added `sensors` property support in `controller_yaml.py`.
- **Logging**: Added verification logs for SSL optimizations.

### Changed
- **Stability**:
    - Introduced a "strike system" in `coordinator.py` and `samsung_2878.py` (max 3 strikes) to handle transient network failures without marking entities unavailable immediately.
    - Added automatic fallback to the Legacy (requests) engine if `InvalidHeaderError` is detected.
- **Properties**:
    - Fixed temperature conversions (~line 173 `properties.py`) by enforcing float parsing and handling units dynamically.
    - Updated `insecure_ssl` handling in SmartThings YAML templates.

### Fixed
- **Outdoor Temperature**: Corrected calculation in `samsung_2878.yaml` (subtracting 55 from raw value) and set unit to Celsius.
