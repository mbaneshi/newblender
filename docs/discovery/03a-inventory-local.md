# Inventory A — Local corpus per stage (human + internal lenses)

- **Date:** 2026-10-07 · **Index:** [03 — Inventory](03-inventory.md)
- **Root:** `~/agent-native-lab-data/sources/blender/projects.blender.org/`. Every path below was checked with `ls`.
- **Prefixes:**
  - **SBT** = `studio/blender-studio-tools/docs/`
  - **MAN** = `blender/blender-manual/manual/`
  - **DEV** = `blender/blender-developer-docs/docs/`
  - **SRC** = `blender/blender/`
  - **RN** = `DEV release_notes/5.2/`
- **Licences:** all local material is free (GPL code; CC-BY-SA manual and dev docs; CC-BY Studio docs). **[sub]** = linked training that needs a Studio subscription.

## S01 Modeling
| Source | Path / URL | Lens | Why |
|---|---|---|---|
| Studio artist guide: modeling | SBT artist-guide/asset-creation/modeling.md | human | Real studio modeling conventions (richest artist page) |
| Manual: Modeling | MAN modeling/{meshes,modifiers,curves,surfaces,volumes} | human | Every mesh tool and modifier |
| Manual: Sculpt | MAN sculpt_paint/sculpting | human | Sculpt brushes and workflow |
| Dev docs: Mesh / BMesh | DEV features/objects/mesh/ | internal | Edit-mode topology vs Mesh data model |
| Dev docs: attributes, geometry sets | DEV features/objects/{attributes.md,geometry_sets.md} | internal | Generic attribute layer shared with GN |
| Source modules | SRC source/blender/{bmesh, editors/mesh, editors/sculpt_paint, modifiers, editors/transform, blenkernel}; intern/{opensubdiv,quadriflow} | internal | Implementation |
| UI panels | SRC scripts/startup/bl_ui/{space_view3d.py, space_view3d_toolbar.py, properties_data_mesh.py, properties_data_modifier.py} | internal | UI → operators/RNA map |
| Release notes | RN modeling.md, sculpt.md | internal | Version drift |
| Blender Fundamentals 4.5 (free) | https://studio.blender.org/training/blender-fundamentals-45-lts/ | human | Free baseline video course |

## S02 UV & texturing
| Source | Path / URL | Lens | Why |
|---|---|---|---|
| Manual: UV editor | MAN editors/uv | human | Unwrap and UV tools |
| Manual: texture / vertex paint | MAN sculpt_paint/{texture_paint,vertex_paint} | human | Painting on meshes |
| Manual: image editor | MAN editors/image | human | Texture viewing |
| Studio guide: shading | SBT artist-guide/asset-creation/shading.md | human | Studio texturing practice |
| Dev docs: mesh paint | DEV features/sculpt_paint/mesh_paint.md | internal | Paint internals |
| Source modules | SRC source/blender/{editors/uvedit, editors/sculpt_paint, imbuf}; intern/{slim, mikktspace} | internal | Unwrap solvers, tangents |
| UI panels | bl_ui/{space_image.py, properties_paint_common.py} | internal | UV/paint UI |
| UV layout add-on | SRC scripts/addons_core/io_mesh_uv_layout | internal | Python UV access example |

## S03 Shading & materials
| Source | Path / URL | Lens | Why |
|---|---|---|---|
| Studio guide: shading | SBT artist-guide/asset-creation/shading.md | human | Studio material conventions |
| Manual: shader nodes, materials | MAN render/{shader_nodes,materials} | human | Every BSDF/texture node |
| Manual: shader editor | MAN editors/shader_editor.rst | human | Node-editing UX |
| Dev docs: Cycles node guidelines | DEV features/cycles/node_guidelines.md | internal | Shader node design rules |
| Source modules | SRC source/blender/{nodes/shader, editors/space_node, gpu, draw/engines/eevee}; intern/cycles/scene | internal | Graph → GPU/Cycles compile |
| UI panels | bl_ui/{properties_material.py, node_add_menu_shader.py, space_node.py} | internal | Node menus are machine-readable |
| Node Wrangler | SRC scripts/addons_core/node_wrangler | internal | Programmatic node-tree patterns |
| Procedural Shading [sub] | https://studio.blender.org/training/procedural-shading/ | human | Expert course |

