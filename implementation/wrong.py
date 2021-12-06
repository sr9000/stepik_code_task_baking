from pre_definition.tag import wrong


@wrong
def repeat(h, w, table):
    for i in range(h + w - 1):
        print(*table[i % len(table)])
