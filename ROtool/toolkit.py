# Made by Vortex
#ROtool 2.0
# toolkit.py — Roblox multi tool unblacklister
# Usage: python toolkit.py --mode [add|regenerate|unblacklist|full]

import os
import uuid
import random
import time
import argparse
from lxml import etree

MAPS_FOLDER = r""

INVALID_PARENTS = {
    "PackageLink", "BinaryString", "FloatCurve", "NumberSequence",
    "ColorSequence", "SharedTable", "SoundService", "Chat", "TextChatService",
    "VoiceChatService", "LocalizationService", "TestService", "VRService",
    "Players", "Lighting", "MaterialService"
}

BLACKLISTED_PROPERTY_NAMES = {
    "archivable", "SourceAssetId", "LinkedSourceAssetId", "IsPublicDomain", "AssetId"
}

BLACKLISTED_CLASS_NAMES = {
    "MeshPartOperation", "UnionOperation", "ScriptContext", "SolidModel"
}

def generate_unique_id():
    return str(uuid.uuid4())

def log(msg):
    print(f" - {msg}")

def remove_existing_unique_ids(item):
    removed = 0
    for child in list(item.findall("Item")):
        if child.attrib.get("class") == "StringValue":
            props = child.find("Properties")
            if props is not None:
                name = props.find("string[@name='Name']")
                if name is not None and name.text == "UniqueID":
                    item.remove(child)
                    removed += 1
    return removed

def add_unique_id(item):
    uid = generate_unique_id()
    string_item = etree.Element("Item", {"class": "StringValue"})
    props = etree.SubElement(string_item, "Properties")
    etree.SubElement(props, "string", {"name": "Name"}).text = "UniqueID"
    etree.SubElement(props, "string", {"name": "Value"}).text = uid
    item.append(string_item)
    return uid

def is_valid_parent(item):
    return item.attrib.get("class") not in INVALID_PARENTS

def rename_item(item):
    props = item.find("Properties")
    if props is not None:
        name_elem = props.find("string[@name='Name']")
        if name_elem is not None:
            name_elem.text = f"Obf_{uuid.uuid4().hex[:8]}"

def remove_blacklisted_properties(root):
    count = 0
    for properties in root.xpath(".//Properties"):
        for child in list(properties):
            if child.attrib.get("name", "") in BLACKLISTED_PROPERTY_NAMES:
                properties.remove(child)
                count += 1
    return count

def remove_blacklisted_classes(element):
    count = 0
    for child in list(element):
        if child.tag == "Item" and child.attrib.get("class", "") in BLACKLISTED_CLASS_NAMES:
            element.remove(child)
            count += 1
        else:
            count += remove_blacklisted_classes(child)
    return count

def shuffle_items(root):
    items = [child for child in root if child.tag == "Item"]
    random.shuffle(items)
    for child in items:
        root.remove(child)
    for child in items:
        root.append(child)

def add_metadata(root):
    metadata_item = etree.Element("Item", attrib={"class": "StringValue"})
    props = etree.SubElement(metadata_item, "Properties")
    etree.SubElement(props, "string", {"name": "Name"}).text = "RandomID"
    etree.SubElement(props, "string", {"name": "Value"}).text = generate_unique_id()
    root.append(metadata_item)

def add_decoy_part(root):
    part = etree.Element("Item", attrib={"class": "Part"})
    props = etree.SubElement(part, "Properties")
    etree.SubElement(props, "string", {"name": "Name"}).text = f"Decoy_{uuid.uuid4().hex[:6]}"
    etree.SubElement(props, "bool", {"name": "Anchored"}).text = "true"
    etree.SubElement(props, "bool", {"name": "CanCollide"}).text = "false"
    etree.SubElement(props, "Vector3", {"name": "Size"}).text = "0.1,0.1,0.1"
    etree.SubElement(props, "Color3uint8", {"name": "Color"}).text = "0,0,0"
    etree.SubElement(props, "float", {"name": "Transparency"}).text = "1"
    root.append(part)

def process_items(root, mode):
    all_items = []
    stack = [root]
    while stack:
        item = stack.pop()
        all_items.append(item)
        stack.extend(item.findall("Item"))

    ids_added = ids_removed = renamed = 0

    for item in all_items:
        if not is_valid_parent(item):
            continue

        removed = remove_existing_unique_ids(item)
        ids_removed += removed

        if mode in {"add", "regenerate", "unblacklist", "full"}:
            add_unique_id(item)
            ids_added += 1

        if mode in {"full"}:
            rename_item(item)
            renamed += 1

    return ids_added, ids_removed, renamed

def process_file(filepath, mode):
    print(f"\n📂 Processing: {os.path.basename(filepath)}")
    parser = etree.XMLParser(recover=True)

    try:
        tree = etree.parse(filepath, parser)
    except Exception as e:
        print(f"❌ Error parsing: {e}")
        return

    root = tree.getroot()
    start = time.time()

    removed_props = removed_classes = renamed = 0

    if mode in {"unblacklist", "full"}:
        removed_props = remove_blacklisted_properties(root)
        removed_classes = remove_blacklisted_classes(root)

    ids_added, ids_removed, renamed = process_items(root, mode)

    if mode in {"unblacklist", "full"}:
        add_metadata(root)
        add_decoy_part(root)
        shuffle_items(root)

    filename_out = filepath.replace(".rbxlx", f"_{mode}.rbxlx")
    tree.write(filename_out, encoding="utf-8", xml_declaration=True)

    print("✅ Completed:")
    print(f"   - {ids_removed} UniqueIDs removed")
    print(f"   - {ids_added} UniqueIDs added")
    if mode in {"full"}:
        print(f"   - {renamed} objects renamed")
    if mode in {"unblacklist", "full"}:
        print(f"   - {removed_props} properties removed")
        print(f"   - {removed_classes} class instances removed")
    print(f"📄 Output saved: {filename_out}")
    print(f"⏱ Time: {int(time.time() - start)}s")

def main():
    parser = argparse.ArgumentParser(description="Roblox Game Toolkit")
    parser.add_argument("--mode", required=True, choices=["add", "regenerate", "unblacklist", "full"],
                        help="Operation mode")
    args = parser.parse_args()

    for filename in os.listdir(MAPS_FOLDER):
        if filename.endswith(".rbxlx"):
            process_file(os.path.join(MAPS_FOLDER, filename), args.mode)

    print("\n🚀 All done.")

if __name__ == "__main__":
    main()
