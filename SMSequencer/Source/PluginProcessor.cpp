/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin processor.

  ==============================================================================
*/

#include "PluginProcessor.h"
#include "PluginEditor.h"

//==============================================================================
SmsequencerAudioProcessor::SmsequencerAudioProcessor()
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
	state(*this, nullptr, juce::Identifier("SMSequencer"),
	{
		std::make_unique<juce::AudioParameterBool>("chkPitch", "Check Pitch", true),
		std::make_unique<juce::AudioParameterBool>("chkVelocity", "Check Velocity", false),
		std::make_unique<juce::AudioParameterBool>("chkDuration", "Check Duration", false),
		std::make_unique<juce::AudioParameterInt>("chainLevel", "Chain Level", 1, 10, 3),
		std::make_unique<juce::AudioParameterInt>("pitchShift", "Pitch Shift", -36, 36, 0),
		std::make_unique<juce::AudioParameterFloat>("staccato", "Staccato", -1.0, 1.0, 0.0),
		std::make_unique<juce::AudioParameterFloat>("xVelocity", "Velocity Mult", 0.1, 3.0, 1.0),
		std::make_unique<juce::AudioParameterFloat>("xDuration", "Duration Mult", 0.1, 3.0, 1.0),
		std::make_unique<juce::AudioParameterInt>("minOctave", "Min Octave", -1, 6, -1),
		std::make_unique<juce::AudioParameterInt>("maxOctave", "Max Octave", -1, 6, 6),
		std::make_unique<juce::AudioParameterInt>("velocity", "Velocity", 0, 127, 0),
		std::make_unique<juce::AudioParameterFloat>("duration", "Duration", 0.0, 5.0, 0.0),
		std::make_unique<juce::AudioParameterBool>("arp", "Arpeggio", false)
	})
{
	modelPath = "";

	chkPitch = (juce::AudioParameterBool*) state.getParameter("chkPitch");
	chkVelocity = (juce::AudioParameterBool*) state.getParameter("chkVelocity");
	chkDuration = (juce::AudioParameterBool*) state.getParameter("chkDuration");
	arp = (juce::AudioParameterBool*) state.getParameter("arp");

	chainLevel = (juce::AudioParameterInt*) state.getParameter("chainLevel");
	
	pitchShift = (juce::AudioParameterInt*) state.getParameter("pitchShift");
	staccatto = (juce::AudioParameterFloat*) state.getParameter("staccato");
	xVelocity = (juce::AudioParameterFloat*) state.getParameter("xVelocity");
	xDuration = (juce::AudioParameterFloat*) state.getParameter("xDuration");

	minOctave = (juce::AudioParameterInt*) state.getParameter("minOctave");
	maxOctave = (juce::AudioParameterInt*) state.getParameter("maxOctave");
	velocity = (juce::AudioParameterInt*) state.getParameter("velocity");
	duration = (juce::AudioParameterFloat*) state.getParameter("duration");
}

SmsequencerAudioProcessor::~SmsequencerAudioProcessor()
{
}

//==============================================================================
const juce::String SmsequencerAudioProcessor::getName() const
{
    return JucePlugin_Name;
}

bool SmsequencerAudioProcessor::acceptsMidi() const
{
   #if JucePlugin_WantsMidiInput
    return true;
   #else
    return false;
   #endif
}

bool SmsequencerAudioProcessor::producesMidi() const
{
   #if JucePlugin_ProducesMidiOutput
    return true;
   #else
    return false;
   #endif
}

bool SmsequencerAudioProcessor::isMidiEffect() const
{
   #if JucePlugin_IsMidiEffect
    return true;
   #else
    return false;
   #endif
}

double SmsequencerAudioProcessor::getTailLengthSeconds() const
{
    return 0.0;
}

int SmsequencerAudioProcessor::getNumPrograms()
{
    return 1;   // NB: some hosts don't cope very well if you tell them there are 0 programs,
                // so this should be at least 1, even if you're not really implementing programs.
}

int SmsequencerAudioProcessor::getCurrentProgram()
{
    return 0;
}

void SmsequencerAudioProcessor::setCurrentProgram (int index)
{
}

const juce::String SmsequencerAudioProcessor::getProgramName (int index)
{
    return {};
}

void SmsequencerAudioProcessor::changeProgramName (int index, const juce::String& newName)
{
}

