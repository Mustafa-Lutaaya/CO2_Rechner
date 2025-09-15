def merge_category_docs(source_doc, dest_doc):
    existing_items = {item["name"]: item for item in dest_doc.get("items", [])}
    for item in source_doc.get("items", []):
        name = item["name"]
        if name in existing_items:
            existing_items[name]["count"] += item.get("count", 0)
            existing_items[name]["co2"] += item.get("co2", 0)
        else:
            existing_items[name] = item 
    return list(existing_items.values())

def sync_collection(source_collection, dest_collection):
    for source_doc in source_collection.find({}):
        category = source_doc["category"]
        dest_doc = dest_collection.find_one({"category": category})

        if not dest_doc:
            dest_collection.insert_one(source_doc)
        else:
            merged_items = merge_category_docs(source_doc, dest_doc)
            dest_collection.update_one(
                {"category": category},
                {"$set": {"items": merged_items}}
            )
def sync_cloud_to_local(cloud_client, local_client):
    sync_collection(
        cloud_client["YoungCaritas"]["co2"],
        local_client["YoungCaritas"]["co2"]
    )

def sync_local_to_cloud(local_client, cloud_client):
    sync_collection(
        local_client["YoungCaritas"]["co2"],
        cloud_client["YoungCaritas"]["co2"]
    )
