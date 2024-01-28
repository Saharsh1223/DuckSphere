def remove_elements_with_even_index(input_list):
    return [element for index, element in enumerate(input_list) if index % 2 != 0]

# Example usage:
original_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
filtered_list = remove_elements_with_even_index(original_list)

print("Original List:", original_list)
print("Filtered List (odd indices only):", filtered_list)