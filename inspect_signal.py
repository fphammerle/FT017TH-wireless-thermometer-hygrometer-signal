#!/usr/bin/env python3

import itertools

import numpy
import numpy.ma
from matplotlib import pyplot
import scipy.io.wavfile
import scipy.signal


def main():
    samplerate_per_sec, data = scipy.io.wavfile.read(
        "./gqrx_20201127_090051_433893500.silences-shortened-4s.wav"
    )
    print("sample rate:", samplerate_per_sec, "Hz")
    assert data.shape[1:] == (2,)
    assert (data[:, 0] == data[:, 1]).all()
    print("frames before trimming:", data.shape[0])
    frames = data[:, 0]
    # pyplot.plot(frames, linewidth=0.5)
    smoothed_frames = scipy.signal.medfilt(frames, kernel_size=31)
    # pyplot.plot(smoothed_frames)
    silence_mask = scipy.signal.medfilt(smoothed_frames == 0, kernel_size=31)
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
    for msg_frames in msgs_frames:
        # pyplot.plot(msg_frames)
        digital_msg_frames = numpy.trim_zeros(
            msg_frames > (numpy.max(msg_frames) / 4), trim="f"
        )
        # pyplot.plot(digital_msg_frames[:-5000])
        bits = []
        for bit, bit_frames_iter in itertools.groupby(digital_msg_frames):
            bit_length = sum(1 for _ in bit_frames_iter)
            bit_lengths.append(bit_length)
            bits.append(bit)
            if bit_length > 36:
                bits.append(bit)
        print("message length:", len(bits), "bits")
        pyplot.plot(bits)
    # pyplot.hist(bit_lengths, bins=80, range=(0, 80))
    pyplot.show()


if __name__ == "__main__":
    main()
