from magenta.models.nsynth.wavenet.fastgen import tf, load_fastgen_nsynth, Config, np, generate_audio_sample

# A variation on the <synthesize> function from https://github.com/magenta/magenta/blob/36b050d3e3bed4381da5453cbec171affb13083f/magenta/models/nsynth/wavenet/fastgen.py#L173
# This one returns the samples instead of writing them to a wav file.
def synth_samples(encodings,
               checkpoint_path="model.ckpt-200000"):
  """Synthesize audio from an array of encodings.
  Args:
    encodings: Numpy array with shape [batch_size, time, dim].
    save_paths: Iterable of output file names.
    checkpoint_path: Location of the pretrained model. [model.ckpt-200000]
    samples_per_save: Save files after every amount of generated samples.
  """
  session_config = tf.ConfigProto(allow_soft_placement=True)
  session_config.gpu_options.allow_growth = True
  with tf.Graph().as_default(), tf.Session(config=session_config) as sess:
    net = load_fastgen_nsynth(batch_size=encodings.shape[0])
    saver = tf.train.Saver()
    saver.restore(sess, checkpoint_path)

    # Get lengths
    batch_size, encoding_length, _ = encodings.shape
    hop_length = Config().ae_hop_length
    total_length = encoding_length * hop_length

    # initialize queues w/ 0s
    sess.run(net["init_ops"])

    # Regenerate the audio file sample by sample
    audio_batch = np.zeros(
        (batch_size, total_length), dtype=np.float32)
    audio = np.zeros([batch_size, 1])

    for sample_i in range(total_length):
      encoding_i = sample_i // hop_length
      audio = generate_audio_sample(sess, net,
                                    audio, encodings[:, encoding_i, :])
      audio_batch[:, sample_i] = audio[:, 0]
      if sample_i % 100 == 0:
        tf.logging.info("Sample: %d" % sample_i)

    return audio_batch
