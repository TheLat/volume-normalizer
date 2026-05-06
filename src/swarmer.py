import sys
import array
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
    data = data[int(len(data)*0.8):]
    total = sum(data)
    count = len(data)
    return total/count

sys.stdout.write(str(get_file_average_volume(sys.argv[1])))

