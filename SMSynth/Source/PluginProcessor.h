/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin processor.

  ==============================================================================
*/

#pragma once

#include <JuceHeader.h>
#include "MappedSampleSound.h"

//==============================================================================
/**
*/

class SmsynthAudioProcessor  : public juce::AudioProcessor
{
public:
    //==============================================================================
    SmsynthAudioProcessor();
    ~SmsynthAudioProcessor() override;

    //==============================================================================
    void prepareToPlay (double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;

   #ifndef JucePlugin_PreferredChannelConfigurations
    bool isBusesLayoutSupported (const BusesLayout& layouts) const override;
   #endif

    void processBlock (juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

    //==============================================================================
    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override;

    //==============================================================================
    const juce::String getName() const override;

    bool acceptsMidi() const override;
    bool producesMidi() const override;
    bool isMidiEffect() const override;
    double getTailLengthSeconds() const override;

    //==============================================================================
    int getNumPrograms() override;
    int getCurrentProgram() override;
    void setCurrentProgram (int index) override;
    const juce::String getProgramName (int index) override;
    void changeProgramName (int index, const juce::String& newName) override;

    //==============================================================================
    void getStateInformation (juce::MemoryBlock& destData) override;
    void setStateInformation (const void* data, int sizeInBytes) override;

	void clearMap();
	void addSample(int pitch, int vel, juce::AudioBuffer<float>* sample);
	void loadConfig(const juce::StringArray& files);
	void readAudio(juce::File file, double pitch, int vel);
	void setSource(const juce::StringArray& files);
	void setFit(const juce::StringArray& files);
	void makeConfig(const juce::StringArray& files);

	juce::AudioProcessorValueTreeState* getState() { return &state; }

	int currBlockSize;
	juce::String sourcePath = "";
	juce::String fitPath = "";
	juce::String configPath = "";

private:
    //==============================================================================
	std::vector<MappedSample> sample_map;
	juce::Synthesiser synth;
	juce::AudioProcessorValueTreeState state;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (SmsynthAudioProcessor)
};
