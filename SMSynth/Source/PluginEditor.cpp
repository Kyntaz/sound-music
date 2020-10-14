/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin editor.

  ==============================================================================
*/

#include "PluginProcessor.h"
#include "PluginEditor.h"

//==============================================================================
SmsynthAudioProcessorEditor::SmsynthAudioProcessorEditor (SmsynthAudioProcessor& p)
    : AudioProcessorEditor (&p), audioProcessor (p)
{
	setStyle(getLookAndFeel());

	logoImg = juce::Drawable::createFromSVG(*juce::parseXML(BinaryData::SoundMusic_svg));
	addAndMakeVisible(*logoImg);

	addAndMakeVisible(titleLbl);
	titleLbl.setText("Synth", juce::dontSendNotification);
	titleLbl.setFont(juce::Font(30, juce::Font::bold));
	titleLbl.setColour(juce::Label::ColourIds::textColourId, juce::Colour(255, 255, 255));
	titleLbl.setJustificationType(juce::Justification(juce::Justification::centred));

	addAndMakeVisible(evolutionParams);
	evolutionParams.setText("Evolution Parameters", juce::dontSendNotification);
	evolutionParams.setJustificationType(juce::Justification(juce::Justification::centred));
	evolutionParams.setFont(evolutionParams.getFont().boldened());

	addAndMakeVisible(genSld);
	genSld.setSliderStyle(juce::Slider::SliderStyle::LinearHorizontal);
	genSld.setTextBoxStyle(juce::Slider::TextBoxRight, true, 50, 20);
	addAndMakeVisible(genSld_l);
	genSld_l.attachToComponent(&genSld, false);
	genSld_l.setText("Generations", juce::dontSendNotification);
	genSld_l.setJustificationType(juce::Justification(juce::Justification::centred));
	genSld_a.reset(new SliderAttachment(*(audioProcessor.getState()), "gens", genSld));

	addAndMakeVisible(mutSld);
	mutSld.setSliderStyle(juce::Slider::SliderStyle::LinearHorizontal);
	mutSld.setTextBoxStyle(juce::Slider::TextBoxRight, true, 50, 20);
	addAndMakeVisible(mutSld_l);
	mutSld_l.attachToComponent(&mutSld, false);
	mutSld_l.setText("Mutations", juce::dontSendNotification);
	mutSld_l.setJustificationType(juce::Justification(juce::Justification::centred));
	mutSld_a.reset(new SliderAttachment(*(audioProcessor.getState()), "mut", mutSld));

	addAndMakeVisible(varSld);
	varSld.setSliderStyle(juce::Slider::SliderStyle::LinearHorizontal);
	varSld.setTextBoxStyle(juce::Slider::TextBoxRight, true, 50, 20);
	addAndMakeVisible(varSld_l);
	varSld_l.attachToComponent(&varSld, false);
	varSld_l.setText("Mutation Variation", juce::dontSendNotification);
	varSld_l.setJustificationType(juce::Justification(juce::Justification::centred));
	varSld_a.reset(new SliderAttachment(*(audioProcessor.getState()), "varMut", varSld));

	addAndMakeVisible(eliteSld);
	eliteSld.setSliderStyle(juce::Slider::SliderStyle::LinearHorizontal);
	eliteSld.setTextBoxStyle(juce::Slider::TextBoxRight, true, 50, 20);
	addAndMakeVisible(eliteSld_l);
	eliteSld_l.attachToComponent(&eliteSld, false);
	eliteSld_l.setText("Elitism", juce::dontSendNotification);
	eliteSld_l.setJustificationType(juce::Justification(juce::Justification::centred));
	eliteSld_a.reset(new SliderAttachment(*(audioProcessor.getState()), "elite", eliteSld));

	addAndMakeVisible(statusTxt);
	statusTxt.setText("Debug Messages Here...");
	statusTxt.setReadOnly(true);

	//addAndMakeVisible(sourceTxt);
	sourceTxt.setText("Source Audio Here...");
	sourceTxt.setMultiLine(true);
	//sourceTxt.setReadOnly(true);

	addAndMakeVisible(fitnessTxt);
	fitnessTxt.setText("Fitness Model Here...");
	fitnessTxt.setReadOnly(true);

	addAndMakeVisible(loSld);
	loSld.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
	loSld.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	addAndMakeVisible(loSld_l);
	loSld_l.attachToComponent(&loSld, false);
	loSld_l.setText("Low Pass", juce::dontSendNotification);
	loSld_l.setJustificationType(juce::Justification(juce::Justification::centred));
	loSld_a.reset(new SliderAttachment(*(audioProcessor.getState()), "loPass", loSld));

	addAndMakeVisible(hiSld);
	hiSld.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
	hiSld.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	addAndMakeVisible(hiSld_l);
	hiSld_l.attachToComponent(&hiSld, false);
	hiSld_l.setText("High Pass", juce::dontSendNotification);
	hiSld_l.setJustificationType(juce::Justification(juce::Justification::centred));
	hiSld_a.reset(new SliderAttachment(*(audioProcessor.getState()), "hiPass", hiSld));

	addAndMakeVisible(grainSld);
	grainSld.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
	grainSld.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	addAndMakeVisible(grainSld_l);
	grainSld_l.attachToComponent(&grainSld, false);
	grainSld_l.setText("Grains", juce::dontSendNotification);
	grainSld_l.setJustificationType(juce::Justification(juce::Justification::centred));
	grainSld_a.reset(new SliderAttachment(*(audioProcessor.getState()), "grains", grainSld));

	addAndMakeVisible(speedSld);
	speedSld.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
	speedSld.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	addAndMakeVisible(speedSld_l);
	speedSld_l.attachToComponent(&speedSld, false);
	speedSld_l.setText("Speed", juce::dontSendNotification);
	speedSld_l.setJustificationType(juce::Justification(juce::Justification::centred));
	speedSld_a.reset(new SliderAttachment(*(audioProcessor.getState()), "speed", speedSld));

	addAndMakeVisible(aSld);
	aSld.setSliderStyle(juce::Slider::SliderStyle::LinearVertical);
	aSld.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	addAndMakeVisible(aSld_l);
	aSld_l.attachToComponent(&aSld, false);
	aSld_l.setText("A", juce::dontSendNotification);
	aSld_l.setJustificationType(juce::Justification(juce::Justification::centred));
	aSld_a.reset(new SliderAttachment(*(audioProcessor.getState()), "atk", aSld));

	addAndMakeVisible(dSld);
	dSld.setSliderStyle(juce::Slider::SliderStyle::LinearVertical);
	dSld.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	addAndMakeVisible(dSld_l);
	dSld_l.attachToComponent(&dSld, false);
	dSld_l.setText("D", juce::dontSendNotification);
	dSld_l.setJustificationType(juce::Justification(juce::Justification::centred));
	dSld_a.reset(new SliderAttachment(*(audioProcessor.getState()), "decay", dSld));

	addAndMakeVisible(sSld);
	sSld.setSliderStyle(juce::Slider::SliderStyle::LinearVertical);
	sSld.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	addAndMakeVisible(sSld_l);
	sSld_l.attachToComponent(&sSld, false);
	sSld_l.setText("S", juce::dontSendNotification);
	sSld_l.setJustificationType(juce::Justification(juce::Justification::centred));
	sSld_a.reset(new SliderAttachment(*(audioProcessor.getState()), "sus", sSld));

	addAndMakeVisible(rSld);
	rSld.setSliderStyle(juce::Slider::SliderStyle::LinearVertical);
	rSld.setTextBoxStyle(juce::Slider::TextBoxBelow, true, 50, 20);
	addAndMakeVisible(rSld_l);
	rSld_l.attachToComponent(&rSld, false);
	rSld_l.setText("R", juce::dontSendNotification);
	rSld_l.setJustificationType(juce::Justification(juce::Justification::centred));
	rSld_a.reset(new SliderAttachment(*(audioProcessor.getState()), "rel", rSld));

	addAndMakeVisible(pingBtn);
	pingBtn.setButtonText("Ping-Pong");
	pingBtn_a.reset(new ButtonAttachment(*(audioProcessor.getState()), "ping", pingBtn));

    // Make sure that before the constructor has finished, you've set the
    // editor's size to whatever you need it to be.
    setSize(800, 420);

	chkStatus();
}