## S04 Geometry Nodes / procedural
| Source | Path / URL | Lens | Why |
|---|---|---|---|
| Manual: Geometry Nodes | MAN modeling/geometry_nodes | human | Full node reference |
| Dev docs: nodes | DEV features/nodes/{fields.md, anonymous_attributes.md, geometry_socket.md, adding_a_node.md} | internal | Fields and evaluation model, the declarative core |
| Dev docs: proposals | DEV features/nodes/proposals | internal | "Everything Nodes" rationale |
| Studio add-on: geonode_shapekeys | SBT addons/geonode_shapekeys.md | human | GN in production rigs |
| Source modules | SRC source/blender/{nodes/geometry, geometry, functions, blenkernel (geometry_set)}, editors/space_node | internal | Lazy-function evaluator |
| UI panels | bl_ui/{node_add_menu_geometry.py, properties_physics_geometry_nodes.py} | internal | Node catalogue as data |
| Release notes | RN geometry_nodes.md | internal | Closures, bundles, lists: fast change |
| GN from Scratch [sub] | https://studio.blender.org/training/geometry-nodes-from-scratch/ | human | Pedagogy |

## S05 Rigging
| Source | Path / URL | Lens | Why |
|---|---|---|---|
| CloudRig docs (10 pages) | SBT addons/cloudrig/ | human | Production rig generator, documented in depth |
| Studio guide: rigging | SBT artist-guide/asset-creation/rigging.md | human | Rig hand-off rules |
| Add-ons: easy_weight, pose_shape_keys, lattice_magic | SBT addons/… | human | Weighting and correctives |
| Manual: armatures, constraints, drivers, shape keys | MAN animation/{armatures,constraints,drivers,shape_keys} | human | Building blocks |
| Dev docs: armatures, IK, Rigify | DEV features/animation/{armatures,ik.md,rigify,b-bone_vertex_mapping.md} | internal | Bone math |
| Source modules | SRC source/blender/{animrig, editors/armature, ikplugin}; intern/{iksolver,itasc}; scripts/addons_core/rigify | internal | Rig evaluation, IK |
| UI panels | bl_ui/{properties_data_armature.py, properties_data_bone.py, properties_constraint.py} | internal | Rig UI → RNA |
| Studio Rigging Tools (free) | https://studio.blender.org/training/blender-studio-rigging-tools/ | human | Video companion to CloudRig |

## S06 Layout & scene assembly
| Source | Path / URL | Lens | Why |
|---|---|---|---|
| Asset Pipeline add-on | SBT addons/asset_pipeline.md | human | Task-layer publishing and linking |
| Project-tools: build/update shot, asset | SBT artist-guide/project_tools/{usage-build-shot-core,usage-update-shot,usage-asset}.md | human | Automated shot assembly |
| Studio guide: shot assembly | SBT artist-guide/shot-production/shot-assembly.md | human | Linking and overrides per shot |
| Manual: libraries, assets, collections, outliner | MAN files/{linked_libraries,asset_libraries}, scene_layout/collections, editors/{asset_browser.rst,outliner} | human | Reference |
| Dev docs: library overrides | DEV features/core/overrides/library/{functional_design.md,usd_mapping.md} | internal | Override semantics, which are hard for agents |
| Dev docs: asset system | DEV features/asset_system/ | internal | Catalogs, remote libraries |
| Source modules | SRC source/blender/{asset_system, editors/asset, editors/space_outliner, editors/id_management, blenloader, blenkernel (lib_override)} | internal | Link/override internals |
| Batch scripts | studio/blender-studio-tools/scripts/{resync_blends,remap,bbatch} | internal | Headless resync/remap |
| 2019 asset-publishing proposal | SBT archive/pipeline-proposal-2019/asset-publishing | human | Earlier design reasoning |

## S07 Animation
| Source | Path / URL | Lens | Why |
|---|---|---|---|
| Studio guide: animation, animation testing | SBT artist-guide/shot-production/animation.md, asset-creation/animation-testing.md | human | Shot workflow, rig testing |
| Add-on: anim_cupboard | SBT addons/anim_cupboard.md | human | Animator utilities |
| Manual: keyframes, actions, graph/dope sheet/NLA | MAN animation/{keyframes,actions.rst}, editors/{graph_editor,dope_sheet,nla} | human | Reference |
| Dev docs: layered/slotted actions, NLA | DEV features/animation/{animation_system (layered.md), nla.md} | internal | New Action data model |
| Source modules | SRC source/blender/{animrig, editors/animation, editors/space_action, editors/space_graph, editors/space_nla, blenkernel (anim/fcurve)} | internal | Action/F-curve evaluation |
| UI panels | bl_ui/{space_dopesheet.py, space_graph.py, space_nla.py, anim.py} | internal | Editor UIs |
| Pose library | SRC scripts/addons_core/pose_library | internal | Pose assets via Python |
| Release notes | RN animation_rigging.md | internal | Action API churn |

