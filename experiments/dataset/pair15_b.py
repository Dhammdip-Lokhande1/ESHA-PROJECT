def get_maximum(numbers):
    if not numbers: return None
    highest = numbers[0]
    for n in numbers:
        if n > highest:
            highest = n
    return highest