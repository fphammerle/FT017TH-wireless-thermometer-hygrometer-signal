#!/usr/bin/env python3

import argparse
import itertools
import pathlib

import numpy
import numpy.ma
from matplotlib import pyplot
import scipy.io.wavfile
import scipy.signal


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
    msg_start_indices = [
        next(silence_mask_iter)[0]
        for is_silence, silence_mask_iter in itertools.groupby(
            enumerate(silence_mask), key=lambda v: v[1]
        )
        if not is_silence
    ]
    msgs_frames = list(
        filter(
            lambda f: len(f) > 10000,
            map(numpy.trim_zeros, numpy.split(smoothed_frames, msg_start_indices)),
        )
    )
    print("number of messages:", len(msgs_frames))
    bit_lengths = []
    for msg_frames, ax in zip(msgs_frames, pyplot.subplots(len(msgs_frames))[1]):
        # pyplot.figure()
        # pyplot.plot(msg_frames)
        threshold = numpy.max(msg_frames) / 4
        digital_msg_frames = msg_frames > threshold
        # pyplot.plot(digital_msg_frames * threshold)
        bits = []
        for bit, bit_frames_iter in itertools.groupby(
            numpy.trim_zeros(digital_msg_frames, trim="f")
        ):
            bit_length = sum(1 for _ in bit_frames_iter)
            bit_lengths.append(bit_length)
            bits.append(bit)
            if bit_length > 36:
                bits.append(bit)
        print("message length:", len(bits), "bits")
        ax.plot(bits)
    # pyplot.hist(bit_lengths, bins=80, range=(0, 80))
    pyplot.show()


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
