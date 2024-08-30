import array
import os
import ffmpeg
import sys
from pydub import AudioSegment
from pydub.utils import get_array_type

def get_file_average_volume(filename):
    sound = AudioSegment.from_file(file=filename)
    bit_depth = sound.sample_width * 8
    array_type = get_array_type(bit_depth)
    raw = array.array(array_type, sound._data)
    total = 0
    count = 0
    data = [abs(r) for r in raw]
    data.sort()
    data = data[int(len(data)*0.1):]
    for d in data:
        total += d
        count += 1
    return total/count

def parse_and_normalize(in_path, out_path):
    in_files = [f for f in os.listdir(in_path) if os.path.isfile(os.path.join(in_path, f))]
    volumes = {}
    count = 0
    total = 0
    for f in in_files:
        print("Analyzing %s." % os.path.join(in_path, f))
        volumes[f] = get_file_average_volume(os.path.join(in_path, f))
        count += 1
        total += volumes[f]
    average = total/count
    for f in in_files:
        ffmpeg.input(os.path.join(in_path, f)).filter('volume', float(average/volumes[f])).output(os.path.join(out_path, f)).run()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise Exception("Invalid input.  Script only takes input directory and output directory");
    if not os.path.isdir(sys.argv[1]):
        raise Exception("Invalid input.  First parameter must be a directory.")
    if not os.path.isdir(sys.argv[2]):
        raise Exception("Invalid input.  Second parameter must be a directory.")
    in_files = [f for f in os.listdir(sys.argv[1]) if os.path.isfile(os.path.join(sys.argv[1], f))]
    out_files = [f for f in os.listdir(sys.argv[2]) if os.path.isfile(os.path.join(sys.argv[2], f))]
    for file in out_files:
        if file in in_files:
            raise Exception("Error:  File %s in output directory shares name with file in input directory and would be overwritten." % file)
    parse_and_normalize(sys.argv[1], sys.argv[2])
