/*
  ==============================================================================

    MappedSampleVoice.h
    Created: 21 Aug 2020 3:49:00pm
    Author:  pQ

  ==============================================================================
*/

#pragma once

#include <JuceHeader.h>
#include <cmath>#include "PluginProcessor.h"

class SmsynthAudioProcessor;

class MappedSampleVoice : public juce::SynthesiserVoice {
private:
	juce::ADSR adsr;
	static const int n_grains = 20;
	double curr_sample_hi[n_grains];
	double curr_sample_lo[n_grains];
	juce::dsp::ProcessorDuplicator<juce::dsp::IIR::Filter<float>, juce::dsp::IIR::Coefficients<float>> hiFilter;
	juce::dsp::ProcessorDuplicator<juce::dsp::IIR::Filter<float>, juce::dsp::IIR::Coefficients<float>> loFilter;
	float curr_vel = 0;
	float curr_shift = 0;
	float curr_pitch = 0;
	float hiQ = 0;
	float loQ = 0;
	bool playing = false;
	SmsynthAudioProcessor* owner;

public:
	MappedSampleVoice(SmsynthAudioProcessor* processor);
	bool canPlaySound(juce::SynthesiserSound* sound) override;

	// Inherited via SynthesiserVoice
	virtual void startNote(int midiNoteNumber, float velocity, juce::SynthesiserSound* sound, int currentPitchWheelPosition) override;
	virtual void stopNote(float velocity, bool allowTailOff) override;
	virtual void pitchWheelMoved(int newPitchWheelValue) override;
	virtual void controllerMoved(int controllerNumber, int newControllerValue) override;
	virtual void renderNextBlock(juce::AudioBuffer<float>& outputBuffer, int startSample, int numSamples) override;
	void resetGrains();
};