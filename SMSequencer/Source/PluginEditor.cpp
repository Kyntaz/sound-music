/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin editor.

  ==============================================================================
*/

#include "PluginProcessor.h"
#include "PluginEditor.h"

//==============================================================================
SmsequencerAudioProcessorEditor::SmsequencerAudioProcessorEditor (SmsequencerAudioProcessor& p, juce::AudioProcessorValueTreeState& s)
    : AudioProcessorEditor (&p), audioProcessor (p), state(s)
{
	setStyle(getLookAndFeel());

	logoImg = juce::Drawable::createFromSVG(*juce::parseXML(BinaryData::SoundMusic_svg));
	addAndMakeVisible(*logoImg);

	addAndMakeVisible(titleLabel);
	titleLabel.setText("Sequencer", juce::dontSendNotification);
	titleLabel.setFont(juce::Font(30, juce::Font::bold));
	titleLabel.setColour(juce::Label::ColourIds::textColourId, juce::Colour(80, 110, 125));
	titleLabel.setJustificationType(juce::Justification(juce::Justification::centred));

	addAndMakeVisible(transitionsLabel);
	transitionsLabel.setText("Transition Checks:", juce::dontSendNotification);
	transitionsLabel.setFont(transitionsLabel.getFont().boldened());

	addAndMakeVisible(chkPitchToggle);
	chkPitchToggle.setButtonText("Pitch");
	chkPitchAtch.reset(new ButtonAttachment(state, "chkPitch", chkPitchToggle));

	addAndMakeVisible(chkVelocityToggle);
	chkVelocityToggle.setButtonText("Velocity");
	chkVelocityAtch.reset(new ButtonAttachment(state, "chkVelocity", chkVelocityToggle));

	addAndMakeVisible(chkDurationToggle);
	chkDurationToggle.setButtonText("Duration");
	chkDurationAtch.reset(new ButtonAttachment(state, "chkDuration", chkDurationToggle));

	addAndMakeVisible(arpToggle);
	arpToggle.setButtonText("Arpeggio");
	arpAtch.reset(new ButtonAttachment(state, "arp", arpToggle));

	addAndMakeVisible(levelSlider);
	levelSlider.setSliderStyle(juce::Slider::Rotary);
	levelSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	levelSlider.setRange(1, 10, 1);
	levelSlider.setValue(3);
	addAndMakeVisible(levelSliderLabel);
	levelSliderLabel.attachToComponent(&levelSlider, false);
	levelSliderLabel.setText("Chain Level", juce::dontSendNotification);
	levelSliderLabel.setJustificationType(juce::Justification(juce::Justification::centred));
	chainLevelAtch.reset(new SliderAttachment(state, "chainLevel", levelSlider));

	addAndMakeVisible(pitchSlider);
	pitchSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
	pitchSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	pitchSlider.setRange(-36, 36, 1);
	pitchSlider.setValue(0);
	addAndMakeVisible(pitchSliderLabel);
	pitchSliderLabel.attachToComponent(&pitchSlider, false);
	pitchSliderLabel.setText("Pitch Shift", juce::dontSendNotification);
	pitchSliderLabel.setJustificationType(juce::Justification(juce::Justification::centred));
	pitchShiftAtch.reset(new SliderAttachment(state, "pitchShift", pitchSlider));

	addAndMakeVisible(staccatoSlider);
	staccatoSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
	staccatoSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	staccatoSlider.setRange(-1.0, 1.0, 0.01);
	staccatoSlider.setValue(0.0);
	addAndMakeVisible(staccatoSliderLabel);
	staccatoSliderLabel.attachToComponent(&staccatoSlider, false);
	staccatoSliderLabel.setText("Staccato/Legato", juce::dontSendNotification);
	staccatoSliderLabel.setJustificationType(juce::Justification(juce::Justification::centred));
	staccatoAtch.reset(new SliderAttachment(state, "staccato", staccatoSlider));

	addAndMakeVisible(xVelocitySlider);
	xVelocitySlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
	xVelocitySlider.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	xVelocitySlider.setRange(0.1, 3.0, 0.1);
	xVelocitySlider.setValue(1.0);
	addAndMakeVisible(xVelocitySliderLabel);
	xVelocitySliderLabel.attachToComponent(&xVelocitySlider, false);
	xVelocitySliderLabel.setText("x Velocity", juce::dontSendNotification);
	xVelocitySliderLabel.setJustificationType(juce::Justification(juce::Justification::centred));
	xVelocityAtch.reset(new SliderAttachment(state, "xVelocity", xVelocitySlider));

	addAndMakeVisible(xDurationSlider);
	xDurationSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
	xDurationSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	xDurationSlider.setRange(0.1, 3.0, 0.1);
	xDurationSlider.setValue(1.0);
	addAndMakeVisible(xDurationSliderLabel);
	xDurationSliderLabel.attachToComponent(&xDurationSlider, false);
	xDurationSliderLabel.setText("x Duration", juce::dontSendNotification);
	xDurationSliderLabel.setJustificationType(juce::Justification(juce::Justification::centred));
	xDurationAtch.reset(new SliderAttachment(state, "xDuration", xDurationSlider));

	addAndMakeVisible(maxOctavesSlider);
	maxOctavesSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
	maxOctavesSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	maxOctavesSlider.setRange(-1, 6, 1);
	maxOctavesSlider.setValue(6);
	addAndMakeVisible(maxOctavesSliderLabel);
	maxOctavesSliderLabel.attachToComponent(&maxOctavesSlider, false);
	maxOctavesSliderLabel.setText("Max Octave", juce::dontSendNotification);
	maxOctavesSliderLabel.setJustificationType(juce::Justification(juce::Justification::centred));
	maxOctaveAtch.reset(new SliderAttachment(state, "maxOctave", maxOctavesSlider));

	addAndMakeVisible(minOctavesSlider);
	minOctavesSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
	minOctavesSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	minOctavesSlider.setRange(-1, 6, 1);
	minOctavesSlider.setValue(-1);
	addAndMakeVisible(minOctavesSliderLabel);
	minOctavesSliderLabel.attachToComponent(&minOctavesSlider, false);
	minOctavesSliderLabel.setText("Min Octave", juce::dontSendNotification);
	minOctavesSliderLabel.setJustificationType(juce::Justification(juce::Justification::centred));
	minOctaveAtch.reset(new SliderAttachment(state, "minOctave", minOctavesSlider));

	addAndMakeVisible(velocitySlider);
	velocitySlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
	velocitySlider.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	velocitySlider.setRange(0, 127, 1);
	velocitySlider.setValue(0);
	addAndMakeVisible(velocitySliderLabel);
	velocitySliderLabel.attachToComponent(&velocitySlider, false);
	velocitySliderLabel.setText("Velocity", juce::dontSendNotification);
	velocitySliderLabel.setJustificationType(juce::Justification(juce::Justification::centred));
	velocityAtch.reset(new SliderAttachment(state, "velocity", velocitySlider));

	addAndMakeVisible(durationSlider);
	durationSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
	durationSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	durationSlider.setRange(0.0, 5.0, 0.01);
	durationSlider.setValue(0.0);
	addAndMakeVisible(durationSliderLabel);
	durationSliderLabel.attachToComponent(&durationSlider, false);
	durationSliderLabel.setText("Duration", juce::dontSendNotification);
	durationSliderLabel.setJustificationType(juce::Justification(juce::Justification::centred));
	durationAtch.reset(new SliderAttachment(state, "duration", durationSlider));

	addAndMakeVisible(debugBox);
	debugBox.setText("Debug Messages Here...");
	debugBox.setReadOnly(true);

	checkModelStatus();

    // Make sure that before the constructor has finished, you've set the
    // editor's size to whatever you need it to be.
    setSize (800, 420);
}

