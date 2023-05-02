import os
import numpy as np
import argparse

SIGNAL_FILE_EXTENSIONS_BY_TYPE = {
    "int8": (np.int8, ".complex16s"),
    "uint8": (np.uint8, ".complex16u"),
    "int16": (np.int16, ".complex32s"),
    "uint16": (np.uint16, ".complex32u"),
    "float32": (np.float32, ".complex"),
    "complex64": (np.complex64, ".complex"),
}

def read_sub_file(filename):
    # Check if the file has the .sub extension
    if not filename.lower().endswith(".sub"):
        raise ValueError(f"Invalid file extension: {filename}. Expected a .sub file.")

    with open(filename, "r") as file:
        lines = file.readlines()

    preset = None
    raw_data = []
    sample_rate = None
    center_frequency = None

    for line in lines:
        if line.startswith("Frequency:"):
            center_frequency = int(line.split(":")[1].strip())
        elif line.startswith("Preset:"):
            preset = line.split(":")[1].strip()
        elif line.startswith("RAW_Data:"):
            raw_data.extend(map(int, line.split(":")[1].strip().split()))
        elif line.startswith("Key:"):
            raw_data.extend(int(x, 16) for x in line.split(":")[1].strip().split())
        elif line.startswith("TE:"):
            sample_rate = int(line.split(":")[1].strip())

    if preset is None or sample_rate is None or center_frequency is None or not raw_data:
        raise ValueError(f"Invalid .sub file format: {filename}")

    return center_frequency, preset, raw_data, sample_rate, center_frequency

def convert_sub_to_signal_file(input_file, output_file, dtype, file_extension=None):
    frequency, preset, raw_data = read_sub_file(input_file)

    if dtype not in SIGNAL_FILE_EXTENSIONS_BY_TYPE:
        raise ValueError(f"Unsupported data type: {dtype}")

    np_dtype, default_file_extension = SIGNAL_FILE_EXTENSIONS_BY_TYPE[dtype]

    if file_extension is None:
        file_extension = default_file_extension

    output_path = os.path.splitext(output_file)[0] + file_extension

    data = convert_sub_to_signal(raw_data, dtype)
    data.tofile(output_path)

    print(f"Converted {input_file} to {output_path}")

def convert_sub_to_signal(raw_data, dtype):
    if dtype == "int8":
        return convert_sub_to_complex16s(raw_data)
    elif dtype == "uint8":
        return convert_sub_to_complex16u(raw_data)
    elif dtype == "int16":
        return convert_sub_to_complex32s(raw_data)
    elif dtype == "uint16":
        return convert_sub_to_complex32u(raw_data)
    elif dtype == "float32":
        return convert_sub_to_float(raw_data)
    elif dtype == "complex64":
        return convert_sub_to_complex(raw_data)
    else:
        raise ValueError(f"Unsupported data type: {dtype}")

def convert_sub_to_complex16s(raw_data):
    complex_data = np.array([complex(np.int8(value), 0) for value in raw_data], dtype=np.complex64)
    return complex_data

def convert_sub_to_complex16u(raw_data):
    complex_data = np.array([complex(np.uint8(value), 0) for value in raw_data], dtype=np.complex64)
    return complex_data

def convert_sub_to_complex32s(raw_data):
    complex_data = np.array([complex(np.int16(value), 0) for value in raw_data], dtype=np.complex64)
    return complex_data

def convert_sub_to_complex32u(raw_data):
    complex_data = np.array([complex(np.uint16(value), 0) for value in raw_data], dtype=np.complex64)
    return complex_data

def convert_sub_to_float(raw_data):
    float_data = np.array(raw_data, dtype=np.float32)
    return float_data

def convert_sub_to_complex(raw_data):
    if len(raw_data) % 2 != 0:
        raise ValueError("The length of raw data must be even to convert it to complex format.")

    complex_data = np.array([complex(raw_data[i], raw_data[i + 1]) for i in range(0, len(raw_data), 2)], dtype=np.complex64)
    return complex_data

def write_accompanying_txt_file(output_path, frequency, sample_rate=500000):
    txt_filename = os.path.splitext(output_path)[0] + ".txt"
    center_frequency = frequency * 1000

    with open(txt_filename, "w") as file:
        file.write(f"sample_rate={sample_rate}\n")
        file.write(f"center_frequency={center_frequency}\n")

    print(f"Created accompanying .txt file: {txt_filename}")

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
        type=str,
        choices=SIGNAL_FILE_EXTENSIONS_BY_TYPE.keys(),
        help="Data type for the output file",
    )
    parser.add_argument(
        "--file-extension",
        type=str,
        choices=[ext for _, ext in SIGNAL_FILE_EXTENSIONS_BY_TYPE.values()],
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
        _, _, _, sample_rate, center_frequency = read_sub_file(args.input_file)
        output_path = os.path.splitext(args.output_file)[0] + SIGNAL_FILE_EXTENSIONS_BY_TYPE[args.dtype][1]
        write_accompanying_txt_file(output_path, center_frequency, sample_rate)
    except (OSError, ValueError) as e:
        print(f"Error: {e}")
        exit(1)