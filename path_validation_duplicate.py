"""
NOTE: This module was copied over from DinoSlide because of annoying python module issues :))))))
Module for validation different file and directory paths used by DinoSlide.
Functions based on the principle of cascading 'ValidationResult's.
"""

import os
import re

mag_dir_pattern = re.compile(r"^\d+x$")  # Pattern that magnification scale directories need to match


class ValidationResult:
    """
    Class for returning validation results while also giving the option to add a
    message explaining the failure.
    """

    is_valid: bool
    failure_message: str

    def __init__(self, is_valid: bool, failure_message: str):
        self.is_valid = is_valid
        self.failure_message = failure_message


def contains_only_directories(path: str) -> bool:
    if os.path.isdir(path):
        try:
            for entry in os.listdir(path):
                if not os.path.isdir(os.path.join(path, entry)):
                    return False
            return True
        except PermissionError:
            print(f"Permission to {path} denied")
    return False


def contains_only_files_of_type(path: str, type: str) -> bool:
    """
    Check if the directory at the given path contains only files of the given file type.
    (e.g. type=".svs")
    """
    if os.path.isdir(path):
        try:
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                if not os.path.isfile(full_path) or not full_path.endswith(type):
                    return False
            return True
        except PermissionError:
            print(f"Permission to {path} denied")
    return False


# ------WSI DIRECTORY VALIDATION------
def validate_dir_for_patchify(path: str) -> ValidationResult:
    """
    Checks if the given path is to a directory of the proper layout
    for the patchify process (specified in the readme).
    """

    if not os.path.isdir(path):
        return ValidationResult(False, f"{path} is not a directory")

    # Directory must either be called WSI or contain a subdirectory called WSI
    if not os.path.basename(path) == "WSI":
        contains_wsi = False
        try:
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path) and entry == "WSI":
                    contains_wsi = True
                    path = os.path.join(path, "WSI")
                    break
        except PermissionError:
            return ValidationResult(False, f"Permission to {path} denied")
        if not contains_wsi:
            return ValidationResult(False, f"{path} is not 'WSI' and does not contain 'WSI' subdirectory")

    if not contains_only_directories(path):
        return ValidationResult(False, f"{path} should only contain site directories")

    # Check site directories
    for directory in os.listdir(path):
        dir_path = os.path.join(path, directory)
        validate_result = validate_wsi_site_directory(dir_path)
        if not validate_result.is_valid:
            return validate_result
    return ValidationResult(True, "Valid!")


def validate_wsi_site_directory(path: str) -> ValidationResult:
    """
    Checks if the given path is to a body site directory of the proper layout
    for the patchify process (specified in the readme).
    """

    if not contains_only_directories(path):
        return ValidationResult(False, f"{path} should only contain diagnosis directories")

    # Check diagnosis directories
    for directory in os.listdir(path):
        dir_path = os.path.join(path, directory)
        validate_result = validate_wsi_diagnosis_directory(dir_path)
        if not validate_result.is_valid:
            return validate_result
    return ValidationResult(True, "Valid!")


def validate_wsi_diagnosis_directory(path: str) -> ValidationResult:
    """
    Checks if the given path is to a diagnosis directory of the proper layout
    for the patchify process (specified in the readme).
    """

    if not contains_only_directories(path):
        return ValidationResult(False, f"{path} should only contain magnification scale directories")

    # Check magnification scale directories
    for directory in os.listdir(path):
        dir_path = os.path.join(path, directory)
        validate_result = validate_wsi_mag_directory(dir_path)
        if not validate_result.is_valid:
            return validate_result
    return ValidationResult(True, "Valid!")


def validate_wsi_mag_directory(path: str) -> ValidationResult:
    """
    Checks if the given path is to a magnification scale directory of the proper layout
    for the patchify process (specified in the readme).
    """

    if not mag_dir_pattern.match(os.path.basename(path)):
        return ValidationResult(False, f"{path} should be a mag directory of the pattern '<scale>x'")

    if not contains_only_files_of_type(path, ".svs"):
        return ValidationResult(False, f"{path} should only contain files ending in '.svs'")

    return ValidationResult(True, "Valid!")
