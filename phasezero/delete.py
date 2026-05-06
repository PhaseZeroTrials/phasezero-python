import phasezero.core as core


def delete_file_main(args):
    session = args.session
    project_id = args.project_id
    relative_path = args.relative_path
    recursive = getattr(args, 'recursive', False)
    skip_confirm = getattr(args, 'yes', False)

    if recursive:
        _delete_folder(session, project_id, relative_path, skip_confirm=skip_confirm)
        return

    try:
        result = core.delete_file(session, project_id, relative_path)
        print(f"File '{relative_path}' has been successfully deleted.")
        print(result)
    except Exception as e:
        print(f"Error deleting file: {str(e)}")


def _delete_folder(session, project_id, folder_path, skip_confirm=False):
    tenant_id = session.get_tenant_id()
    root_prefix = f"{tenant_id}/{project_id}/".replace("//", "/")

    print(f"Listing files under '{folder_path}'...")
    try:
        files = _collect_files(session, project_id, folder_path, root_prefix)
    except Exception as e:
        print(f"Error listing files under '{folder_path}': {str(e)}")
        return

    if not files:
        print(f"No files found under '{folder_path}'.")
        return

    print(f"Found {len(files)} file(s) under '{folder_path}':")
    for f in files:
        print(f"  {f}")

    if not skip_confirm:
        confirm = input(f"\nDelete all {len(files)} file(s)? Type 'yes' to confirm: ").strip().lower()
        if confirm != 'yes':
            print("Aborted. No files were deleted.")
            return

    deleted = 0
    failed = 0
    for f in files:
        try:
            core.delete_file(session, project_id, f)
            print(f"Deleted: {f}")
            deleted += 1
        except Exception as e:
            print(f"Error deleting '{f}': {str(e)}")
            failed += 1

    print(f"\nDone. Deleted: {deleted}, Failed: {failed}")


def _collect_files(session, project_id, folder_path, root_prefix, _seen=None):
    if _seen is None:
        _seen = set()

    normalized = folder_path.rstrip('/')
    if normalized in _seen:
        return []
    _seen.add(normalized)

    result = core.list_files(session, project_id, folder_path)
    s3_objects = result.get('s3Objects', []) or []
    common_prefixes = result.get('commonPrefixes', []) or []

    files = []
    for obj in s3_objects:
        key = obj['key']
        files.append(key.replace(root_prefix, ''))

    for folder in common_prefixes:
        sub_path = folder.replace(root_prefix, '')
        if sub_path.rstrip('/') == normalized:
            continue
        files.extend(_collect_files(session, project_id, sub_path, root_prefix, _seen))

    return files
