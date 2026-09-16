import numpy as np
from typing import Annotated, Literal

def convert_amplitude_to_power(signal: Annotated[np.typing.NDArray[np.int8], Literal['M', 'N']]): ...
