# Source provenance

Original evidence remained read-only. The repository was reconstructed from reviewed source files rather than publishing either supplied archive wholesale. Build products, logs, caches, machine paths, documents, slide decks, and credentials were excluded.

## Evidence SHA-256

| Evidence label | SHA-256 |
| --- | --- |
| `warehouse_robot_project.zip` | `07c747c7a4cd90dfc59d8609e250a4a3735f68b8f79870f99479b75f0e0977cf` |
| `COMP219_project_001_team1.zip` | `bb49d1fb3b4c4df98390f74a2655bd1ed8ae952ab0ac5da96ffd3b0b3a079b18` |
| `COMP219_Report_Final (1).docx` | `23d4e75f44d966076e76f51509e334d291803222687f05e30e4dc98b96187a2e` |
| `COMP219_Presentation.pptx` | `73fa61a261187e847eda06f342177f853c3c8d8569376177035e513fffa016f0` |
| `COMP219_Script (1).docx` | `b18956477fa24328cbcbf4ab1960262fba0687ad1d4406a50be33ff75324a6e9` |
| standalone Mistral prototype | `be2e58b018a624146c6d8039843dc6fc9bf5fd9eeb511a9ac951915788f0e03c` |
| alternate WSL Mistral prototype | `e9bc39237b727e028f45ba5d8d7a39a30971f4028ca846264cee02e6d9591673` |

## Canonical source snapshot SHA-256

| Relative source path | SHA-256 |
| --- | --- |
| `warehouse_robot_description/CMakeLists.txt` | `9043efd596a40818ec9aaccff07d519fb9293aca956fd27223b64c475fc2aa38` |
| `warehouse_robot_description/launch/view_robot.launch.py` | `ed41b45fc4ec95b31787f42d4287226c095de02f0f1712eddb390279471ea665` |
| `warehouse_robot_description/package.xml` | `fe35059ff582bd30882d11a4a833ec4d9e2a076046b2407d33d7c17ba4b9a562` |
| `warehouse_robot_description/urdf/robot.urdf.xacro` | `b098c1a8dc20dc6a56316b66d2ce24cb126acf4e4a042ad8671ae558f1f9aba9` |
| `warehouse_robot_llm/package.xml` | `950f6b0de8cd137e8ce4d09b76da7e5c67e2df3790d4ca812565e26923e06527` |
| `warehouse_robot_llm/setup.cfg` | `872814f4fbcc41f398359faf8694631693e10fb7574a83e0fe3763145a604ae7` |
| `warehouse_robot_llm/setup.py` | `64f02d5da06cfe203c68b45e22c41f2d3d7b447d19ca2cb5e59eaf30a13b2193` |
| `warehouse_robot_llm/warehouse_robot_llm/llm_nav_node.py` | `70bf465ad27260960bef88d8a31092eb53ddb8fe60c299ee611fcc51425ccc8b` |
| `warehouse_robot_nav/CMakeLists.txt` | `5d31091ecaa282bd720f2c18e6c5c1c68c27ef060172abe3aa85968975b8c9c8` |
| `warehouse_robot_nav/launch/nav2.launch.py` | `96f3c8632e16dddf0ae4d19f4c1dccc8c759e7b61114f709de1a8826fa983008` |
| `warehouse_robot_nav/launch/slam.launch.py` | `a0d70cdfdf62dea6e3a64124f93adbda3d56ab708b7fd77b84994c9b4570e499` |
| `warehouse_robot_nav/maps/warehouse_map.pgm` | `b0cd84be4b16f21c37fc81d9990336a47dde611c280b6281b2de0304769a27dc` |
| `warehouse_robot_nav/maps/warehouse_map.yaml` | `cccbfec25e7de312c6b114bf1a3011aed683ab1b8353e36f4dce53df4b0b1868` |
| `warehouse_robot_nav/package.xml` | `4b25cc0d01b89be52aa30699cbabd3f10f5b034d0c7b74254be636c726f08165` |
| `warehouse_robot_nav/params/nav2_params.yaml` | `61924289e562c1e44c8a9bf180880fed62ea73032f9b0485e7d94e6fc8b1882b` |
| `warehouse_robot_nav/params/slam_params.yaml` | `996385f26445103dcea891b0b52e54742203f955e62530ba7ef12beb071c886a` |
| `warehouse_robot_nav/rviz/nav2.rviz` | `b5ebec363f931b76fc1a8fbba3b7b00bb768668d76d38c495dd2b2be834e6ac1` |
| `warehouse_robot_nav/src/nav_menu.cpp` | `db18af56b3dd5fe755d47346d72b85fbbb294a3b41883460910f5e069e89926d` |
| `warehouse_robot_sim/CMakeLists.txt` | `d7a6800777750ecd8631cd3a6a63514fcff131b9b1c10111ca967c4c1c61e104` |
| `warehouse_robot_sim/launch/sim.launch.py` | `3085ced05289a8fbbbe63d961f556d483ec13f235f2d02cd749de49e6d6bbfe8` |
| `warehouse_robot_sim/package.xml` | `6351bc0bd3c0842bb534c79f97f35159527f45ca99f5fed28719dcf08fba26c9` |
| `warehouse_robot_sim/worlds/warehouse.world` | `e5a913eb8377399af092302797e3c8f07c521fbf6b457498c6f1e079a53c91cf` |

Empty package marker files hash to SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## Reconciliation decisions

- The submitted Python command node is documented as deterministic keyword matching.
- The Mistral code is a separate portfolio enhancement.
- Safe approach coordinates from the C++ menu and later Mistral prototype replace conflicting values in the submitted Python dictionary.
- The shelf-only alternate prototype was not copied because it describes a different location model.
- Nav2 result callbacks now distinguish success from cancellation, abort, rejection, and transport errors.
- Dynamic-obstacle claims were narrowed to tested static-obstacle avoidance and costmap replanning.
