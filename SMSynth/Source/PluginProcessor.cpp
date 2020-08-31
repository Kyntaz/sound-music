/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin processor.

  ==============================================================================
*/

#include "PluginProcessor.h"
#include "PluginEditor.h"
#include "MappedSampleVoice.h"

//==============================================================================
SmsynthAudioProcessor::SmsynthAudioProcessor()
#ifndef JucePlugin_PreferredChannelConfigurations
     : AudioProcessor (BusesProperties()
                     #if ! JucePlugin_IsMidiEffect
                      #if ! JucePlugin_IsSynth
                       .withInput  ("Input",  juce::AudioChannelSet::stereo(), true)
                      #endif
                       .withOutput ("Output", juce::AudioChannelSet::stereo(), true)
                     #endif
                       ),
#endif
	state(*this, nullptr, juce::Identifier("SMSynth"),
	{
			std::make_unique<juce::AudioParameterInt>("gens", "Generations", 1, 500, 50),
			std::make_unique<juce::AudioParameterFloat>("mut", "Mutations", 0.0f, 5.0f, 3.0f),
			std::make_unique<juce::AudioParameterFloat>("varMut", "Var Mutations", 0.0f, 5.0f, 2.0f),
			std::make_unique<juce::AudioParameterFloat>("elite", "Elitism", 0.0f, 1.0f, 0.2f),
			std::make_unique<juce::AudioParameterFloat>("hiPass", "High Pass", 0.0f, 1.0f, 0.5f),
			std::make_unique<juce::AudioParameterFloat>("loPass", "Low Pass", 0.0f, 1.0f, 0.0f),
			std::make_unique<juce::AudioParameterInt>("grains", "Grains", 1, 20, 3),
			std::make_unique<juce::AudioParameterFloat>("atk", "Attack", 0.0f, 5.0f, 0.1f),
			std::make_unique<juce::AudioParameterFloat>("decay", "Decay", 0.0f, 5.0f, 0.1f),
			std::make_unique<juce::AudioParameterFloat>("sus", "Sustain", 0.0f, 1.0f, 1.0f),
			std::make_unique<juce::AudioParameterFloat>("rel", "Release", 0.0f, 5.0f, 0.1f),
			std::make_unique<juce::AudioParameterBool>("ping", "Ping-Pong", false)
	})
{
	auto sound = new MappedSamplerSound(&sample_map);
	synth.clearSounds();
	synth.addSound(sound);
	synth.clearVoices();
	for (int i = 0; i < 1; i++)
		synth.addVoice(new MappedSampleVoice(this));
	DBG(juce::String(synth.getNumVoices()));
	synth.setNoteStealingEnabled(true);
}

SmsynthAudioProcessor::~SmsynthAudioProcessor()
{
}

//==============================================================================
const juce::String SmsynthAudioProcessor::getName() const
{
    return JucePlugin_Name;
}

bool SmsynthAudioProcessor::acceptsMidi() const
{
   #if JucePlugin_WantsMidiInput
    return true;
   #else
    return false;
   #endif
}

bool SmsynthAudioProcessor::producesMidi() const
{
   #if JucePlugin_ProducesMidiOutput
    return true;
   #else
    return false;
   #endif
}

bool SmsynthAudioProcessor::isMidiEffect() const
{
   #if JucePlugin_IsMidiEffect
    return true;
   #else
    return false;
   #endif
}

double SmsynthAudioProcessor::getTailLengthSeconds() const
{
    return 0.0;
}

int SmsynthAudioProcessor::getNumPrograms()
{
    return 1;   // NB: some hosts don't cope very well if you tell them there are 0 programs,
                // so this should be at least 1, even if you're not really implementing programs.
}

int SmsynthAudioProcessor::getCurrentProgram()
{
    return 0;
}

void SmsynthAudioProcessor::setCurrentProgram (int index)
{
}

const juce::String SmsynthAudioProcessor::getProgramName (int index)
{
    return {};
}

