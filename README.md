# Flipper_Zero-sub_converter
Python script to convert .sub files to other usable subghz files

First do:<br>
```pip install -r requirements.txt```

Then:

<pre><code>Convert a .sub file to a specified signal file format.

positional arguments:
  input_file            Path to the input .sub file
  output_file           Path to the output file (without file extension)
  {&lt;class 'numpy.int8'&gt;,&lt;class 'numpy.uint8'&gt;,&lt;class 'numpy.int16'&gt;,&lt;class 'numpy.uint16'&gt;,&lt;class 'numpy.float32'&gt;,&lt;class 'numpy.complex64'&gt;}
                        Data type for the output file

options:
  -h, --help            show this help message and exit
  --file-extension {.complex16s,.complex16u,.complex32s,.complex32u,.complex,.complex}
                        File extension for the output file (optional)
</code></pre>

![20221001_061501504_iOS](https://user-images.githubusercontent.com/57732082/235715064-31017bf2-7b16-401a-b894-83680b1aa135.jpg)
