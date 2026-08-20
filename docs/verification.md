# Verification record

Verification environment: Ubuntu 24.04 under WSL2, ROS 2 Jazzy, Gazebo Harmonic, Python 3.12.

## Completed automated gates

```bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --event-handlers console_direct+
source install/setup.bash
python3 -m pytest
colcon test --event-handlers console_direct+
colcon test-result --verbose
```

Results recorded on 2026-08-19:

- `rosdep`: all required dependencies satisfied;
- `colcon build`: four packages completed;
- portable suite: 32 passed;
- `colcon test`: 2 passed, 0 errors, 0 failures, 0 skipped.

## Controlled navigation gate

The controlled Gazebo/Nav2 run and the live Mistral phrase check are recorded only after the terminal Nav2 result was observed. A Mistral interpretation alone was not counted as navigation success.

Results recorded on 2026-08-19:

- Gazebo Harmonic launched the reviewed warehouse world and robot;
- Nav2 lifecycle nodes reached the active state and AMCL initialized at the home pose;
- the phrase `the battery is almost dead` intentionally bypassed the deterministic keyword aliases;
- Mistral returned the allow-listed destination `charging_station`;
- the canonical configuration resolved that destination to `(5.5, 0.0, 0.0)`;
- Nav2 completed the corresponding `NavigateToPose` goal with terminal status `SUCCEEDED` and result error code `0`;
- a return goal to `home` also completed successfully for the route capture.

No API credential, response metadata, account data, or machine-specific path appears in the captured evidence.

## Security gate

- no credential is stored in tracked source or documentation;
- API access uses `MISTRAL_API_KEY` from the process environment;
- the previously persistent shell assignment was removed, its old credential was revoked, and the protected rollback copy was deleted before staging;
- generated build/install/log state is ignored;
- an exact-value scan and generic credential-pattern scan are required immediately before staging and immediately after the final commit.
