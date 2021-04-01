# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)
import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
import senko
print("booting")

# OTA = senko.Senko(
    # user="makeinstall77", # Required
  # repo="strawberry_monitoring", # Required
  # branch="main", # Optional: Defaults to "master"
  # working_dir="app", # Optional: Defaults to "app"
  # files = ["boot.py", "main.py"]
# )

# try:
    # # if OTA.fetch():
        # # print("A newer version is available!")
    # if OTA.update():
        # print("Updated to the latest version! Rebooting...")
        # machine.reset()
    # else:
        # print("Up to date!")
# except:
    # print ("error while checking new version")
    # pass

#import webrepl
#webrepl.start()
gc.collect()
print("success boot")