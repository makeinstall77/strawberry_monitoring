# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)
import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
import senko

OTA = senko.Senko(
  user="makeinstall77", # Required
  repo="strawberry_monitoring", # Required
  branch="main", # Optional: Defaults to "master"
  working_dir="app", # Optional: Defaults to "app"
  files = ["boot.py", "main.py"]
)

#import webrepl
#webrepl.start()
gc.collect()