SmsequencerAudioProcessorEditor::~SmsequencerAudioProcessorEditor()
{
}

//==============================================================================
void SmsequencerAudioProcessorEditor::paint (juce::Graphics& g)
{
    // (Our component is opaque, so we must completely fill the background with a solid colour)
    g.fillAll (getLookAndFeel().findColour (juce::ResizableWindow::backgroundColourId));
}

void SmsequencerAudioProcessorEditor::resized()
{
    // This is generally where you'll want to lay out the positions of any
    // subcomponents in your editor..

	auto logoWidth = 300;
	auto logoHeight = 80;
	auto logoPad = 10;

	auto titleX = getWidth() - 190;
	auto titleY = 15;
	auto titleW = 180;
	auto titleH = 50;

	auto transitionsX = getWidth() / 6;
	auto transitionsY = getHeight() - 55;
	auto transitionsW = 100;
	auto transitionsH = 30;
	auto transitionsSep = 5;

	auto levelSliderX = 400;
	auto levelSliderY = 240;
	auto levelSliderW = 180;
	auto levelSliderH = 180;

	auto rotariesX = getWidth() - 250;
	auto rotariesX2 = 50;
	auto rotariesY = 150;
	auto rotariesW = 80;
	auto rotariesH = 80;
	auto rotariesSep = 30;

	auto debugBoxX = 10;
	auto debugBoxY = getHeight() - 35;
	auto debugBoxW = getWidth() - 20;
	auto debugBoxH = 25;

	logoImg->setBounds(logoPad, logoPad, logoWidth, logoHeight);
	titleLabel.setBounds(titleX, titleY, titleW, titleH);

	transitionsLabel.setBounds(transitionsX, transitionsY, transitionsW, transitionsH);
	chkPitchToggle.setBounds(transitionsX, transitionsY + transitionsH + transitionsSep, transitionsW, transitionsH);
	chkVelocityToggle.setBounds(transitionsX, transitionsY + transitionsH*2 + transitionsSep*2, transitionsW, transitionsH);
	chkDurationToggle.setBounds(transitionsX, transitionsY + transitionsH*3 + transitionsSep*3, transitionsW, transitionsH);
	arpToggle.setBounds(transitionsX, transitionsY + transitionsH * 3 + transitionsSep * 3, transitionsW, transitionsH);
	transitionsLabel.setCentrePosition(transitionsX, transitionsY);
	chkPitchToggle.setCentrePosition(transitionsX*2, transitionsY);
	chkVelocityToggle.setCentrePosition(transitionsX*3, transitionsY);
	chkDurationToggle.setCentrePosition(transitionsX*4, transitionsY);
	arpToggle.setCentrePosition(transitionsX * 5, transitionsY);

	levelSlider.setBounds(0, 0, levelSliderW, levelSliderH);
	levelSlider.setCentrePosition(levelSliderX, levelSliderY);

	pitchSlider.setBounds(rotariesX, rotariesY, rotariesW, rotariesH);
	staccatoSlider.setBounds(rotariesX + rotariesW + rotariesSep, rotariesY, rotariesW, rotariesH);
	xVelocitySlider.setBounds(rotariesX, rotariesY + rotariesH + rotariesSep, rotariesW, rotariesH);
	xDurationSlider.setBounds(rotariesX + rotariesW + rotariesSep, rotariesY + rotariesH + rotariesSep, rotariesW, rotariesH);

	minOctavesSlider.setBounds(rotariesX2, rotariesY, rotariesW, rotariesH);
	maxOctavesSlider.setBounds(rotariesX2 + rotariesW + rotariesSep, rotariesY, rotariesW, rotariesH);
	velocitySlider.setBounds(rotariesX2, rotariesY + rotariesH + rotariesSep, rotariesW, rotariesH);
	durationSlider.setBounds(rotariesX2 + rotariesW + rotariesSep, rotariesY + rotariesH + rotariesSep, rotariesW, rotariesH);

	debugBox.setBounds(debugBoxX, debugBoxY, debugBoxW, debugBoxH);
}

