import stifler_ds18 as temp_sens
import asyncio
import time
# temp_sens.init_config()

async def print_temp():
    temp_sens.init_config()
    while True:        
        temp = temp_sens.get_temp("qq")
        print(temp)                   
        await asyncio.sleep(0.2)
        
                        
asyncio.run(print_temp())
