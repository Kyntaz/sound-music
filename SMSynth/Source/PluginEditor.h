/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin editor.

  ==============================================================================
*/

#pragma once

#include <JuceHeader.h>
#include "PluginProcessor.h"

//==============================================================================
/**
*/

typedef juce::AudioProcessorValueTreeState::SliderAttachment SliderAttachment;
typedef juce::AudioProcessorValueTreeState::ButtonAttachment ButtonAttachment;

class SmsynthAudioProcessorEditor  : public juce::AudioProcessorEditor, public juce::FileDragAndDropTarget
{
public:
    SmsynthAudioProcessorEditor (SmsynthAudioProcessor&);
    ~SmsynthAudioProcessorEditor() override;

    //==============================================================================
    void paint (juce::Graphics&) override;
    void resized() override;

	// Inherited via FileDragAndDropTarget
	virtual bool isInterestedInFileDrag(const juce::StringArray& files) override;
	virtual void filesDropped(const juce::StringArray& files, int x, int y) override;

	void setStyle(juce::LookAndFeel&);

	void chkStatus();

private:
    // This reference is provided as a quick way for your editor to
    // access the processor object that created it.
    SmsynthAudioProcessor& audioProcessor;

	juce::Label titleLbl;
	std::unique_ptr<juce::Drawable> logoImg;

	juce::Label evolutionParams;
	juce::TextButton evolutionBtn;
	
	juce::ToggleButton pingBtn;
	std::unique_ptr<ButtonAttachment> pingBtn_a;
	juce::TextEditor fitnessTxt;
	juce::TextEditor sourceTxt;
	juce::TextEditor statusTxt;

	juce::Slider genSld;
	juce::Label genSld_l;
	std::unique_ptr<SliderAttachment> genSld_a;

	juce::Slider mutSld;
	juce::Label mutSld_l;
	std::unique_ptr<SliderAttachment> mutSld_a;

	juce::Slider varSld;
	juce::Label varSld_l;
	std::unique_ptr<SliderAttachment> varSld_a;

	juce::Slider eliteSld;
	juce::Label eliteSld_l;
	std::unique_ptr<SliderAttachment> eliteSld_a;

	juce::Slider hiSld;
	juce::Label hiSld_l;
	std::unique_ptr<SliderAttachment> hiSld_a;

	juce::Slider loSld;
	juce::Label loSld_l;
	std::unique_ptr<SliderAttachment> loSld_a;

	juce::Slider grainSld;
	juce::Label grainSld_l;
	std::unique_ptr<SliderAttachment> grainSld_a;

	juce::Slider speedSld;
	juce::Label speedSld_l;
	std::unique_ptr<SliderAttachment> speedSld_a;

	juce::Slider aSld;
	juce::Label aSld_l;
	std::unique_ptr<SliderAttachment> aSld_a;

	juce::Slider dSld;
	juce::Label dSld_l;
	std::unique_ptr<SliderAttachment> dSld_a;

	juce::Slider sSld;
	juce::Label sSld_l;
	std::unique_ptr<SliderAttachment> sSld_a;

	juce::Slider rSld;
	juce::Label rSld_l;
	std::unique_ptr<SliderAttachment> rSld_a;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (SmsynthAudioProcessorEditor)
};
