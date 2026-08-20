# Case study: autonomous warehouse navigation

## Challenge

The team needed a mobile robot to localize and travel between meaningful warehouse destinations rather than raw coordinates. The deliverable had to combine simulation, mapping, navigation, and an operator-friendly command layer within a course-project schedule.

## Anton's contribution

Anton Ilin created the custom Gazebo warehouse, manually mapped it for localization, and prototyped a Mistral-backed natural-language parser. The project was completed by a five-person team; other work is credited collectively to the team/group members.

## Course baseline

The submitted Python implementation did not make a live LLM call. It scanned normalized input for configured names such as `aisle 2`, `packing station`, or `home`, then sent the associated pose through `NavigateToPose`. This deterministic implementation is preserved as the course baseline.

## Portfolio hardening

Repository reconstruction exposed three incompatible coordinate sets. The final design moves all destinations into one installed CSV contract shared by C++ and Python. Physical-model centers were compared with the occupancy map and approach poses; safe approach coordinates were selected rather than targets inside collision geometry.

Action clients were also hardened. A callback now reports success only for Nav2's terminal succeeded status and separately handles rejection, cancellation, abort, unknown results, and callback failures.

## Mistral enhancement

The portfolio extension reads an API key only from process environment, asks Mistral for a small JSON response, and rejects any destination outside the configured allow-list. Typed network, timeout, authorization, schema, and allow-list failures fall back to deterministic parsing.

The phrase `the battery is almost dead` deliberately bypasses keyword aliases. It is used as the live semantic validation phrase and counts as validated only when Mistral resolves `charging_station` and Nav2 subsequently reports a successful charging-station goal.

## Honest scope

The world contains static obstacles. LiDAR feeds Nav2 obstacle layers, and the verified project demonstrates planning and avoidance in that static environment. It does not claim tested performance with moving people, vehicles, or dynamically spawned obstacles.

## Outcome

The result is a reproducible ROS 2 workspace with one location contract, portable tests, corrected action semantics, build automation, source provenance, secret controls, and a portfolio presentation that distinguishes submitted work from later engineering.
