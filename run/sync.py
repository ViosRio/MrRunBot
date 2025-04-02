import os
import time
import subprocess

RUN_DIRECTORY = "run"

CHECK_INTERVAL = 10

def check_and_run_files():
    while True:
        # 
        for user_folder in os.listdir(RUN_DIRECTORY):
            user_folder_path = os.path.join(RUN_DIRECTORY, user_folder)

            if os.path.isdir(user_folder_path):
                for file_name in os.listdir(user_folder_path):
                    file_path = os.path.join(user_folder_path, file_name)

                    # 
                    if file_name.endswith('.py') and os.path.isfile(file_path):
                        try:
                            # 
                            with open('running_files.txt', 'r') as f:
                                running_files = f.readlines()
                            running_files = [line.strip() for line in running_files]

                            if file_name not in running_files:
                                # 
                                subprocess.Popen(["python3", file_path])

                                # 
                                with open('running_files.txt', 'a') as f:
                                    f.write(f"{file_name}\n")
                                print(f"✅ {file_name} çalıştırıldı.")
                        except Exception as e:
                            print(f"⚠️ Hata oluştu: {e}")

        # 
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    check_and_run_files()
