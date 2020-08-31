/*
  ==============================================================================

    MappedSampleSound.h
    Created: 21 Aug 2020 3:40:48pm
    Author:  pQ

  ==============================================================================
*/

#pragma once

#include <JuceHeader.h>

struct MappedSample {
	double pitch;
	int vel;
	std::unique_ptr<juce::AudioBuffer<float>> sample;
};

class MappedSamplerSound : public juce::SynthesiserSound {
public:
	std::vector<MappedSample>* sample_map;

	MappedSamplerSound(std::vector<MappedSample>* m):
		SynthesiserSound(), sample_map(m) {}

	bool appliesToNote(int note) override { return true; }
	bool appliesToChannel(int channel) override { return true; }
};