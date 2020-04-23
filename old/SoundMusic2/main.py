import traceback
import commands
import context
import audio
import notes

def main():
    print("Welcome to SoundMusic!\nHave lots of fun!")

    # Initialize some stuff:
    audio.init_dataset()
    notes.init_midis()

    # Main loop:
    while True:
        try:
            s_command = input("$ ")
            if s_command == "exit": break
            if len(s_command) == 0: continue
            command = parse_command(s_command)
            exec_command(command)
        except KeyboardInterrupt: print(); break
        except: traceback.print_exc()
    
    print("Bye bye!")

def parse_command(s_command):
    return s_command.split(" ")

def exec_command(command):
    try:
        action, *args = command
        args = context.apply(args)
        commands.do(action, args)
    except commands.CommandNotFoundError:
        print(f"\"{action}\" command not found.")
    except TypeError:
        print(f"Wrong arguments for \"{action}\" command.")
        traceback.print_exc()

if __name__ == "__main__": main()