SmsynthAudioProcessorEditor::~SmsynthAudioProcessorEditor()
{
}

//==============================================================================
void SmsynthAudioProcessorEditor::paint (juce::Graphics& g)
{
    // (Our component is opaque, so we must completely fill the background with a solid colour)
    g.fillAll (getLookAndFeel().findColour (juce::ResizableWindow::backgroundColourId));
}

void SmsynthAudioProcessorEditor::resized()
{
    // This is generally where you'll want to lay out the positions of any
    // subcomponents in your editor..

	auto logoWidth = 300;
	auto logoHeight = 80;
	auto logoPad = 10;

	auto titleX = getWidth() - 150;
	auto titleY = 15;
	auto titleW = 180;
	auto titleH = 50;

	auto debugBoxX = 10;
	auto debugBoxY = getHeight() - 35;
	auto debugBoxW = getWidth() - 20;
	auto debugBoxH = 25;

	auto evolutionX = 10;
	auto evolutionY = 120;
	auto evolutionW = 400;
	auto evolutionH = 25;
	auto evolutionP = 20;

	auto paramsX = 440;
	auto paramsY = 120;
	auto paramsW = 70;
	auto paramsH = 100;
	auto paramsP = 10;

	auto adsrX = 450;
	auto adsrY = 250;
	auto adsrW = 30;
	auto adsrH = 80;
	auto adsrP = 20;

	logoImg->setBounds(logoPad, logoPad, logoWidth, logoHeight);
	titleLbl.setBounds(titleX, titleY, titleW, titleH);
	statusTxt.setBounds(debugBoxX, debugBoxY, debugBoxW, debugBoxH);
	evolutionParams.setBounds(evolutionX, evolutionY - 20, evolutionW, evolutionH);
	genSld.setBounds(evolutionX, evolutionY + evolutionH + evolutionP, evolutionW, evolutionH);
	mutSld.setBounds(evolutionX, evolutionY + evolutionH * 2 + evolutionP * 2, evolutionW, evolutionH);
	varSld.setBounds(evolutionX, evolutionY + evolutionH * 3 + evolutionP * 3, evolutionW, evolutionH);
	eliteSld.setBounds(evolutionX, evolutionY + evolutionH * 4 + evolutionP * 4, evolutionW, evolutionH);
	fitnessTxt.setBounds(evolutionX, evolutionY + evolutionH * 5 + evolutionP * 5, debugBoxW, evolutionH);
	hiSld.setBounds(paramsX, paramsY, paramsW, paramsH);
	loSld.setBounds(paramsX + paramsW + paramsP, paramsY, paramsW, paramsH);
	grainSld.setBounds(paramsX + paramsW * 2 + paramsP * 2, paramsY, paramsW, paramsH);
	speedSld.setBounds(paramsX + paramsW * 3 + paramsP * 3, paramsY, paramsW, paramsH);
	aSld.setBounds(adsrX, adsrY, adsrW, adsrH);
	dSld.setBounds(adsrX + adsrW + adsrP, adsrY, adsrW, adsrH);
	sSld.setBounds(adsrX + adsrW * 2 + adsrP * 2, adsrY, adsrW, adsrH);
	rSld.setBounds(adsrX + adsrW * 3 + adsrP * 3, adsrY, adsrW, adsrH);
	pingBtn.setBounds(670, 230, 100, 100);
}

