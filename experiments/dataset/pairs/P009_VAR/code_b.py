def calculate_total_sum(numbers_list):
    running_total = 0
    for num in numbers_list:
        running_total += num
    return running_total

def sum_elements(arr):
    return calculate_total_sum(arr)
