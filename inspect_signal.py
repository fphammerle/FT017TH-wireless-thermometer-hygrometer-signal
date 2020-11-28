#!/usr/bin/env python3

import argparse
import itertools
import pathlib
import struct
import typing

import manchester_code
import numpy
import scipy.io.wavfile
import scipy.ndimage
import scipy.signal
from matplotlib import pyplot


def inspect_transmission(smoothed_frames: numpy.ndarray) -> typing.List[int]:
    # pyplot.figure()
    # pyplot.plot(smoothed_frames)
    rolling_mean = scipy.ndimage.uniform_filter1d(smoothed_frames, size=21 * 16)
    minimum_threshold = numpy.max(smoothed_frames) / 5
    threshold = numpy.where(
        rolling_mean > minimum_threshold, rolling_mean, minimum_threshold
    )
    digital_frames = smoothed_frames > threshold
    # pyplot.plot(digital_frames * threshold)
    bit_lengths = []
    manchester_bits = []
    for bit, bit_frames_iter in itertools.groupby(
        numpy.trim_zeros(digital_frames, trim="f")
    ):
        bit_length = sum(1 for _ in bit_frames_iter)
        bit_lengths.append(bit_length)
        manchester_bits.append(bit)
        if bit_length > 36:
            manchester_bits.append(bit)
    # print("transmission length:", len(manchester_bits), "manchester bits")
    # subplot.plot(manchester_bits)
    assert len(manchester_bits) == 390
    repeats_manchester_bits = numpy.split(numpy.array(manchester_bits), 3)
    assert numpy.array_equal(repeats_manchester_bits[0], repeats_manchester_bits[1])
    repeats_manchester_bits[2][-2] = repeats_manchester_bits[1][-2]  # FIXME
    assert numpy.array_equal(repeats_manchester_bits[0], repeats_manchester_bits[2])
    inspect_message(list(manchester_code.decode_bits(repeats_manchester_bits[0])))
    return bit_lengths


def inspect_message(data_bits: typing.List[bool]) -> None:
    assert len(data_bits) == (390 // 3 // 2) == 65
    assert data_bits[:9] == [True] * 9, "sync?"
    temperature_index, = struct.unpack(
        ">H", numpy.packbits(data_bits[33:45], bitorder="big")
    )
    # advertised range: [-40°C, +60°C]
    # intercept: -40°C = -40°F
    # slope estimated with statsmodels.regression.linear_model.OLS
    # 12 bits have sufficient range: 2**12 * slope / 2**4 - 40 = 73.76
    temperature_celsius = temperature_index / 576.077364 - 40
    # advertised range: [10%, 99%]
    # intercept: 0%
    # slope estimated with statsmodels.regression.linear_model.OLS
    # 12 bits have sufficient range: 2**12 * slope / 2**4 + 0 = 1.27
    relative_humidity_index, = struct.unpack(
        ">H", numpy.packbits(data_bits[45:57], bitorder="big")
    )
    relative_humidity = relative_humidity_index / 51451.432435
    print(
        numpy.packbits(data_bits[9:33], bitorder="big"),  # address & battery?
        # f"{data_bytes[0]:02x}",
        f"{temperature_celsius:.01f}°C",
        f"{relative_humidity*100:.01f}%",
        numpy.packbits(data_bits[57:], bitorder="big"),  # checksum?
        sep="\t",
    )


def inspect_recording(recording_path: pathlib.Path):
    samplerate_per_sec, data = scipy.io.wavfile.read(recording_path)
    print("sample rate:", samplerate_per_sec, "Hz")
    assert data.shape[1:] == (2,)
    assert (data[:, 0] == data[:, 1]).all()
    print("frames before trimming:", data.shape[0])
    frames = data[:, 0]
    # pyplot.plot(frames, linewidth=0.5)
    smoothed_frames = scipy.signal.medfilt(frames, kernel_size=21)
    # pyplot.plot(smoothed_frames)
    silence_mask = scipy.signal.medfilt(smoothed_frames == 0, kernel_size=21)
    transmission_start_indices = [
        next(silence_mask_iter)[0]
        for is_silence, silence_mask_iter in itertools.groupby(
            enumerate(silence_mask), key=lambda v: v[1]
        )
        if not is_silence
    ]
    transmissions_frames = list(
        filter(
            lambda f: len(f) > 10000,
            map(
                numpy.trim_zeros,
                numpy.split(smoothed_frames, transmission_start_indices),
            ),
        )
    )
    print("number of transmissions:", len(transmissions_frames))
    bit_lengths: typing.List[int] = []
    # for transmission_frames, subplot in zip(
    #    transmissions_frames, pyplot.subplots(len(transmissions_frames))[1]
    # ):
    for transmission_frames in transmissions_frames:
        bit_lengths.extend(inspect_transmission(transmission_frames))
    # pyplot.hist(bit_lengths, bins=80, range=(0, 80))
    # pyplot.show()


def _main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "recording_path",
        type=pathlib.Path,
        nargs="?",
        default=pathlib.Path(__file__).parent.joinpath(
            "gqrx_20201127_110315_433893500.silences-shortened-4s.wav"
        ),
    )
    args = argparser.parse_args()
    inspect_recording(args.recording_path)


if __name__ == "__main__":
    _main()