void SmsynthAudioProcessor::changeProgramName (int index, const juce::String& newName)
{
}

//==============================================================================
void SmsynthAudioProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
{
    // Use this method as the place to do any pre-playback
    // initialisation that you need..
	synth.setCurrentPlaybackSampleRate(sampleRate);
	for (int i = 0; i < synth.getNumVoices(); i++) {
		synth.getVoice(i)->setCurrentPlaybackSampleRate(sampleRate);
	}
	currBlockSize = samplesPerBlock;
}

void SmsynthAudioProcessor::releaseResources()
{
    // When playback stops, you can use this as an opportunity to free up any
    // spare memory, etc.
}

#ifndef JucePlugin_PreferredChannelConfigurations
bool SmsynthAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
  #if JucePlugin_IsMidiEffect
    juce::ignoreUnused (layouts);
    return true;
  #else
    // This is the place where you check if the layout is supported.
    // In this template code we only support mono or stereo.
    if (layouts.getMainOutputChannelSet() != juce::AudioChannelSet::mono()
     && layouts.getMainOutputChannelSet() != juce::AudioChannelSet::stereo())
        return false;

    // This checks if the input layout matches the output layout
   #if ! JucePlugin_IsSynth
    if (layouts.getMainOutputChannelSet() != layouts.getMainInputChannelSet())
        return false;
   #endif

    return true;
  #endif
}
#endif

void SmsynthAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
{
	/*
    juce::ScopedNoDenormals noDenormals;
    auto totalNumInputChannels  = getTotalNumInputChannels();
    auto totalNumOutputChannels = getTotalNumOutputChannels();

    // In case we have more outputs than inputs, this code clears any output
    // channels that didn't contain input data, (because these aren't
    // guaranteed to be empty - they may contain garbage).
    // This is here to avoid people getting screaming feedback
    // when they first compile a plugin, but obviously you don't need to keep
    // this code if your algorithm always overwrites all the output channels.
    for (auto i = totalNumInputChannels; i < totalNumOutputChannels; ++i)
        buffer.clear (i, 0, buffer.getNumSamples());

    // This is the place where you'd normally do the guts of your plugin's
    // audio processing...
    // Make sure to reset the state if your inner loop is processing
    // the samples and the outer loop is handling the channels.
    // Alternatively, you can process the samples with the channels
    // interleaved by keeping the same state.
    for (int channel = 0; channel < totalNumInputChannels; ++channel)
    {
        auto* channelData = buffer.getWritePointer (channel);

        // ..do something to the data...
    }
	*/
	
	buffer.clear();
	synth.renderNextBlock(buffer, midiMessages, 0, buffer.getNumSamples());
}

//==============================================================================
bool SmsynthAudioProcessor::hasEditor() const
{
    return true; // (change this to false if you choose to not supply an editor)
}

juce::AudioProcessorEditor* SmsynthAudioProcessor::createEditor()
{
    return new SmsynthAudioProcessorEditor (*this);
}

//==============================================================================
void SmsynthAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    // You should use this method to store your parameters in the memory block.
    // You could do that either as raw data, or use the XML or ValueTree classes
    // as intermediaries to make it easy to save and load complex data.
	auto currState = state.copyState();
	std::unique_ptr<juce::XmlElement> xml(currState.createXml());
	xml->setAttribute("sourcePath", sourcePath);
	xml->setAttribute("fitPath", fitPath);
	xml->setAttribute("configPath", configPath);
	copyXmlToBinary(*xml, destData);
}

void SmsynthAudioProcessor::setStateInformation (const void* data, int sizeInBytes)
{
    // You should use this method to restore your parameters from this memory block,
    // whose contents will have been created by the getStateInformation() call.
	std::unique_ptr<juce::XmlElement> xml(getXmlFromBinary(data, sizeInBytes));
	if (xml.get() != nullptr) {
		if (xml->hasTagName(state.state.getType())) {
			state.replaceState(juce::ValueTree::fromXml(*xml));
			configPath = xml->getStringAttribute("configPath");
			sourcePath = xml->getStringAttribute("sourcePath");
			fitPath = xml->getStringAttribute("fitPath");
			juce::StringArray path;
			path.add(configPath);
			loadConfig(path);
		}
	}
}

