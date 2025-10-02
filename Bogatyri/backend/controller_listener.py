import subprocess

def write_params_file(path, update_time_seconds):
    millis = str(int(update_time_seconds * 1000))
    with open('params.txt', 'w') as f:
        f.write(millis)

    subprocess.run(['mpremote', 'cp', path, ':params.txt'])

def run_mpremote(update_time_seconds=1):
    write_params_file('params.txt', update_time_seconds)

    proc = subprocess.Popen(
        ['mpremote', 'run', 'D:\\DESKTOP\\DOCUMENTS\\GitLocal\\Bogatyri\\Bogatyri\\backend\\ble_device_tracker.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    try:
        for line in proc.stdout:
            print(line, end='')
    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()


if __name__ == "__main__":
	run_mpremote(0.1)