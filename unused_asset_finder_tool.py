import unreal
import datetime

# create recovery folder 
RECOVERY_FOLDER = "/Game/_RecoveredAssets"

# this function finds any unused assets in the project
def find_unused_assets():
    """Find and optionally move unused assets."""

    # check if the recovery folder exists and  if not make one
    if not unreal.EditorAssetLibrary.does_directory_exist(RECOVERY_FOLDER):
        unreal.EditorAssetLibrary.make_directory(RECOVERY_FOLDER)

    # get the asset registry (this stores info about all assets in the project)
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()

    # get every asset in the Game folder (recursive means it checks subfolders too)
    all_assets = asset_registry.get_assets_by_path("/Game", recursive=True)

    # make an empty list to store unused assets
    unused_assets = []

    # go through every asset in the project
    for asset_data in all_assets:
        asset_path = asset_data.object_path.string
        referencers = asset_registry.get_referencers(asset_data.package_name, recursive=True)

        # if something is using the asset skip past it
        if referencers:
            continue

        # if the asset is loaded in a level, skip it
        if unreal.EditorAssetLibrary.is_asset_loaded(asset_path):
            continue

        # otherwise, add it to the unused list
        unused_assets.append(asset_data)

    # print out how many unused assets were found
    unreal.log(f"Found {len(unused_assets)} unused assets.")
    for asset in unused_assets:
        unreal.log(f"- {asset.object_path}")

    # ask the user if they want to move the assets
    response = unreal.EditorDialog.show_message(
        "Unused Assets Found",
        f"{len(unused_assets)} unused assets found. Move them to a recovery folder?",
        unreal.AppMsgType.YES_NO
    )

    # if they click YES, move the unused assets to the recovery folder
    if response == unreal.AppReturnType.YES:
        for asset_data in unused_assets:
            src_path = asset_data.object_path.string
            asset_name = asset_data.asset_name
            dest_path = f"{RECOVERY_FOLDER}/{asset_name}"

            # if an asset with the same name already exists, add a timestamp
            if unreal.EditorAssetLibrary.does_asset_exist(dest_path):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                dest_path = f"{RECOVERY_FOLDER}/{asset_name}_{timestamp}"

            # move the asset
            result = unreal.EditorAssetLibrary.rename_asset(src_path, dest_path)

            if result:
                unreal.log(f"Moved: {src_path} -> {dest_path}")
            else:
                unreal.log_warning(f"Failed to move: {src_path}")
    else:
        unreal.log("User declined to move unused assets.")


# this function adds the tool to Unreal’s Tools menu
def register_tool():
    """Register the Find Unused Assets tool in Unreal's menu."""
    menus = unreal.ToolMenus.get()
    tools_menu = menus.find_menu("LevelEditor.MainMenu.Tools")

    if not tools_menu:
        unreal.log_error("Could not find Tools menu to register entry.")
        return

    # make a new menu entry (button)
    entry = unreal.ToolMenuEntry(
        name="PythonTools_FindUnusedAssets",
        type=unreal.MultiBlockType.MENU_ENTRY
    )

    entry.set_label("Find Unused Assets")
    entry.set_tool_tip("Scan and move unused assets to a recovery folder.")
    
    # this tells Unreal what to run when the button is clicked
    entry.set_string_command(
        type=unreal.ToolMenuStringCommandType.PYTHON,
        custom_type="",
        command_string="import unused_assets_tool; unused_assets_tool.find_unused_assets()"
    )

    # add it to the Tools menu under Python Tools
    tools_menu.add_menu_entry("PythonTools", entry)
    menus.refresh_all_widgets()

    unreal.log("Registered 'Find Unused Assets' under Tools → Python Tools")


# automatically register the tool in unreal
register_tool()








