import unicodedata


def count_full_width_and_half_width_characters(string: str) -> int:
    count: int = 0
    for char in string:
        if unicodedata.east_asian_width(char) in "WFA":
            count += 2
        else:
            count += 1

    return count
