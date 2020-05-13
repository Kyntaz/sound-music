# Link the UI with the SoundMusic python backend.
import SoundMusic as sm
import eel
import os.path
import tkinter as tk
import tkinter.filedialog
import traceback as tb
import time

@eel.expose
def manipulators():
    simp = [m.__name__ for m in sm.manipulators.as_list]
    comp = [m.__name__ for m in sm.manipulators.compound.as_list]
    return (simp, comp)

@eel.expose
def renderMakeRand(filePath, complexity):
    print(f"Starting work on {filePath}...")
    try:
        manip = sm.makerand.make_random_manip(
            sm.manipulators.as_list,
            sm.manipulators.compound.as_list,
            complexity
        )
        source = sm.sound.SoundObject.load(filePath)
        out = manip.do([source])
        out_r = sm.render.render_audio(out, fade=3, pretty=True)
        r_path = f"temp/audio-{time.time()}.wav"
        path = os.path.join(eel.root_path, r_path)
        out_r.write(path)
    except:
        tb.print_exc()
        return ""
    print("Done!")
    return r_path

@eel.expose
def renderCustom(filePath, manipRep):
    print("Building manipulator.")
    try:
        manip_dict = {}
        for manip in sm.manipulators.as_list:
            manip_dict[manip.__name__] = manip
        comp_dict = {}
        for comp in sm.manipulators.compound.as_list:
            comp_dict[comp.__name__] = comp
        manip = _build_manip(manipRep, manip_dict, comp_dict)
        source = sm.sound.SoundObject.load(filePath)
        print("Rendering...")
        out = manip.do([source])
        out_r = sm.render.render_audio(out, fade=3, pretty=True)
        r_path = f"temp/audio-{time.time()}.wav"
        path = os.path.join(eel.root_path, r_path)
        out_r.write(path)
    except:
        tb.print_exc()
        return ""
    print("Done!")
    return r_path

def _build_manip(manipRep, manip_dict, comp_dict):
    if isinstance(manipRep, str):
        return manip_dict[manipRep]()
    else:
        manips = [_build_manip(mr, manip_dict, comp_dict) for mr in manipRep[1:]]
        return comp_dict[manipRep[0]](manips)

@eel.expose
def getFile():
    root = tk.Tk()
    root.withdraw()
    f = tk.filedialog.askopenfilename(parent=root)
    root.destroy()
    return f