import time

# complex_computation() simulates a slow function.
# time.sleep(n) causes the program to pause for n seconds.
# In real life, this might be a call to a database, or a 
# request to another web service
def complex_computation(a,b):
    computation = a + b
    time.sleep(.5)
    return computation

## Improve the cached_computation() function below so that 
## it caches results after computing them for the first time
## so future calls to the function using the same inputs
## are faster
CACHE = {}  # empty dictionary
cache_hits = 0
def cache_computation(a,b):
    global cache_hits
    global CACHE
    if CACHE.get((a,b),False):
        cache_hits=cache_hits+1
        return CACHE[(a,b)]
    if CACHE.get((b,a),False):
        cache_hits=cache_hits+1
        return CACHE[(b,a)]
    val = complex_computation(a,b)
    CACHE[(a,b)]=val
    return val


# TEST code
start_time = time.time()
print (cache_computation(1,2))
print (cache_computation(2,3))
print (cache_computation(4,5))
print (cache_computation(1,2))   ## hit
print (cache_computation(6,7))
print (cache_computation(2,3))   ## hit
print (cache_computation(4,5))   ## hit
print (cache_computation(8,9))
print (cache_computation(2,1))   ## hit
print (cache_computation(5,4))   ## hit

print ('total time %f' % (time.time() - start_time))
print ('hits =', cache_hits)