## S08 Simulation & FX
| Source | Path / URL | Lens | Why |
|---|---|---|---|
| Manual: Physics | MAN physics/{cloth,fluid,particles,rigid_body,soft_body,dynamic_paint,simulation_nodes.rst,baking.rst} | human | Every solver |
| Studio guide: effects | SBT artist-guide/shot-production/effects.md | human | FX and cache practice |
| 2019 shot-caching proposal | SBT archive/pipeline-proposal-2019/shot-caching | human | Cache pipeline design |
| Dev docs: XPBD | DEV features/nodes/{xpbd_simulation.md,xpbd_solver} | internal | Node-based physics future |
| Source modules | SRC source/blender/{simulation, editors/physics, blenkernel (cloth/fluid/particle/pointcache)}; intern/{mantaflow,rigidbody,openvdb} | internal | Solvers, caches |
| UI panels | bl_ui/properties_physics_*.py, properties_particle.py | internal | Physics settings → RNA |
| Release notes | RN physics.md | internal | Drift |

## S09 Lighting & rendering
| Source | Path / URL | Lens | Why |
|---|---|---|---|
| Studio guide: lighting | SBT artist-guide/shot-production/lighting.md | human | Lighting workflow |
| Lighting Overrider add-on | SBT addons/lighting_overrider.md | human | Per-shot overrides as JSON, agent-friendly |
| Project-tools: final render, playblast, review | SBT artist-guide/project_tools/{usage-final-render,usage-playblast,usage-render-review}.md | human | Render hand-off |
| Manual: Render | MAN render/{cycles,eevee,lights,cameras.rst,color_management,layers,output} | human | Engines and settings |
| Dev docs: Cycles, EEVEE, Workbench, pipeline | DEV features/{cycles,eevee,workbench,render_pipeline} | internal | Kernel scheduling, EEVEE design |
| Source modules | SRC intern/cycles; source/blender/{render, draw/engines/{eevee,workbench}, gpu, imbuf} | internal | Both engines |
| UI panels | bl_ui/{properties_render.py, properties_output.py, properties_data_light.py, properties_view_layer.py, properties_world.py} | internal | Render settings surface |
| Release notes | RN {cycles,eevee,rendering}.md | internal | Drift |

## S10 Compositing
| Source | Path / URL | Lens | Why |
|---|---|---|---|
| Manual: Compositing | MAN compositing/{types,compositor_system.rst,usage.rst} | human | Nodes and usage |
| Manual: tracking, masking | MAN movie_clip/{tracking,masking} | human | VFX inputs |
| Studio guide: coloring | SBT artist-guide/shot-production/coloring.md | human | Stub (4 lines) |
| Dev docs: compositor | DEV features/compositor/{realtime,glossary.md} | internal | GPU realtime compositor |
| Source modules | SRC source/blender/{compositor, nodes/composite, editors/space_clip, editors/mask}; intern/libmv | internal | Compositor, tracker |
| UI panels | bl_ui/{node_add_menu_compositor.py, space_clip.py} | internal | Node catalogue |
| Release notes | RN {compositor,motion_tracking}.md | internal | Drift |

## S11 Editing (VSE)
| Source | Path / URL | Lens | Why |
|---|---|---|---|
| Studio guide: editorial | SBT artist-guide/pre-production/editorial.md | human | Studio edit workflow |
| Project-tools: sync edit, import playblast | SBT artist-guide/project_tools/{usage-sync-edit,usage-import-playblast}.md | human | Edit ↔ shot round trip |
| Blender Kitsu add-on | SBT addons/blender_kitsu.md | human | VSE strips → Kitsu shots |
| Manual: video editing | MAN video_editing/{edit,setup,storyboarding}, editors/video_sequencer | human | Reference |
| Dev docs: sequencer | DEV features/sequencer/ | internal | Strip data model, cache, retiming |
| Source modules | SRC source/blender/{sequencer, editors/space_sequencer, imbuf, editors/sound} | internal | Implementation |
| UI panels | bl_ui/{space_sequencer.py, properties_strip.py, properties_strip_modifier.py} | internal | UI surface |
| Scripts: contactsheet, film-delivery, framegrid | SBT addons/contactsheet.md; studio/blender-studio-tools/scripts/{film-delivery,framegrid} | internal | Deliverable automation |

## S12 Grease Pencil 2D
| Source | Path / URL | Lens | Why |
|---|---|---|---|
| Manual: Grease Pencil | MAN grease_pencil/{modes,modifiers,materials,animation,visual_effects} | human | Full GP v3 reference |
| Studio guide: storyboard | SBT artist-guide/pre-production/storyboard.md | human | GP for boards |
| Add-ons: brushstroke_tools, grease_converter | SBT addons/brushstroke_tools.md; SBT media/addons/grease_converter | human | Stylised strokes (Project Gold) |
| Dev docs: GP architecture, line art | DEV features/grease_pencil/{architecture.md,line_art} | internal | GP v3 on curves |
| Source modules | SRC source/blender/{editors/grease_pencil, editors/gpencil_legacy, draw/engines/gpencil, shader_fx} | internal | Editing and draw |
| UI panels | bl_ui/{properties_data_grease_pencil.py, properties_grease_pencil_common.py, properties_material_gpencil.py} | internal | UI surface |
| GP Fundamentals (free) | https://studio.blender.org/training/grease-pencil-fundamentals/ | human | Free course |

