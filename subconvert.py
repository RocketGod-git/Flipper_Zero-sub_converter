import os
import numpy as np
import argparse

SIGNAL_FILE_EXTENSIONS_BY_TYPE = {
    np.int8: ".complex16s",
    np.uint8: ".complex16u",
    np.int16: ".complex32s",
    np.uint16: ".complex32u",
    np.float32: ".complex",
    np.complex64: ".complex",
}

def read_sub_file(filename):
    with open(filename, "r") as file:
        lines = file.readlines()

    frequency = None
    preset = None
    raw_data = []

    for line in lines:
        if line.startswith("Frequency:"):
            frequency = int(line.split(":")[1].strip())
        elif line.startswith("Preset:"):
            preset = line.split(":")[1].strip()
        elif line.startswith("RAW_Data:"):
            raw_data.extend(map(int, line.split(":")[1].strip().split()))

    return frequency, preset, raw_data

def convert_sub_to_signal_file(input_file, output_file, dtype, file_extension=None):
    frequency, preset, raw_data = read_sub_file(input_file)

    if dtype not in SIGNAL_FILE_EXTENSIONS_BY_TYPE:
        raise ValueError(f"Unsupported data type: {dtype}")

    if file_extension is None:
        file_extension = SIGNAL_FILE_EXTENSIONS_BY_TYPE[dtype]

    output_path = os.path.splitext(output_file)[0] + file_extension

    data = np.array(raw_data, dtype=dtype)
    data.tofile(output_path)

    print(f"Converted {input_file} to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a .sub file to a specified signal file format."
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the input .sub file",
    )
    parser.add_argument(
        "output_file",
        type=str,
        help="Path to the output file (without file extension)",
    )
    parser.add_argument(
        "dtype",
        type=np.dtype,
        choices=SIGNAL_FILE_EXTENSIONS_BY_TYPE.keys(),
        help="Data type for the output file",
    )
    parser.add_argument(
        "--file-extension",
        type=str,
        choices=SIGNAL_FILE_EXTENSIONS_BY_TYPE.values(),
        help="File extension for the output file (optional)",
    )

    args = parser.parse_args()

    try:
        convert_sub_to_signal_file(
            args.input_file,
            args.output_file,
            args.dtype,
            file_extension=args.file_extension,
        )
    except (OSError, ValueError) as e:
        print(f"Error: {e}")
        exit(1)