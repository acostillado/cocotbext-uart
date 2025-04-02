import cocotb
from cocotb.triggers import Timer, Edge
from cocotb.handle import ModifiableObject


class UartSource:
    def __init__(self, signal: ModifiableObject, baud=115200, bits=8, stop_bits=1, parity=None):
        self._signal = signal
        self._baud = baud
        self._bits = bits
        self._stop_bits = stop_bits
        self._parity = parity
        self._bit_time_ns = int(1e9 / baud)

    async def write(self, data: int):
        """Send a byte of UART data."""
        frame = []

        # Start bit
        frame.append(0)

        # Data bits (LSB first)
        for i in range(self._bits):
            frame.append((data >> i) & 1)

        # Parity (optional)
        if self._parity == "even":
            parity_bit = frame[1:self._bits+1].count(1) % 2 == 1
            frame.append(int(parity_bit))
        elif self._parity == "odd":
            parity_bit = frame[1:self._bits+1].count(1) % 2 == 0
            frame.append(int(parity_bit))

        # Stop bits
        frame.extend([1] * self._stop_bits)

        for bit in frame:
            self._signal.value = bit
            await Timer(self._bit_time_ns, units="ns")

        # Leave line idle (high)
        self._signal.value = 1


class UartSink:
    def __init__(self, signal: ModifiableObject, baud=115200, bits=8, stop_bits=1, parity=None):
        self._signal = signal
        self._baud = baud
        self._bits = bits
        self._stop_bits = stop_bits
        self._parity = parity
        self._bit_time_ns = int(1e9 / baud)

    async def read(self):
        """Receive a byte of UART data."""
        # Wait for start bit (falling edge)
        while self._signal.value.integer != 0:
            await Edge(self._signal)

        # Center of first data bit
        await Timer(int(1.5 * self._bit_time_ns), units="ns")

        value = 0
        for i in range(self._bits):
            bit = int(self._signal.value)
            value |= (bit << i)
            await Timer(self._bit_time_ns, units="ns")

        # Optional: skip parity + stop bits
        if self._parity:
            await Timer(self._bit_time_ns, units="ns")  # parity
        await Timer(self._stop_bits * self._bit_time_ns, units="ns")

        return value