void SmsequencerAudioProcessorEditor::setStyle(juce::LookAndFeel& lf)
{
	juce::Colour bgColour(255, 255, 255);
	juce::Colour txtColour(50, 65, 70);
	juce::Colour lightColour(88, 141, 168);
	juce::Colour mediumColour(80, 110, 125);
	juce::Colour invisible(0.0f, 0.0f, 0.0f, 0.0f);

	lf.setColour(juce::ResizableWindow::backgroundColourId, bgColour);
	lf.setColour(juce::Label::textColourId, txtColour);
	lf.setColour(juce::ToggleButton::ColourIds::textColourId, txtColour);
	lf.setColour(juce::ToggleButton::ColourIds::tickColourId, txtColour);
	lf.setColour(juce::ToggleButton::ColourIds::tickDisabledColourId, txtColour);
	lf.setColour(juce::Slider::ColourIds::textBoxTextColourId, txtColour);
	lf.setColour(juce::Slider::ColourIds::textBoxOutlineColourId, invisible);
	lf.setColour(juce::Slider::ColourIds::thumbColourId, lightColour);
	lf.setColour(juce::Slider::ColourIds::trackColourId, mediumColour);
	lf.setColour(juce::Slider::ColourIds::backgroundColourId, txtColour);
	lf.setColour(juce::Slider::ColourIds::rotarySliderFillColourId, mediumColour);
	lf.setColour(juce::Slider::ColourIds::rotarySliderOutlineColourId, txtColour);
	lf.setColour(juce::TextEditor::ColourIds::backgroundColourId, bgColour);
	lf.setColour(juce::TextEditor::ColourIds::outlineColourId, lightColour);
	lf.setColour(juce::TextEditor::ColourIds::textColourId, txtColour);
}

bool SmsequencerAudioProcessorEditor::isInterestedInFileDrag(const juce::StringArray& files)
{
	return true;
}

void SmsequencerAudioProcessorEditor::filesDropped(const juce::StringArray& files, int x, int y)
{
	auto file = juce::File(files[0]);
	if (file.getFileExtension() == ".seq") {
		debugBox.setText("Loading model...");
		audioProcessor.loadSeq(files);
	}
	else if (file.getFileExtension() == ".mp3" || file.getFileExtension() == ".wav" || file.getFileExtension() == ".aiff") {
		debugBox.setText("Processing audio, might take a while...");
		audioProcessor.loadAudio(files);
	}
	checkModelStatus();
}

void SmsequencerAudioProcessorEditor::checkModelStatus()
{
	auto modelPath = audioProcessor.getCurrentModel();
	if (modelPath.isEmpty()) {
		debugBox.setText("No sequencer model loaded. Drag and drop an audio or model file to load it.");
	}
	else {
		debugBox.setText("Loaded model in " + modelPath);
	}
}