//==============================================================================
void SmsequencerAudioProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
{
    // Use this method as the place to do any pre-playback
    // initialisation that you need..
	time = 0;
	sampRate = sampleRate;
	lastNote = -1;
	currDur = 0;
	legatoBuffer = -1;
	chord.clear();
}

void SmsequencerAudioProcessor::releaseResources()
{
    // When playback stops, you can use this as an opportunity to free up any
    // spare memory, etc.
}

#ifndef JucePlugin_PreferredChannelConfigurations
bool SmsequencerAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
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

void SmsequencerAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
{
	juce::AudioPlayHead::CurrentPositionInfo info;
	getPlayHead()->getCurrentPosition(info);

	for each (auto data in midiMessages) {
		auto msg = data.getMessage();
		if (msg.isNoteOn()) {
			chord.push_back(msg.getNoteNumber());
		}
		else if (msg.isNoteOff()) {
			auto it = std::find(chord.begin(), chord.end(), msg.getNoteNumber());
			if (it != chord.end()) chord.erase(it);
		}
		else if (msg.isAllNotesOff()) {
			chord.clear();
		}
	}

	midiMessages.clear();

	if (model.size() > 0 && (!(*arp) || chord.size() > 0)) {
		auto nSamps = buffer.getNumSamples();
		auto noteDur = static_cast<int>(std::max(std::ceil(currDur * sampRate), 1.0));
		auto offset = juce::jlimit(0, nSamps, noteDur - time);

		if ((time + nSamps) >= noteDur) {
			auto note = getNextNote();

			if (*staccatto <= 0 && lastNote > -1) {
				midiMessages.addEvent(juce::MidiMessage::noteOff(1, lastNote), offset);
				lastNote = -1;
			}
			else if (legatoBuffer > -1) {
				if (lastNote > -1)
					midiMessages.addEvent(juce::MidiMessage::noteOff(1, lastNote), offset);
				lastNote = legatoBuffer;
				legatoBuffer = -1;
			}

			int v = (*velocity > 0) ? *velocity : (note.velocity * (*xVelocity));
			double d = (*duration > 0) ? *duration : (note.duration * (*xDuration));
			int p = note.pitch + (*pitchShift);
			if (p < (*minOctave + 1) * 12) p = (p % 12) + ((*minOctave + 1) * 12);
			if (p > (*maxOctave + 1) * 12) p = (p % 12) + ((*maxOctave + 1) * 12);

			if (*arp) {
				auto sDist = -1;
				auto np = p;
				for each (auto cp in chord) {
					auto dist = std::abs(cp - p);
					if (sDist < 0 || dist < sDist) {
						sDist = dist;
						np = cp;
					}
				}
				p = np;
			}

			midiMessages.addEvent(juce::MidiMessage::noteOn(1, p, juce::uint8(v)), offset);
			if (*staccatto <= 0.0) lastNote = p;
			else legatoBuffer = p;
			currDur = d;
		}
		else if (*staccatto < 0 && lastNote > -1 && (time + nSamps) >= (1.0 + *staccatto) * noteDur) {
			midiMessages.addEvent(juce::MidiMessage::noteOff(1, lastNote), offset);
			lastNote = -1;
		}
		else if (*staccatto > 0 && legatoBuffer > -1 && (time + nSamps) >= *staccatto * noteDur) {
			if (lastNote > -1)
				midiMessages.addEvent(juce::MidiMessage::noteOff(1, lastNote), offset);
			lastNote = legatoBuffer;
			legatoBuffer = -1;
		}

		time = (time + nSamps) % noteDur;
	}
}

//==============================================================================
bool SmsequencerAudioProcessor::hasEditor() const
{
    return true; // (change this to false if you choose to not supply an editor)
}

juce::AudioProcessorEditor* SmsequencerAudioProcessor::createEditor()
{
    return new SmsequencerAudioProcessorEditor (*this, state);
}

//==============================================================================
void SmsequencerAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    // You should use this method to store your parameters in the memory block.
    // You could do that either as raw data, or use the XML or ValueTree classes
    // as intermediaries to make it easy to save and load complex data.
	auto currState = state.copyState();
	std::unique_ptr<juce::XmlElement> xml(currState.createXml());
	xml->setAttribute("modelPath", modelPath);
	copyXmlToBinary(*xml, destData);
}

