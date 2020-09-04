#include "MappedSampleVoice.h"
#include "PluginProcessor.h"

MappedSampleVoice::MappedSampleVoice(SmsynthAudioProcessor* processor) :
	juce::SynthesiserVoice(),
	hiFilter(),
	loFilter(),
	owner(processor)
{
	juce::ADSR::Parameters params;
	params.attack = 0.1f;
	params.decay = 0.1f;
	params.sustain = 1.0f;
	params.release = 1.0f;
	adsr.setSampleRate(getSampleRate());
	adsr.setParameters(params);
	resetGrains();
}

bool MappedSampleVoice::canPlaySound(juce::SynthesiserSound* sound) {
	return dynamic_cast<MappedSamplerSound*>(sound) != nullptr;
}

// Inherited via SynthesiserVoice

void MappedSampleVoice::startNote(int midiNoteNumber, float velocity, juce::SynthesiserSound* sound, int currentPitchWheelPosition) {
	float targetPitch = pow(2.0f, (midiNoteNumber - 69.0f) / 12.0f) * 440.0f;
	if (curr_pitch == 0) curr_pitch = midiNoteNumber;

	juce::ADSR::Parameters params;
	params.attack = *(juce::AudioParameterFloat*)(owner->getState()->getParameter("atk"));
	params.decay = *(juce::AudioParameterFloat*)(owner->getState()->getParameter("decay"));
	params.sustain = *(juce::AudioParameterFloat*)(owner->getState()->getParameter("sus"));
	params.release = *(juce::AudioParameterFloat*)(owner->getState()->getParameter("rel"));
	adsr.setParameters(params);
	if (!playing)
		adsr.noteOn();

	spec.sampleRate = getSampleRate();
	spec.maximumBlockSize = owner->currBlockSize;
	spec.numChannels = 2;
	hiFilter.prepare(spec);
	loFilter.prepare(spec);

	curr_vel = velocity;
	playing = true;
}

void MappedSampleVoice::stopNote(float velocity, bool allowTailOff) {
	if (!allowTailOff) {
		DBG("End Note");
		clearCurrentNote();
	}
	else {
		adsr.noteOff();
		playing = false;
	}
}

void MappedSampleVoice::pitchWheelMoved(int newPitchWheelValue) {
	curr_shift = (float)newPitchWheelValue / (float)0x4000;
}

void MappedSampleVoice::controllerMoved(int controllerNumber, int newControllerValue) {

}

