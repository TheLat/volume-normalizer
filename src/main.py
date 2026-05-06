import array
import os
import ffmpeg
import sys
from pydub import AudioSegment
from pydub.utils import get_array_type
import subprocess
import time

def get_file_average_volume(filename):
    sound = AudioSegment.from_file(file=filename)
    bit_depth = sound.sample_width * 8
    array_type = get_array_type(bit_depth)
    raw = array.array(array_type, sound._data)
    total = 0
    count = 0
    data = [abs(r) for r in raw]
    data.sort()
    data = data[int(len(data)*0.8):]
    total = sum(data)
    count = len(data)
    return total/count

def parse_and_normalize(in_path, out_path):
    in_files = [f for f in os.listdir(in_path) if os.path.isfile(os.path.join(in_path, f))]
    volumes = {}
    peak = 0
    p = {}
    count = 0
    start = time.time()
    print("Analyzing...", end='', flush=True)
    for f in in_files:
        count = count + 1
        p[f] = subprocess.Popen(["python3", "src/swarmer.py", os.path.join(in_path, f)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        if (count % os.cpu_count() == 0):
            for k in p.keys():
                data = float(p[k].communicate()[0])
                volumes[k] = data
                peak = max(peak, data)
            p = {}
    for k in p.keys():
        data = float(p[k].communicate()[0])
        volumes[k] = data
        peak = max(peak, data)
    p = []
    print(" Done! (%s seconds)" % int(time.time() - start), flush=True)

    print("Normalizing...", end='', flush=True)

    for f in in_files:
        if volumes[f] == 0.0:
            volumes[f] = 1.0

        probe = ffmpeg.probe(os.path.join(in_path, f))
        has_art = any(s['codec_type'] == 'video' for s in probe['streams'])
        i = ffmpeg.input(os.path.join(in_path, f))
        a = i['a'].filter('volume', float(peak/volumes[f]))
        streams = [a, i['v']] if has_art else [a]

        p.append(ffmpeg.output(*streams, os.path.join(out_path, f), vcodec="copy", id3v2_version=3, write_xing=1).run_async(pipe_stdin=True, quiet=True))
        if len(p) % os.cpu_count() == 0:
            for i in range(len(p)):
                p[i].wait()
    for i in range(len(p)):
        p[i].wait()

    print(" Done! (%s seconds)" % int(time.time() - start), flush=True)
    print("Done!", flush=True)

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
