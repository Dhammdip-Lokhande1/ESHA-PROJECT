def flatten(nested_list):
    stack = [iter(nested_list)]
    result = []
    while stack:
        for item in stack[-1]:
            if isinstance(item, list):
                stack.append(iter(item))
                break
            else:
                result.append(item)
        else:
            stack.pop()
    return result
