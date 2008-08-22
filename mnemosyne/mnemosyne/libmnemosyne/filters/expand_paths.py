# TODO


def f():    

    """Fill out relative paths for src tags (e.g. img src or sound src)."""
    
    i = new_s.lower().find("src")
    while i != -1:
        start = new_s.find("\"", i)
        end = new_s.find("\"", start+1)
        if end == -1:
            break
        old_path = new_s[start+1:end]
        new_s = new_s[:start+1] + expand_path(old_path) + new_s[end:]
        # Since new_s is always longer now, we can start searching
        # from the previous end tag.
        i = new_s.lower().find("src", end+1)
    return new_s
