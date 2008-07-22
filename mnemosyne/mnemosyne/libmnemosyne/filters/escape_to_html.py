def f():
    
    # Escape literal < (unmatched tag) and new line from string.
    
    hanging = []
    open = 0
    pending = 0

    for i in range(len(s)):
        if s[i] == '<':
            if open != 0:
                hanging.append(pending)
                pending = i
                continue
            open += 1
            pending = i
        elif s[i] == '>':
            if open > 0:
                open -= 1

    if open != 0:
        hanging.append(pending)

    new_s = ""
    for i in range(len(s)):
        if s[i] == '\n':
            new_s += "<br>"
        elif i in hanging:
            new_s += "&lt;"
        else:
            new_s += s[i]
