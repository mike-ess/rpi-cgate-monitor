cgate_config = {
    "ip_address":"192.168.x.x",
    "command_port":20023,
    "event_port":20025,
    "cgate_project":"MYHOME",
    "cbus_network":"254",
    "cbus_application":"56"   
}

startup_config = {
    "max_connection_attempts":10,
    "connection_retry_interval":1 # Seconds
}

event_actions = {
    ("1","255"):"Kitchen Lights Turned On",
    ("3","0"):"Bedroom Lights Turned Off",
    ("6","255"):"ALARM SIREN SOUNDING. POSSIBLE INTRUDER?",
    ("6","0"):"ALARM SIREN HAS STOPPED",
    ("7","255"):"Alarm Armed",
    ("7","0"):"Alarm Disarmed",
    ("10","255"):"All Lights Off"
}

cbus_groups = {
    "1":"Kitchen",
    "2":"Living Room",
    "3":"Bedroom",
    "4":"Bathroom",
    "5":"Garage",
    "6":"Bus Coupler 1",
    "7":"Bus Coupler 2",
    "8":"Bus Coupler 3",
    "9":"Bus Coupler 4",
    "10":"Trigger All Lights On"

}

cbus_units = {
    "1":"Kitchen",
    "2":"Living Room East",
    "3":"Living Room West",
    "4":"Bedroom Main",
    "5":"Bedroom Bedside Left",
    "6":"Bedroom Bedside Right",
    "7":"Bathroom",
    "8":"Garage",
    "9":"Bus Coupler for Alarm"
}
