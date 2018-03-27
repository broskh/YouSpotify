import sys
import time

debug = False
logFile = "YouSpotify.log"


# Print the debug string in console and in log file if debug value is "True"
def print_debug(tag, string):
    if debug:
        tag = "DEBUG//" + tag
        print_console(tag, string)


# Return the string in log form
def log_string(tag, string):
    return output_string(tag, '[{}] {}\n'.format(time.strftime('%I:%M:%S'), string))


# Print the log string in the log file
def print_log(tag, string):
    of = open(logFile, 'w')
    of.write(log_string(tag, string))
    of.close()


# Print the output string in console and in log file
def print_console(tag, string):
    sys.stdout.buffer.write(output_string(tag, string).encode(sys.stdout.encoding, errors='replace'))
    sys.stdout.flush()
    print_log(tag, string)


# Return the output string in the output form
def output_string(tag, string):
    return (tag + " - " + string)


# Set debug value "True"
def enable_debug():
    global debug
    debug = True
