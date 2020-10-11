from enum import Enum
from typing import List


class FileType(Enum):
    Other = 0,  # This is for other file types, e.g. PDF, ZIP etc.
    Small = 1,
    LittleSquare = 150,
    Thumbnail = 300,
    Medium = 624,
    MediumLarge = 768,
    Large = 1024,
    Original = 10000,


def get_fallback(wished: FileType, available: List[FileType]):
    """
    >>> get_fallback(FileType.Thumbnail, [FileType.LittleSquare, FileType.Thumbnail, FileType.Medium])
    <FileType.Thumbnail: (300,)>
    >>> get_fallback(FileType.Large, [FileType.Thumbnail, FileType.Medium, FileType.Large])
    <FileType.Large: (1024,)>
    >>> get_fallback(FileType.LittleSquare, [FileType.Small, FileType.LittleSquare, FileType.Original])
    <FileType.LittleSquare: (150,)>
    >>> get_fallback(FileType.Thumbnail, [FileType.Original])
    <FileType.Original: (10000,)>
    """

    if wished in available:
        return wished
    for file_type in FileType:
        if file_type.value >= wished.value and file_type.value in available:
            return file_type
    return available[0]
