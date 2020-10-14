#
# Base code to replace a Millenium Controller using a Raspberrypi 
# python3 code
#
import RPi.GPIO as GPIO
import time
import datetime
import csv

output_01 = 4 # BCM4, pin7, OUT-01, heater_control
output_02 = 17 # BCM17, pin11, OUT-02, livingroom_v3v_control 
output_03 = 27 # BCM27, pin13, OUT-03, bedroom_v3v_control
output_04 = 22 # BCM22, pin15, OUT-04, livingroom_pump_control
output_05 = 10 # BCM10, pin19, OUT-05, bedroom_pump_control
input_01 = 9 # BCM9, pin21, IN-01, xxx 
input_02 = 11 # BCM11, pin23, IN-02, yyy
input_03 = 5 # BCM5, pin29, IN-03, zzz

# Check period [jav]
period = 5 # Period in seconds
t = 0

door_hysteresis = False
door_count = 0
door_time = 2

pir_hysteresis = False
pir_count = 0
pir_time = 60
pir_time_begin = datetime.datetime.strptime('20:00', '%H:%M').time()
pir_time_end = datetime.datetime.strptime('08:00', '%H:%M').time()

command_file_str = '/home/pi/Projects/pi-millenium/command.csv'
# 
# Available commands
# test_heater
# reset
# automate_mode
#
command = ''
parameter = ''

test_count = 0
test_states = 10

test_heater_state = 'STATE_INIT'
test_heater_count = 0

#
# main_state's states
# ST_INIT
# ST_WAIT_ONE_MINUTE_01
# ST_READY
# ST_TURN_ON_HEATER
# ST_TURN_ON_V3V_LIVINGROOM
# ST_TURN_ON_V3V_BEDGROOM
# ST_TURN_ON_V3V_LIVINGROOM_BEDROOM
# ST_WAIT_ONE_MINUTE_02
# ST_TURN_ON_PUMP_LIVINGROOM
# ST_TURN_ON_PUMP_BEDROOM
# ST_TURN_ON_PUMP_LIVINGROOM_BEDROOM
# ST_HEATING_LIVINGROOM
# ST_HEATING_BEDROOM
# ST_HEATING_LIVINGROOM_BDEROOM
# ST_WAIT_ONE_MINUTE_03
# ST_TURN_OFF_V3V_LIVINGROOM
# ST_TURN_OFF_V3V_BEDROOM
# ST_TURN_OFF_V3V_LIVINGROOM_BEDROOM
# ST_TURN_OFF_HEATER
#
#
main_state = 'ST_INIT'
main_count = 0

bedroom_time_begin  = datetime.datetime.strptime('19:00', '%H:%M').time()
bedroom_time_end  = datetime.datetime.strptime('22:30', '%H:%M').time()
livingroom_time_begin  = datetime.datetime.strptime('18:00', '%H:%M').time()
livingroom_time_end  = datetime.datetime.strptime('22:30', '%H:%M').time()

livingroom_time = False
bedroom_time = False
livingroom_thermostat = False
bedroom_thermostat = False

# output_gpio[] definition 
# bit 0 = HEATER_CONTROL 
# bit 1 = LIVINGROOM_V3V_CONTROL 
# bit 2 = BEDROOM_V3V_CONTROL 
# bit 3 = LIVINGROOM_PUMP_CONTROL 
# bit 4 = BEDROOM_PUMP_CONTROL 
output_gpio = [GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH]

# input_gpio definition 
# bit 0 = input_01(IN-01) THERMOSTAT_LIVINGROOM
# bit 1 = input_02(IN-02) THERMOSTAT_BEDROOM
# bit 2 = input_03(IN-03) THERMOSTAT_KIT_CONFORT
# bit 3 = HEATER_CONTROL_ON (command.csv)
# bit 4 = HEATER_CONTROL_OFF (command.csv)
# bit 5 = LIVINGROOM_V3V_CONTROL_ON (command.csv)
# bit 6 = LIVINGROOM_V3V_CONTROL_OFF (command.csv)
# bit 7 = BEDROOM_V3V_CONTROL_ON (command.csv)
# bit 8 = BEDROOM_V3V_CONTROL_OFF (command.csv)
# bit 9 = LIVINGROOM_PUMP_CONTROL_ON (command.csv)
# bit 10 = LIVINGROOM_PUMP_CONTROL_OFF (command.csv)
# bit 11 = BEDROOM_PUMP_CONTROL_ON (command.csv)
# bit 12 = BEDROOM_PUMP_CONTROL_OFF (command.csv)
input_gpio = [GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW] 