void SmsynthAudioProcessor::clearMap()
{
	sample_map.clear();
}

void SmsynthAudioProcessor::addSample(int pitch, int vel, juce::AudioBuffer<float>* sample)
{
	sample_map.push_back(MappedSample());
	auto msample = &(sample_map.back());
	msample->pitch = pitch;
	msample->vel = vel;
	msample->sample.reset(sample);
}

void SmsynthAudioProcessor::loadConfig(const juce::StringArray& files)
{
	auto file = juce::File(files[0]);
	if (!file.existsAsFile()) return;

	juce::FileInputStream inStream(file);
	if (!inStream.openedOk()) return;

	clearMap();
	configPath = files[0];

	while (!inStream.isExhausted()) {
		auto line = inStream.readNextLine();
		juce::StringArray props;

		props.addTokens(line, ",", "");
		if (props.size() < 3) continue;

		auto audio_file = props[0];
		double pitch = juce::CharacterFunctions::getDoubleValue(props[1].begin());
		int vel = (int)juce::CharacterFunctions::getDoubleValue(props[2].begin());

		readAudio(file.getSiblingFile(audio_file), pitch, vel);
	}
}

void SmsynthAudioProcessor::readAudio(juce::File file, double pitch, int vel)
{
	juce::AudioFormatManager formatManager;
	formatManager.registerBasicFormats();
	auto reader = formatManager.createReaderFor(file);
	auto buffer = new juce::AudioBuffer<float>(2, reader->lengthInSamples);
	reader->read(buffer, 0, reader->lengthInSamples, 0, true, true);
	addSample(pitch, vel, buffer);
	delete reader;
}

void SmsynthAudioProcessor::setSource(const juce::StringArray& files)
{
	sourcePath = files[0];
}

void SmsynthAudioProcessor::setFit(const juce::StringArray& files)
{
	fitPath = files[0];
}

void SmsynthAudioProcessor::makeConfig(const juce::StringArray& files)
{
	auto gens = (juce::AudioParameterInt*)state.getParameter("gens");
	auto mut = (juce::AudioParameterFloat*)state.getParameter("mut");
	auto elite = (juce::AudioParameterFloat*)state.getParameter("elite");
	auto varMut = (juce::AudioParameterFloat*)state.getParameter("varMut");

	juce::FileChooser chooser("Save sequencer model as...");
	if (chooser.browseForFileToSave(true)) {
		DBG("Selected file successfuly!");
		auto saveFile = chooser.getResult().getFullPathName();
		auto openFile = files[0];
		auto fitFile = fitPath;
		auto smconfig = juce::File::getSpecialLocation(juce::File::SpecialLocationType::currentExecutableFile)
			.getSiblingFile("utils").getChildFile("smconfig.exe");

		juce::StringArray args;
		args.add(smconfig.getFullPathName());
		args.add("synth");
		args.add(openFile);
		args.add(saveFile);
		args.add(fitFile);
		args.add(juce::String(*gens));
		args.add(juce::String(*mut));
		args.add(juce::String(*elite));
		args.add(juce::String(*varMut));

		juce::ChildProcess config;
		if (config.start(args)) {
			DBG("Started config process successfuly!");
			config.waitForProcessToFinish(60e3);

			if (config.getExitCode() == 0) {
				juce::StringArray configFileArr;
				configFileArr.add(saveFile);
				loadConfig(configFileArr);
			}
			else {
				sourcePath = config.readAllProcessOutput();
			}
		}
		DBG("Child process done...");
	}
}

//==============================================================================
// This creates new instances of the plugin..
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new SmsynthAudioProcessor();
}
