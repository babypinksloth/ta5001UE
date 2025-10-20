import unreal
import os
import datetime

# --- SETTINGS ---
RECOVERY_FOLDER = "/Game/_RecoveredAssets"
MENU_NAME = "Python Tools"
TOOL_LABEL = "Find Unused Assets"
TOOL_TIP = "Scan the project and move unused assets to a recovery folder"


# -----------------------------------------------------
# Main Functionality
# -----------------------------------------------------
def find_unused_assets():
    # Ensure recovery folder exists
    if not unreal.EditorAssetLibrary.does_directory_exist(RECOVERY_FOLDER):
        unreal.EditorAssetLibrary.make_directory(RECOVERY_FOLDER)

    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    all_assets = asset_registry.get_assets_by_path("/Game", recursive=True)
    unused_assets = []

    for asset_data in all_assets:
        asset_path = asset_data.object_path.string
        referencers = asset_registry.get_referencers(asset_data.package_name, recursive=True)

        if referencers:
            continue
        if unreal.EditorAssetLibrary.is_asset_loaded(asset_path):
            continue
        unused_assets.append(asset_data)

    print(f"\nFound {len(unused_assets)} unused assets:")
    for asset in unused_assets:
        print(f"- {asset.object_path}")

    if not unused_assets:
        unreal.EditorDialog.show_message(
            "No Unused Assets Found",
            "All assets are referenced or in use.",
            unreal.AppMsgType.OK
        )
        return

    response = unreal.EditorDialog.show_message(
        "Unused Assets Found",
        f"{len(unused_assets)} unused assets found.\n"
        "Would you like to move them to a recovery folder?",
        unreal.AppMsgType.YES_NO
    )

    if response == unreal.AppReturnType.YES:
        for asset_data in unused_assets:
            src_path = asset_data.object_path.string
            asset_name = asset_data.asset_name
            dest_path = f"{RECOVERY_FOLDER}/{asset_name}"

            if unreal.EditorAssetLibrary.does_asset_exist(dest_path):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                dest_path = f"{RECOVERY_FOLDER}/{asset_name}_{timestamp}"

            result = unreal.EditorAssetLibrary.rename_asset(src_path, dest_path)

            if result:
                print(f"Moved: {src_path} -> {dest_path}")
            else:
                print(f"Failed to move: {src_path}")

        unreal.EditorAssetLibrary.fix_redirectors("/Game")
        unreal.EditorDialog.show_message(
            "Assets Moved",
            f"{len(unused_assets)} assets moved to {RECOVERY_FOLDER}",
            unreal.AppMsgType.OK
        )
    else:
        print("User declined to move unused assets.")


def register_tool():
    tool_menus = unreal.ToolMenus.get()
    menu = tool_menus.find_menu("LevelEditor.MainMenu.Tools")

    if not menu:
        print("Could not find 'Tools' menu to register the Python tool.")
        return

    entry = unreal.ToolMenuEntry(
        name="Python_FindUnusedAssets",
        type=unreal.MultiBlockType.MENU_ENTRY,
    )
    entry.set_label(TOOL_LABEL)
    entry.set_tool_tip(TOOL_TIP)
    entry.set_icon("EditorStyle", "ContentBrowser.AssetTreeFolderOpen")
    entry.set_string_command(
        type=unreal.ToolMenuStringCommandType.PYTHON,
        custom_type=unreal.Name("Execute"),  # ✅ FIXED LINE
        string="import unused_assets_tool; unused_assets_tool.find_unused_assets()"
    )

    menu.add_menu_entry(MENU_NAME, entry)
    tool_menus.refresh_all_widgets()
    print(f"✅ Registered '{TOOL_LABEL}' under Tools → {MENU_NAME}")