def show_variables():
    global period
    global t
    global door_hyteresis
    global door_count
    global door_time
    global pir_hyteresis
    global pir_count
    global pir_time
    global pir_time_begin
    global pir_time_end
    global test_count
    global test_states
    global command
    global parameter
    global test_heater_state
    global test_heater_count
    global main_state
    global main_count 
    global livingroom_time
    global bedroom_time
    global livingroom_thermostat
    global bedroom_thermostat

    print(f'period={period}s, t={t}')
    print(f'door_hysteresis={door_hysteresis}, door_count={door_count}, door_time={door_time}')
    print(f'pir_hysteresis={pir_hysteresis}, pir_count={pir_count}, pir_time={pir_time}')
    print(f'pir_time_begin={pir_time_begin}, pir_time_end={pir_time_end}')
    print(f'test_count={test_count}, test_states={test_states}')
    print(f'command={command}, parameter={parameter}')
    print(f'main_state={test_heater_state}, main_count={main_count}')
    print(f'livingroom_time={livingroom_time}, bedroom_time={bedroom_time}')
    print(f'livingroom_thermostat={livingroom_thermostat}, bedroom_thermostat={bedroom_thermostat}')
    print(f'test_heater_state={test_heater_state}, test_heater_count={test_heater_count}')

    return 0

def init_gpio():
    # Initialize GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(output_01, GPIO.OUT) # GPIO assign mode
    GPIO.setup(output_02, GPIO.OUT) # GPIO assign mode
    GPIO.setup(output_03, GPIO.OUT) # GPIO assign mode
    GPIO.setup(output_04, GPIO.OUT) # GPIO assign mode
    GPIO.setup(output_05, GPIO.OUT) # GPIO assign mode
    GPIO.setup(input_01, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) # input with pull-down 
    GPIO.setup(input_02, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) # input with pull-down 
    GPIO.setup(input_03, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) # input with pull-down 

    return 0

def write_gpio():
    GPIO.output(output_01, output_gpio[0])
    GPIO.output(output_02, output_gpio[1])
    GPIO.output(output_03, output_gpio[2])
    GPIO.output(output_04, output_gpio[3])
    GPIO.output(output_05, output_gpio[4])

    return 0

def read_gpio():
    input_gpio[0] = GPIO.input(input_01)
    input_gpio[1] = GPIO.input(input_02)
    input_gpio[2] = GPIO.input(input_03)

    return 0


