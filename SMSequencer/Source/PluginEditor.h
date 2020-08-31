/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin editor.

  ==============================================================================
*/

#pragma once

#include <JuceHeader.h>
#include "PluginProcessor.h"

typedef juce::AudioProcessorValueTreeState::SliderAttachment SliderAttachment;
typedef juce::AudioProcessorValueTreeState::ButtonAttachment ButtonAttachment;

//==============================================================================
/**
*/
class SmsequencerAudioProcessorEditor  : public juce::AudioProcessorEditor,
	public juce::FileDragAndDropTarget
{
public:
    SmsequencerAudioProcessorEditor (SmsequencerAudioProcessor&, juce::AudioProcessorValueTreeState&);
    ~SmsequencerAudioProcessorEditor() override;

    //==============================================================================
    void paint (juce::Graphics&) override;
    void resized() override;

	void setStyle(juce::LookAndFeel&);

	bool isInterestedInFileDrag(const juce::StringArray&) override;
	void filesDropped(const juce::StringArray&, int, int) override;

	void checkModelStatus();

private:
    // This reference is provided as a quick way for your editor to
    // access the processor object that created it.
    SmsequencerAudioProcessor& audioProcessor;
	juce::AudioProcessorValueTreeState& state;

	std::unique_ptr<juce::Drawable> logoImg;
	juce::Label titleLabel;

	juce::Label transitionsLabel;
	juce::ToggleButton chkPitchToggle;
	juce::ToggleButton chkVelocityToggle;
	juce::ToggleButton chkDurationToggle;
	juce::ToggleButton arpToggle;

	juce::Label levelSliderLabel;
	juce::Slider levelSlider;
	juce::Label pitchSliderLabel;
	juce::Slider pitchSlider;
	juce::Label xVelocitySliderLabel;
	juce::Slider xVelocitySlider;
	juce::Label xDurationSliderLabel;
	juce::Slider xDurationSlider;
	juce::Label staccatoSliderLabel;
	juce::Slider staccatoSlider;
	juce::Label minOctavesSliderLabel;
	juce::Slider minOctavesSlider;
	juce::Label maxOctavesSliderLabel;
	juce::Slider maxOctavesSlider;
	juce::Label velocitySliderLabel;
	juce::Slider velocitySlider;
	juce::Label durationSliderLabel;
	juce::Slider durationSlider;
	juce::TextEditor debugBox;

	std::unique_ptr<ButtonAttachment> chkPitchAtch;
	std::unique_ptr<ButtonAttachment> chkVelocityAtch;
	std::unique_ptr<ButtonAttachment> chkDurationAtch;
	std::unique_ptr<ButtonAttachment> arpAtch;

	std::unique_ptr<SliderAttachment> chainLevelAtch;

	std::unique_ptr<SliderAttachment> pitchShiftAtch;
	std::unique_ptr<SliderAttachment> staccatoAtch;
	std::unique_ptr<SliderAttachment> xVelocityAtch;
	std::unique_ptr<SliderAttachment> xDurationAtch;

	std::unique_ptr<SliderAttachment> minOctaveAtch;
	std::unique_ptr<SliderAttachment> maxOctaveAtch;
	std::unique_ptr<SliderAttachment> velocityAtch;
	std::unique_ptr<SliderAttachment> durationAtch;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (SmsequencerAudioProcessorEditor)
};
