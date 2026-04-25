"""Godot CLI: project, scene, export, tests. Replaces godot-mcp. Run where Godot is installed."""
import argparse

from cli._base import out, err, get_cwd


def add_parser(sp):
    p = sp.add_parser("godot", help="Godot project, scene, export, tests")
    sub = p.add_subparsers(dest="godot_cmd", required=True)

    # open-project
    o = sub.add_parser("open-project", help="Validate Godot project (project.godot exists)")
    o.add_argument("project_path")
    o.set_defaults(_run=_run_open_project)

    # run-scene
    rs = sub.add_parser("run-scene", help="Run scene (headless optional)")
    rs.add_argument("scene_path")
    rs.add_argument("--headless", type=lambda x: x.lower() in ("1", "true", "yes"), default=True)
    rs.add_argument("--project-path", default=None)
    rs.set_defaults(_run=_run_run_scene)

    # export-game
    e = sub.add_parser("export-game", help="Export game (preset + output path)")
    e.add_argument("preset")
    e.add_argument("output_path")
    e.add_argument("--project-path", default=None)
    e.set_defaults(_run=_run_export_game)

    # get-scene-tree
    g = sub.add_parser("get-scene-tree", help="Get scene node tree (placeholder)")
    g.add_argument("--project-path", default=None)
    g.set_defaults(_run=_run_get_scene_tree)

    # set-node-property
    s = sub.add_parser("set-node-property", help="Set node property (placeholder)")
    s.add_argument("node_path")
    s.add_argument("property")
    s.add_argument("value")
    s.add_argument("--project-path", default=None)
    s.set_defaults(_run=_run_set_node_property)

    # run-tests
    rt = sub.add_parser("run-tests", help="Run Godot unit tests")
    rt.add_argument("--test-path", default=None)
    rt.add_argument("--project-path", default=None)
    rt.set_defaults(_run=_run_run_tests)

    # take-screenshot
    ts = sub.add_parser("take-screenshot", help="Take screenshot (placeholder)")
    ts.add_argument("output_path")
    ts.add_argument("--project-path", default=None)
    ts.set_defaults(_run=_run_take_screenshot)

    # parse-script
    ps = sub.add_parser("parse-script", help="Parse GDScript (lines count)")
    ps.add_argument("script_path")
    ps.set_defaults(_run=_run_parse_script)


def _run_open_project(args):
    from mcp.local.godot_mcp.server import open_project
    return open_project(project_path=args.project_path)


def _run_run_scene(args):
    from mcp.local.godot_mcp.server import run_scene
    return run_scene(
        scene_path=args.scene_path,
        headless=args.headless,
        project_path=args.project_path or get_cwd(),
    )


def _run_export_game(args):
    from mcp.local.godot_mcp.server import export_game
    return export_game(
        preset=args.preset,
        output_path=args.output_path,
        project_path=args.project_path or get_cwd(),
    )


def _run_get_scene_tree(args):
    from mcp.local.godot_mcp.server import get_scene_tree
    return get_scene_tree(project_path=args.project_path or get_cwd())


def _run_set_node_property(args):
    from mcp.local.godot_mcp.server import set_node_property
    return set_node_property(
        node_path=args.node_path,
        property=args.property,
        value=args.value,
        project_path=args.project_path or get_cwd(),
    )


def _run_run_tests(args):
    from mcp.local.godot_mcp.server import run_tests
    return run_tests(test_path=args.test_path, project_path=args.project_path or get_cwd())


def _run_take_screenshot(args):
    from mcp.local.godot_mcp.server import take_screenshot
    return take_screenshot(
        output_path=args.output_path,
        project_path=args.project_path or get_cwd(),
    )


def _run_parse_script(args):
    from mcp.local.godot_mcp.server import parse_script
    return parse_script(script_path=args.script_path)


def run(args):
    if not hasattr(args, "_run"):
        err("godot: missing subcommand")
    return args._run(args)
