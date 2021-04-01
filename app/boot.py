# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)
import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
import senko

print("start boot")


#import webrepl
#webrepl.start()
gc.collect()
print("success boot")