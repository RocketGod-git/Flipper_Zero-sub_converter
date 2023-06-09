import os
import numpy as np
import argparse
import re

SIGNAL_FILE_EXTENSIONS_BY_TYPE = {
    "int8": (np.int8, ".complex16s"),
    "uint8": (np.uint8, ".complex16u"),
    "int16": (np.int16, ".complex32s"),
    "uint16": (np.uint16, ".complex32u"),
    "float32": (np.float32, ".complex"),
    "complex64": (np.complex64, ".complex"),
}

def decode_manchester(raw_data):
    if len(raw_data) < 2 or len(raw_data) % 2 != 0:
        raise ValueError("Invalid Manchester encoding: length of raw data must be even and contain at least two bits.")

    decoded_data = []

    for i in range(0, len(raw_data), 2):
        if raw_data[i] == 1 and raw_data[i + 1] == 0:
            decoded_data.append(0)
        elif raw_data[i] == 0 and raw_data[i + 1] == 1:
            decoded_data.append(1)
        else:
            raise ValueError(f"Invalid Manchester encoding in raw data at position {i}")

    return decoded_data

def hex_to_binary(hex_string):
    return [int(b) for b in ''.join(format(int(byte, 16), '08b') for byte in hex_string.split())]

def hex_to_ook(hex_string):
    binary_data = hex_to_binary(hex_string)
    ook_data = []

    for bit in binary_data:
        if bit == 1:
            ook_data.extend([1, 0])
        else:
            ook_data.extend([0, 1])

    return ook_data

def read_sub_file(input_file):
    with open(input_file, 'r') as f:
        content = f.readlines()

    content = [line.strip() for line in content]

    frequency = None
    for line in content:
        if line.startswith('Frequency:'):
            frequency = int(line.split(':')[1].strip()) // 1000
            break

    preset = None
    for line in content:
        if line.startswith('Preset:'):
            preset = line.split(':')[1].strip()
            break

    raw_data = []
    key = None
    for line in content:
        if line.startswith('RAW_Data:'):
            raw_data = list(map(int, line.split(':')[1].strip().split()))
            break
        elif line.startswith('Key:'):
            key = line.split(':')[1].strip().replace(' ', '')
            raw_data = hex_to_ook(key)
            break

    sample_rate = None
    for line in content:
        if line.startswith('TE:'):
            sample_rate = int(line.split(':')[1].strip())
            break

    center_frequency = None
    for line in content:
        if line.startswith('CenterFrequency:'):
            center_frequency = int(line.split(':')[1].strip())
            break

    protocol = None
    for line in content:
        if line.startswith('Protocol:'):
            protocol = line.split(':')[1].strip()
            break

    if raw_data and frequency and preset:
        if protocol == "Manchester":
            decoded_data = decode_manchester(raw_data)
        else:
            decoded_data = raw_data

        return frequency, preset, decoded_data, sample_rate, center_frequency
    else:
        raise ValueError(f'Invalid .sub file format: {input_file}')

def convert_sub_to_signal_file(input_path, output_path, output_format):
    frequency, preset, raw_data, sample_rate, center_frequency = read_sub_file(input_path)

    complex_data = convert_sub_to_signal(raw_data, output_format)
    write_signal_file(output_path, complex_data, output_format)
    print(f"Converted {input_path} to {output_path}")

    # Write accompanying .txt file
    write_accompanying_txt_file(output_path, frequency, sample_rate)

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
    center_frequency = frequency
    
    with open(txt_filename, "w") as file:
        file.write(f"sample_rate={sample_rate}\n")
        file.write(f"center_frequency={center_frequency}\n")

    print(f"Created accompanying .txt file: {txt_filename}")

def write_signal_file(output_path, data, output_format):
    dtype, extension = SIGNAL_FILE_EXTENSIONS_BY_TYPE[output_format]
    output_path_with_extension = output_path + extension

    with open(output_path_with_extension, 'wb') as f:
        data.tofile(f)

    print(f"Saved data to {output_path_with_extension}")

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
        args.dtype
    )

        _, _, _, sample_rate, center_frequency = read_sub_file(args.input_file)

    except (OSError, ValueError) as e:
        print(f"Error: {e}")
        exit(1)