void MappedSampleVoice::renderNextBlock(juce::AudioBuffer<float>& outputBuffer, int startSample, int numSamples) {
	auto sound = (MappedSamplerSound*)(getCurrentlyPlayingSound().get());
	if (sound == nullptr || sound->sample_map->size() <= 0) {
		return;
	}

	curr_pitch = std::abs(curr_pitch + (float)getCurrentlyPlayingNote()) / 2.0f;
	DBG(curr_pitch);
	float targetNote = curr_pitch + curr_shift;
	MappedSample* map_lo = nullptr;
	double hiDist_lo = 10e6;
	MappedSample* map_hi = nullptr;
	double hiDist_hi = 10e6;
	for (int i = 0; i < sound->sample_map->size(); i++) {
		auto a_map = &sound->sample_map->at(i);
		auto pitch = a_map->pitch;
		auto vel = a_map->vel;

		double dist = std::abs(pitch - targetNote);
		if (pitch < targetNote && dist < hiDist_lo) {
			map_lo = a_map;
			hiDist_lo = dist;
		}
		else if (pitch >= targetNote && dist < hiDist_hi) {
			map_hi = a_map;
			hiDist_hi = dist;
		}
	}

	if (map_lo == nullptr) map_lo = map_hi;
	if (map_hi == nullptr) map_hi = map_lo;

	float baseNote = map_lo->pitch;
	float basePitch = pow(2.0f, (baseNote - 69.0f) / 12.0f) * 440.0f;
	float targetPitch = pow(2.0f, (targetNote - 69.0f) / 12.0f) * 440.0f;
	double inc_lo = targetPitch / basePitch;
	auto sample_lo = map_lo->sample.get();

	baseNote = map_hi->pitch;
	basePitch = pow(2.0f, (baseNote - 69.0f) / 12.0f) * 440.0f;
	double inc_hi = targetPitch / basePitch;
	auto sample_hi = map_hi->sample.get();
	bool ping = *(juce::AudioParameterBool*)(owner->getState()->getParameter("ping"));

	int curr_grains = *(juce::AudioParameterInt*)(owner->getState()->getParameter("grains"));
	for (int grain = 0; grain < curr_grains; grain++) {
		for (int i = 0; i < numSamples; i++) {
			int idx1_lo = (int)curr_sample_lo[grain];
			int idx2_lo = idx1_lo + 1;
			double r2_lo = curr_sample_lo[grain] - (double)idx1_lo;
			double r1_lo = 1.0 - r2_lo;
			
			if (ping && (idx1_lo / sample_lo->getNumSamples()) % 2 == 1)
				idx1_lo = sample_lo->getNumSamples() - 1 - (idx1_lo % sample_lo->getNumSamples());
			if (ping && (idx2_lo / sample_lo->getNumSamples()) % 2 == 1)
				idx2_lo = sample_lo->getNumSamples() - 1 - (idx2_lo % sample_lo->getNumSamples());

			auto s1_lo = sample_lo->getSample(0, idx1_lo % sample_lo->getNumSamples());
			auto s2_lo = sample_lo->getSample(0, idx2_lo % sample_lo->getNumSamples());
			float s_lo = r1_lo * s1_lo + r2_lo * s2_lo;

			int idx1_hi = (int)curr_sample_hi[grain];
			int idx2_hi = idx1_hi + 1;
			double r2_hi = curr_sample_hi[grain] - (double)idx1_hi;
			double r1_hi = 1.0 - r2_hi;

			if (ping && (idx1_hi / sample_hi->getNumSamples()) % 2 == 1)
				idx1_hi = sample_hi->getNumSamples() - 1 - (idx1_hi % sample_hi->getNumSamples());
			if (ping && (idx2_hi / sample_hi->getNumSamples()) % 2 == 1)
				idx2_hi = sample_hi->getNumSamples() - 1 - (idx2_hi % sample_hi->getNumSamples());

			auto s1_hi = sample_hi->getSample(0, idx1_hi % sample_hi->getNumSamples());
			auto s2_hi = sample_hi->getSample(0, idx2_hi % sample_hi->getNumSamples());
			float s_hi = r1_hi * s1_hi + r2_hi * s2_hi;

			float p = hiDist_lo / (hiDist_hi + hiDist_lo);

			for (int j = 0; j < outputBuffer.getNumChannels(); j++)
				outputBuffer.addSample(j, startSample + i,
					(s_lo * (1.0f - p) + s_hi * p) * curr_vel * (loQ * hiQ * 9.0f + 1.0f) / curr_grains);
			curr_sample_lo[grain] += inc_lo;
			curr_sample_hi[grain] += inc_hi;
		}
	}

	hiQ = *(juce::AudioParameterFloat*)(owner->getState()->getParameter("hiPass"));
	loQ = *(juce::AudioParameterFloat*)(owner->getState()->getParameter("loPass"));
	if (hiQ > 0.0f) {
		auto bw = (1.01 - hiQ) * 5e2;
		auto q = targetPitch / bw;
		auto f = targetPitch - bw;
		if (f > 0) {
			*hiFilter.state = *juce::dsp::IIR::Coefficients<float>::makeHighPass(getSampleRate(), f);
			hiFilter.reset();
		}
	}
	if (loQ > 0.0f) {
		auto bw = (1.01 - loQ) * 5e2;
		auto q = targetPitch / bw;
		*loFilter.state = *juce::dsp::IIR::Coefficients<float>::makeLowPass(getSampleRate(), targetPitch + bw);
		loFilter.reset();
	}

	juce::dsp::AudioBlock<float> block(outputBuffer);
	if (hiQ > 0) {
		hiFilter.process(juce::dsp::ProcessContextReplacing<float>(block));
	}
	if (loQ > 0) {
		loFilter.process(juce::dsp::ProcessContextReplacing<float>(block));
	}

	adsr.applyEnvelopeToBuffer(outputBuffer, startSample, numSamples);
	if (!adsr.isActive()) {
		DBG("End Note");
		clearCurrentNote();
		playing = false;
	}
}

void MappedSampleVoice::resetGrains() {
	for (int i = 0; i < n_grains; i++) {
		curr_sample_hi[i] = rand() % 100000;
		curr_sample_lo[i] = rand() % 100000;
	}
}
