import numpy as np
from more_itertools import sliced
from bitstring import Bits


SCREE_BASE_ADDR = 16384
HACK_SCREEN_RES = 256, 512  # rows x columns
BYTE_SIZE = 16
BYTES_ON_SCREEN = HACK_SCREEN_RES[0]*HACK_SCREEN_RES[1]//BYTE_SIZE  # 8k


DEFAULT_CLASS_NAME = 'DrawTest'
DEFAULT_FUNC_NAME = 'Test'
DEFAULT_OUTPUT = f"{DEFAULT_CLASS_NAME}.jack"


jack_class = """
class {class_name}{{
    {functions}
}}
"""

image: np.ndarray = np.random.randint(2, size=HACK_SCREEN_RES, dtype=np.int16)


integers_to_poke = []  # will have size {BYTES_ON_SCREEN}

for row in image:
    row_as_bytes = list(sliced(row.tolist(), BYTE_SIZE))

    for binary_list in row_as_bytes:
        binary_list = map(str, binary_list)
        integer = Bits(bin=''.join(binary_list)).int
        integers_to_poke.append(integer)


jack_draw_function = """
    function void fullDraw{func_name}(){{
        var int baseAddress;
        let baseAddress = {screen_base_addr}; 
        {poke_calls}
        return;
    }}
"""

poke_calls = [
    f"do Memory.poke(baseAddress+{index}, {integer});"
    for index, integer in enumerate(integers_to_poke)
]

poke_calls = '\n\t\t'.join(poke_calls)



class_name = DEFAULT_CLASS_NAME
func_name = DEFAULT_FUNC_NAME


jack_code = jack_class.format(
    class_name=class_name,
    functions=jack_draw_function.format(
        func_name=func_name,
        screen_base_addr=SCREE_BASE_ADDR,
        poke_calls=poke_calls
    )
)

with open(DEFAULT_OUTPUT, 'w') as file:
    file.write(jack_code)