def read_command():
    global command_file_str
    global command
    global parameter

    with open(command_file_str, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        # Beta implementation. Only process one command per file!
        # Row fromat
        # written|read, who    , n --> input[n], value
        # w|r         , jav|dan, [3-12]        , 0|1
        # w|r         , jav|dan, test_heater   , livingroom|bedroom
        # w|r         , jav|dan, automate_mode , x
        # w|r         , jav|dan, reset         , x
        for row in csv_reader:
            print(f'{datetime.datetime.now()} raw_command=,{row}')
            if row[0] == 'r': # new command
                print(f'{datetime.datetime.now()} new command!')
                row[0] = 'w' # mark the command as done

            # Complete the automate_mode and reset commands [jav]
            if row[2] == 'automate_mode': # AUTOMATE_MODE (thermostat controller mode)
                print(f'{datetime.datetime.now()} command=AUTOMATE_MODE, {row[3]}')
                command = row[2]
                parameter = row[3]

            elif row[2] == 'reset': # RESET 
                print(f'{datetime.datetime.now()} command=RESET, {row[3]}')
                command = row[2]
                parameter = row[3]

            elif row[2] == 'test_heater': # TEST_HEATER (full cycle ON-10minutes-OFF)
                print(f'{datetime.datetime.now()} command=TEST_HEATER on {row[3]}')
                command = row[2]
                parameter = row[3]

            else:
                if int(row[2]) == 3: # HEATER_CONTROL_ON 
                    print(f'{datetime.datetime.now()} command=HEATER_CONTROL_ON,{row[3]}')
                    input_gpio[3] = int(row[3]) 

                elif int(row[2]) == 4: # HEATER_CONTROL_OFF 
                    print(f'{datetime.datetime.now()} command=HEATER_CONTROL_OFF,{row[3]}')
                    input_gpio[4] = int(row[3]) 

                if int(row[2]) == 5: # LIVINGROOM_V3V_CONTROL_ON 
                    print(f'{datetime.datetime.now()} command=LIVINGROOM_V3V_CONTROL_ON,{row[3]}')
                    input_gpio[5] = int(row[3]) 

                elif int(row[2]) == 6: # LIVINGROOM_V3V_CONTROL_OFF 
                    print(f'{datetime.datetime.now()} command=LIVINGROOM_V3V_CONTROL_OFF,{row[3]}')
                    input_gpio[6] = int(row[3]) 

                if int(row[2]) == 7: # BEDROOM_V3V_CONTROL_ON 
                    print(f'{datetime.datetime.now()} command=BEDROOM_V3V_CONTROL_ON,{row[3]}')
                    input_gpio[7] = int(row[3]) 

                elif int(row[2]) == 8: # BEDGROOM_V3V_CONTROL_OFF 
                    print(f'{datetime.datetime.now()} command=BEDROOM_V3V_CONTROL_OFF,{row[3]}')
                    input_gpio[8] = int(row[3]) 

                if int(row[2]) == 9: # LIVINGROOM_PUMP_CONTROL_ON 
                    print(f'{datetime.datetime.now()} command=LIVINGROOM_PUMP_CONTROL_ON,{row[3]}')
                    input_gpio[9] = int(row[3]) 

                elif int(row[2]) == 10: # LIVINGROOM_PUMP_CONTROL_OFF 
                    print(f'{datetime.datetime.now()} command=LIVINGROOM_PUMP_CONTROL_OFF,{row[3]}')
                    input_gpio[10] = int(row[3]) 

                if int(row[2]) == 11: # BEDROOM_PUMP_CONTROL_ON 
                    print(f'{datetime.datetime.now()} command=BEDROOM_PUMP_CONTROL_ON,{row[3]}')
                    input_gpio[11] = int(row[3]) 

                elif int(row[2]) == 12: # BEDGROOM_PUMP_CONTROL_OFF 
                    print(f'{datetime.datetime.now()} command=BEDROOM_PUMP_CONTROL_OFF,{row[3]}')
                    input_gpio[12] = int(row[3]) 

        line_count += 1
        
        print(f'{datetime.datetime.now()} Processed {line_count} lines')

        # Save a copy of the read content
        # check it - it doesn't work
        lines = list(csv_reader)
        print(f'{datetime.datetime.now()} Save lines= {lines}')
                
    with open(command_file_str, mode='w') as csv_file:
        print(f'{datetime.datetime.now()} Updating csv file')

        line_count = 0
        csv_writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
        for row in lines:
            csv_writer.writerow(row)
            line_count += 1

        print(f'{datetime.datetime.now()} Updated csv file with {line_count} lines')


    return 0


def status_gpio():
    global livingroom_time
    global bedroom_time
    global livingroom_thermostat
    global bedroom_thermostat
    
    print(f'{datetime.datetime.now()} input={input_gpio} output={output_gpio} t={t}')
    if command != '':
        print(f'{datetime.datetime.now()} command={command} parameter={parameter} livingroom={livingroom_time}, {livingroom_thermostat}, bedroom={bedroom_time}, {bedroom_thermostat}')

    return 0

def process_heater_control():

    if (input_gpio[3] == GPIO.HIGH):
        output_gpio[0] = GPIO.LOW
        print(f'{datetime.datetime.now()} HEATER_CONTROL_ON')

        #Reset the command
        input_gpio[3] = GPIO.LOW

    if (input_gpio[4] == GPIO.HIGH):
        output_gpio[0] = GPIO.HIGH
        print(f'{datetime.datetime.now()} HEATER_CONTROL_OFF')

        #Reset the command
        input_gpio[4] = GPIO.LOW

                
    return 0

def process_v3v_control():

    if (input_gpio[5] == GPIO.HIGH):
        output_gpio[1] = GPIO.LOW
        print(f'{datetime.datetime.now()} LIVINGROOM_V3V_CONTROL_ON')

        #Reset the command
        input_gpio[5] = GPIO.LOW

    if (input_gpio[6] == GPIO.HIGH):
        output_gpio[1] = GPIO.HIGH
        print(f'{datetime.datetime.now()} LIVINGROOM_V3V_CONTROL_OFF')

        #Reset the command
        input_gpio[6] = GPIO.LOW

    if (input_gpio[7] == GPIO.HIGH):
        output_gpio[2] = GPIO.LOW
        print(f'{datetime.datetime.now()} BEDROOM_V3V_CONTROL_ON')

        #Reset the command
        input_gpio[7] = GPIO.LOW

    if (input_gpio[8] == GPIO.HIGH):
        output_gpio[2] = GPIO.HIGH
        print(f'{datetime.datetime.now()} BEDGROOM_V3V_CONTROL_OFF')

        #Reset the command
        input_gpio[8] = GPIO.LOW

                
    return 0

def process_pump_control():

    if (input_gpio[9] == GPIO.HIGH):
        output_gpio[3] = GPIO.LOW
        print(f'{datetime.datetime.now()} LIVINGROOM_PUMP_CONTROL_ON')

        #Reset the command
        input_gpio[9] = GPIO.LOW

    if (input_gpio[10] == GPIO.HIGH):
        output_gpio[3] = GPIO.HIGH
        print(f'{datetime.datetime.now()} LIVINGROOM_PUMP_CONTROL_OFF')

        #Reset the command
        input_gpio[10] = GPIO.LOW

    if (input_gpio[11] == GPIO.HIGH):
        output_gpio[4] = GPIO.LOW
        print(f'{datetime.datetime.now()} BEDROOM_PUMP_CONTROL_ON')

        #Reset the command
        input_gpio[11] = GPIO.LOW

    if (input_gpio[12] == GPIO.HIGH):
        output_gpio[4] = GPIO.HIGH
        print(f'{datetime.datetime.now()} BEDGROOM_PUMP_CONTROL_OFF')

        #Reset the command
        input_gpio[12] = GPIO.LOW

                
    return 0

def check_thermostat():
    global bedroom_time_begin
    global bedroom_time_end
    global livingroom_time_begin
    global livingroom_time_end
    global livingroom_time
    global livingroom_thermostat
    global bedroom_time
    global bedroom_thermostat

    # Update time limits
    time_now = datetime.datetime.now().time()
    if (time_now > livingroom_time_begin) or (time_now < livingroom_time_end):
        livingroom_time = True

    if (time_now > bedroom_time_begin) or (time_now < bedroom_time_end):
        bedroom_time = True

    # Update thermostat status
    if input_gpio[0] == 1:
        livingroom_thermostat = True

    if input_gpio[1] == 1:
        bedroom_thermostat = True

    return 0

def process_automate_mode():
    global main_state
    global main_count
    global command
    global parameter
    global period
    global livingroom_time
    global bedroom_time
    global livingroom_thermostat
    global bedroom_thermostat

    print(f'{datetime.datetime.now()} automate_mode[{parameter}]: {main_state}, {main_count}')
    if main_state  == 'ST_INIT':
        # Initialize registers and variables
        output_gpio = [GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH]
        main_state = 'ST_WAIT_ONE_MINUTE_01'

    elif main_state == 'ST_WAIT_ONE_MINUTE_01':
        if main_count > (60/period):
            main_state = 'ST_READY'
            main_count = 0
        main_count += 1

    elif main_state == 'ST_READY':
        check_thermostat()
        if (livingroom_time and livingroom_thermostat) or (bedroom_time and bedroom_thermostat):
            main_state = 'ST_TURN_ON_HEATER'

    elif main_state == 'ST_TURN_ON_HEATER':
        input_gpio[3] = GPIO.HIGH
        # [jav] complete two more cases
        if bedroom_thermostat:
            main_state = 'ST_TURN_ON_V3V_BEDROOM'

    elif main_state == 'ST_TURN_ON_V3V_BEDROOM':
        input_gpio[7] = GPIO.HIGH
        main_state = 'ST_WAIT_ONE_MINUTE_02'

    elif main_state == 'ST_WAIT_ONE_MINUTE_02':
        if main_count > (60/period):
        # [jav] complete two more cases
            if bedroom_thermostat:
                main_state = 'ST_TURN_ON_PUMP_BEDROOM'
                main_count = 0
        main_count += 1

    elif main_state == 'ST_TURN_ON_PUMP_BEDROOM':
        input_gpio[11] = GPIO.HIGH
        main_state = 'ST_HEATING_BEDROOM'

    elif main_state == 'ST_HEATING_BEDROOM':
        check_thermostat()
        # [jav] complete two more cases
        if (bedroom_time and bedroom_thermostat) != True:
            main_state = 'ST_TURN_OFF_V3V_BEDROOM'

    elif main_state == 'ST_TURN_OFF_V3V_BEDROOM':
        input_gpio[8] = GPIO.HIGH
        main_state = 'ST_WAIT_ONE_MINUTE_03'

    elif main_state == 'ST_WAIT_ONE_MINUTE_03':
        if main_count > (60/period):
        # [jav] complete two more cases
            if (bedroom_time and bedroom_thermostat) != True:
                main_state = 'ST_TURN_OFF_PUMP_BEDROOM'
                main_count = 0
        main_count += 1

    elif main_state == 'ST_TURN_OFF_PUMP_BEDROOM':
        input_gpio[12] = GPIO.HIGH
        # [jav] complete two more cases
        main_state = 'ST_TURN_OFF_HEATER'

    elif main_state == 'ST_TURN_OFF_HEATER':
        input_gpio[4] = GPIO.HIGH
        main_state = 'ST_READY'

    return 0

def process_reset():
    global command
    global parameter
    global test_count
    global test_states
    global test_heater_state
    global test_heater_count
    global main_state
    global main_count
    global t

    command = ''
    parameter = ''

    test_count = 0
    test_states = 10

    test_heater_state = 'STATE_INIT'
    test_heater_count = 0

    main_state = 'ST_INIT'
    main_count = 0

    t = 0

    output_gpio = [GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH]

    return 0


def process_test_heater():
    global test_heater_state
    global test_heater_count
    global command
    global parameter
    global period

    print(f'{datetime.datetime.now()} test_heater[{parameter}]: {test_heater_state}, {test_heater_count}')
    if test_heater_state == 'STATE_INIT':
        test_heater_state = 'STATE_TURN_ON_HEATER'

    #Check it! I need a full cycle here before jump to the next state!! [jav]
    elif test_heater_state == 'STATE_TURN_ON_HEATER':
        print(f'{datetime.datetime.now()} test_heater[{parameter}]: Inside STATE_TURN_ON_HEATER, setting input_gpio[3]=1')
        input_gpio[3] = GPIO.HIGH
        test_heater_state = 'STATE_TURN_ON_V3V'

    elif test_heater_state == 'STATE_TURN_ON_V3V':
        # Activate V3V, whether livingroom or bedroom
        if parameter == 'livingroom':
            input_gpio[5] = GPIO.HIGH
        elif parameter == 'bedroom':
            input_gpio[7] = GPIO.HIGH

        test_heater_state = 'STATE_WAIT_ONE_MINUTE'

    elif test_heater_state == 'STATE_WAIT_ONE_MINUTE':
        if test_heater_count > (60/period):
            test_heater_state = 'STATE_TURN_ON_PUMP'
            test_heater_count = 0
            
        test_heater_count += 1
        
    elif test_heater_state == 'STATE_TURN_ON_PUMP':
        # Activate PUMP, whether livingroom or bedroom
        if parameter == 'livingroom':
            input_gpio[9] = GPIO.HIGH
        elif parameter == 'bedroom':
            input_gpio[11] = GPIO.HIGH

        test_heater_state = 'STATE_WAIT_TEN_MINUTES'

    elif test_heater_state == 'STATE_WAIT_TEN_MINUTES':
        # Parametrize it [jav]
        if test_heater_count > ((30*60)/period):
            test_heater_state = 'STATE_TURN_OFF_PUMP'
            test_heater_count = 0
            
        test_heater_count += 1
        
    elif test_heater_state == 'STATE_TURN_OFF_PUMP':
        # Dectivate PUMP, whether livingroom or bedroom
        if parameter == 'livingroom':
            input_gpio[10] = GPIO.HIGH
        elif parameter == 'bedroom':
            input_gpio[12] = GPIO.HIGH

        test_heater_state = 'STATE_TURN_OFF_V3V'

    elif test_heater_state == 'STATE_TURN_OFF_V3V':
        # Deactivate V3V, whether livingroom or bedroom
        if parameter == 'livingroom':
            input_gpio[6] = GPIO.HIGH
        elif parameter == 'bedroom':
            input_gpio[8] = GPIO.HIGH

        test_heater_state = 'STATE_WAIT_ANOTHER_MINUTE'

    elif test_heater_state == 'STATE_WAIT_ANOTHER_MINUTE':
        if test_heater_count > (60/period):
            test_heater_state = 'STATE_TURN_OFF_HEATER'
            test_heater_count = 0
            
        test_heater_count += 1
        
    elif test_heater_state == 'STATE_TURN_OFF_HEATER':
        input_gpio[4] = GPIO.HIGH
        test_heater_state = 'STATE_END'

    elif test_heater_state == 'STATE_END':
        test_heater_state = 'STATE_INIT'
        test_heater_count = 0
        command = ''
        parameter = ''

    return 0

def process_automaton():
    global command
    global parameter

    if command == 'automate_mode':
        process_automate_mode()

    elif command == 'reset':
        process_reset()

    elif command == 'test_heater':
        process_test_heater()

    process_heater_control()
    process_v3v_control()
    process_pump_control()

    return 0


def test_relays():
    global test_count
    global test_states

    time_now = datetime.datetime.now().time()
    print(f'{datetime.datetime.now()} test_relays: test_count({test_count}) cycle({test_count%test_states})')

    cycle = test_count % test_states
    if cycle == 0:
        output_gpio[0] = GPIO.LOW

    elif cycle == 1:
        output_gpio[0] = GPIO.HIGH

    elif cycle == 2:
        output_gpio[1] = GPIO.LOW

    elif cycle == 3:
        output_gpio[1] = GPIO.HIGH

    elif cycle == 4:
        output_gpio[2] = GPIO.LOW

    elif cycle == 5:
        output_gpio[2] = GPIO.HIGH

    elif cycle == 6:
        output_gpio[3] = GPIO.LOW

    elif cycle == 7:
        output_gpio[3] = GPIO.HIGH

    elif cycle == 8:
        output_gpio[4] = GPIO.LOW

    elif cycle == 9:
        output_gpio[4] = GPIO.HIGH


    test_count += 1


    return 0


# Initialize GPIO outputs to HIGH (it doesn't activate the relays)
# main() code

print('Initializing GPIO...')
show_variables()
init_gpio()

print('Initializing relays OUTPUT as HIGH...')
write_gpio()

try:
    # Infinite loop waiting for a CTRL^C
    while True:
        process_automaton()

        t += 1
        write_gpio()
        read_gpio()
        read_command()
        status_gpio()
        time.sleep(period)

except KeyboardInterrupt:
   GPIO.cleanup()
   print('Exiting...')