## X1 Production pipeline & management
| Source | Path / URL | Lens | Why |
|---|---|---|---|
| Naming conventions | SBT naming-conventions/ | human | Explicit naming and folder grammar, agent-ready |
| Project-tools overview | SBT artist-guide/project_tools/{project-overview,project-blender}.md | human | Per-project deployment |
| TD guide | SBT td-guide/ (kitsu_server, flamenco_setup, svn-setup, syncthing, folder_structure_*) | human | Full studio infrastructure |
| Kitsu guide and add-on | SBT artist-guide/kitsu.md, addons/blender_kitsu.md | human | Task tracking |
| Flamenco | studio/flamenco (internal/manager/job_compilers/scripts/*.js, addon/flamenco) | internal | Declarative JS job types |
| Watchtower | studio/watchtower/docs | internal | Production state via Kitsu API |
| Batch scripts | studio/blender-studio-tools/scripts/{project-tools,bbatch,shotstats,kitsu-uploader,pipeline-release} | internal | Headless pipeline automation |
| blender-studio site source | studio/blender-studio/{docs,training,projects} | internal | Catalogue data model |
| Design principles | SBT overview/design-principles.md | human | Pipeline philosophy |

## X2 Python, add-ons & extensions
| Source | Path / URL | Lens | Why |
|---|---|---|---|
| Blender Lab MCP | lab/blender_mcp/{mcp/blmcp/tools, addon, readme_tools.rst} | internal | Official agent baseline: 26 tools + system prompt |
| Manual: Advanced | MAN advanced/{scripting,command_line,extensions,operators.rst,app_templates.rst} | human | Scripting, headless, packaging |
| Dev handbook: extensions | DEV handbook/extensions, features/extensions/{schema,api_listing} | internal | Manifest and rules |
| Python operators, modules | SRC scripts/{startup/bl_operators, modules/bpy_extras, addons_core} | internal | Readable reference operators |
| Python bindings | SRC source/blender/python | internal | bpy internals, context limits |
| API doc generator, tests | SRC doc/python_api, tests/python | internal | Pinned API, runnable examples |
| Studio add-ons source | studio/blender-studio-tools/scripts-blender/addons/ (11) | internal | Production add-on code |
| TD guide: python, extensions | SBT td-guide/{python,extensions_setup}.md | human | Add-on distribution |
| Release notes | RN python_api.md | internal | API breakage |
| Scripting for Artists (free) | https://studio.blender.org/training/scripting-for-artists/ | human | Free course |

## X3 Core architecture
| Source | Path / URL | Lens | Why |
|---|---|---|---|
| Dev docs: core | DEV features/core/{dna.md,rna.md,depsgraph.md,undo.md,context.md,datablocks,implicit_sharing.md} | internal | What "state" means |
| Dev docs: interface internals, HIG | DEV features/interface/{operators.md,screen.md,human_interface_guidelines} | internal | Operator lifecycle and UI rules |
| Dev docs: project system | DEV features/project_system/ | internal | Upcoming Blender Projects |
| Source modules | SRC source/blender/{makesdna, makesrna, depsgraph, windowmanager, blenkernel, blenloader, editors/undo, editors/interface} | internal | Core layers |
| Keymaps | SRC scripts/presets/keyconfig | internal | Gesture → operator map |
| Manual: Interface | MAN interface/ | human | The UI substrate |
| Dev handbook | DEV handbook/{guidelines,design,building_blender} | internal | Conventions, design process |
| Release notes | RN core.md, user_interface.md | internal | Drift |

## Gaps in local coverage
- **Studio stubs** (4–5 lines): layout, rendering, coloring, previz, 2D assets; `usage-build-shot.md` is one line. The human lens is weak for S06, S09, S10 and S12.
- **S02 UV:** no Studio page and no dev-docs feature page. It rests on the manual and source.
- **S10 Compositing:** dev docs cover only realtime and a glossary; no Studio workflow.
- **S08 Simulation:** dev docs only for the XPBD proposals; no mantaflow, cloth or point-cache internals.
- **S11 VSE:** no Studio artist page for in-Blender editing; no free training.
- **Flamenco:** only two example job scripts are local.
- **Video training:** nothing local. Free courses include Fundamentals 4.5/2.8, Rigging Tools, GP Fundamentals and Scripting for Artists (partly); most others are [sub]. ("Realistic Character" is a 404; see Inventory B.)
- **Not inspected:** `SBT media/`, `lab/blender_mcp/mcp/blmcp/data`.
