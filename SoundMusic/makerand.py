import random
from SoundMusic import dataset
import SoundMusic as sm
import traceback as tb

def make_random_manip(sManips, cManips, complexity):
    random.seed()
    manip = (random.choice(sManips))()
    for _ in range(complexity):
        manip2 = (random.choice(sManips))()
        connector = random.choice(cManips)
        manip = connector(random.choice((
            [manip, manip2],
            [manip2, manip]
        )))
    manip.tweak(1.0)
    return manip

def batch_experiment(n_sources, n_trials, complexity, s_manips, c_manips, name):
    print("Starting batch job...")
    for s_i in range(1, n_sources + 1):
        random.seed()
        source_id = random.choice(dataset.get())
        print(f"Reading source {s_i}/{n_sources}: {source_id}")
        source = dataset.read(source_id)
        for i in range(1, n_trials + 1):
            print(f"Trial {i}/{n_trials} for source {s_i}/{n_sources} ({source_id}) starting.")
            try:
                print("Generating manipulator.")
                manip = make_random_manip(s_manips, c_manips, complexity)
                print("Executing manipulator.")
                res = manip.do([source])
                print("Rendering result.")
                res = sm.render.render_audio(res, fade=3, pretty=True)
                print("Writing result.")
                res.write(f"output/{name}_{source_id}_t{i}.wav")
            except KeyboardInterrupt:
                print("Batch job interrupted by user.")
                return
            except:
                tb.print_exc()
                print("Failed...")
    print("Batch job done!")