bool SmsynthAudioProcessorEditor::isInterestedInFileDrag(const juce::StringArray& files)
{
	return true;
}

void SmsynthAudioProcessorEditor::filesDropped(const juce::StringArray& files, int x, int y)
{
	auto file = juce::File(files[0]);
	if (file.getFileExtension() == ".synth") {
		audioProcessor.loadConfig(files);
	}
	else if (file.getFileExtension() == ".svm") {
		audioProcessor.setFit(files);
	}
	else {
		audioProcessor.makeConfig(files);
	}
	chkStatus();
}

void SmsynthAudioProcessorEditor::setStyle(juce::LookAndFeel& lf)
{
	juce::Colour bgColour(55, 55, 60);
	juce::Colour txtColour(255, 255, 255);
	juce::Colour lightColour(132, 171, 189);
	juce::Colour mediumColour(175, 237, 234);
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

void SmsynthAudioProcessorEditor::chkStatus()
{
	if (audioProcessor.configPath.isEmpty()) {
		statusTxt.setText("No configuration loaded. Drop a .synth file to load a config or a sound file to generate a new config.");
	}
	else {
		statusTxt.setText("Loaded config from " + audioProcessor.configPath);
	}
	if (audioProcessor.fitPath.isEmpty()) {
		fitnessTxt.setText("Drop a .svm file to use as the fitness model.");
	}
	else {
		fitnessTxt.setText("Loaded fitness from " + audioProcessor.fitPath);
	}

	sourceTxt.setText(audioProcessor.sourcePath);
}
