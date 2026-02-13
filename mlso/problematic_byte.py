def find_problematic_bytes(filepath):
    """Find and print positions and context of problematic bytes."""
    with open(filepath, 'rb') as file:
        content = file.read()

    # Attempt to decode and catch errors
    index = 0
    while index < len(content):
        try:
            # Try to decode a single character
            char = content[index:index+1].decode('utf-8')
            index += 1
        except UnicodeDecodeError as e:
            # Print the problematic byte and its position
            print(f"Problematic byte: {content[index:index+1]} at position {index}")
            # Print surrounding context
            context_range = 10
            start = max(0, index - context_range)
            end = min(len(content), index + context_range + 1)
            context = content[start:end]
            print(f"Context: {context}")
            # Move past the problematic byte
            index += 1