void SmsequencerAudioProcessor::setStateInformation (const void* data, int sizeInBytes)
{
    // You should use this method to restore your parameters from this memory block,
    // whose contents will have been created by the getStateInformation() call.
	std::unique_ptr<juce::XmlElement> xml(getXmlFromBinary(data, sizeInBytes));
	if (xml.get() != nullptr) {
		if (xml->hasTagName(state.state.getType())) {
			state.replaceState(juce::ValueTree::fromXml(*xml));
			juce::StringArray path;
			path.add(xml->getStringAttribute("modelPath"));
			loadSeq(path);
		}
	}
}

void SmsequencerAudioProcessor::clearModel()
{
	model.clear();
}

void SmsequencerAudioProcessor::addEntryToModel()
{
	model.push_back(std::vector<Note>());
}

void SmsequencerAudioProcessor::addNoteToModel(int pitch, int velocity, double duration)
{
	model.back().push_back(Note{pitch, velocity, duration});
}

Note SmsequencerAudioProcessor::getNextNote()
{
	std::vector<Note> possibilities;

	for (auto entry : model) {
		int entry_i = entry.size() - 2;
		int history_i = history.size() - 1;

		while (entry_i >= 0 && history_i >= 0) {
			auto note1 = entry[entry_i];
			auto note2 = history[history_i];

			auto pitch_ch = (! *chkPitch) || (note1.pitch == note2.pitch);
			auto vel_ch = (! *chkVelocity) || (note1.velocity == note2.velocity);
			auto dur_ch = (! *chkDuration) || (note1.duration == note2.duration);

			if (pitch_ch && vel_ch && dur_ch) {
				possibilities.push_back(entry.back());
			}

			entry_i--;
			history_i--;
		}
	}

	if (possibilities.size() > 0) {
		auto note = possibilities[std::rand() % possibilities.size()];
		history.push_back(note);
		while (history.size() > *chainLevel) {
			history.erase(history.begin());
		}
		return note;
	}
	
	DBG("Found no note, choosing random one.");

	auto entry = model[std::rand() % model.size()];
	auto note = entry[std::rand() % entry.size()];
	history.push_back(note);
	while (history.size() > *chainLevel) {
		history.erase(history.begin());
	}

	return note;
}

//==============================================================================
// This creates new instances of the plugin..
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new SmsequencerAudioProcessor();
}

void SmsequencerAudioProcessor::loadSeq(const juce::StringArray& files)
{
	auto file = juce::File(files[0]);
	if (!file.existsAsFile()) return;

	juce::FileInputStream inStream(file);
	if (!inStream.openedOk()) return;

	clearModel();

	while (!inStream.isExhausted()) {
		auto line = inStream.readNextLine();
		addEntryToModel();

		juce::StringArray noteTxts;
		noteTxts.addTokens(line, ";", "");

		for (auto noteTxt : noteTxts) {
			DBG(noteTxt);
			juce::StringArray noteProps;
			noteProps.addTokens(noteTxt, ",", "");
			if (noteProps.size() < 3) continue;

			int pitch = juce::CharacterFunctions::getIntValue<int>(noteProps[0].begin());
			int velocity = juce::CharacterFunctions::getIntValue<int>(noteProps[1].begin());
			double duration = juce::CharacterFunctions::getDoubleValue(noteProps[2].begin());
			addNoteToModel(pitch, velocity, duration);
		}
	}

	modelPath = file.getFullPathName();
}

void SmsequencerAudioProcessor::loadAudio(const juce::StringArray& files)
{
	juce::FileChooser chooser("Save sequencer model as...");
	if (chooser.browseForFileToSave(true)) {
		DBG("Selected file successfuly!");
		auto saveFile = chooser.getResult().getFullPathName();
		auto openFile = files[0];
		auto smconfig = juce::File::getSpecialLocation(juce::File::SpecialLocationType::currentExecutableFile)
			.getSiblingFile("utils").getChildFile("smconfig.exe");

		juce::StringArray args;
		args.add(smconfig.getFullPathName());
		args.add("sequencer");
		args.add(openFile);
		args.add(saveFile);
		args.add("10");

		juce::ChildProcess config;
		if (config.start(args)) {
			DBG("Started config process successfuly!");
			config.waitForProcessToFinish(60e3);

			if (config.getExitCode() == 0) {
				juce::StringArray configFileArr;
				configFileArr.add(saveFile);
				loadSeq(configFileArr);
			}
		}
		DBG("Child process done...");
	}
}
