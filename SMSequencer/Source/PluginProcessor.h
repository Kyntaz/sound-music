/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin processor.

  ==============================================================================
*/

#pragma once

#include <JuceHeader.h>

struct Note {
	int pitch;
	int velocity;
	double duration;
};

//==============================================================================
/**
*/
class SmsequencerAudioProcessor  : public juce::AudioProcessor
{
public:
    //==============================================================================
    SmsequencerAudioProcessor();
    ~SmsequencerAudioProcessor() override;

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

	void loadSeq(const juce::StringArray&);
	void loadAudio(const juce::StringArray&);

	void clearModel();
	void addEntryToModel();
	void addNoteToModel(int, int, double);

	Note getNextNote();

	juce::String getCurrentModel() { return modelPath; }

private:
    //==============================================================================
	std::vector<std::vector<Note>> model;
	std::vector<Note> history;
	std::vector<int> chord;
	int lastNote = 0;
	int legatoBuffer = 0;
	double currDur = 0;
	int time;
	double sampRate;

	juce::String modelPath;

	juce::AudioParameterBool* chkPitch;
	juce::AudioParameterBool* chkVelocity;
	juce::AudioParameterBool* chkDuration;
	juce::AudioParameterBool* arp;

	juce::AudioParameterInt* chainLevel;

	juce::AudioParameterInt* pitchShift;
	juce::AudioParameterFloat* staccatto;
	juce::AudioParameterFloat* xVelocity;
	juce::AudioParameterFloat* xDuration;
	
	juce::AudioParameterInt* minOctave;
	juce::AudioParameterInt* maxOctave;
	juce::AudioParameterInt* velocity;
	juce::AudioParameterFloat* duration;

	juce::AudioProcessorValueTreeState state;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (SmsequencerAudioProcessor)
};
