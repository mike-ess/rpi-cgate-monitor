import sys
sys.path.append("../utilities")

import cbus_config

import cgate_client
import messenger
import string
import threading
import time


class CGateMonitor:

    def __init__(self):
        self.interval_log = ""

        self.ip_address = ""
        self.command_port = ""
        self.event_port = ""
        self.cgate_project = ""
        self.cbus_network = ""
        self.cbus_application = ""

        self.cbus_project_id = ""

        self.messenger = messenger.Messenger()


    # Connect to CGate and then go through the necessary
    # messages to ensure it is functioning correctly, and
    # get us ready to use it.
    def cgate_connect(self):
        self.cgate_commands = cgate_client.CGateClient(self.ip_address, self.command_port)
        # So much can go wrong, assume failure until we reach success
        return_value = False
        open_response = self.cgate_commands.open()
        if open_response.startswith("201 Service ready"):
            load_response = self.cgate_commands.send_receive("noop")
            if load_response.startswith("200 OK") or load_response.startswith("400 Syntax Error."):
                load_response = self.cgate_commands.send_receive("project load " + self.cgate_project)
                if load_response.startswith("200 OK"):
                    use_response = self.cgate_commands.send_receive("project use " + self.cgate_project)
                    if use_response.startswith("200 OK"):
                        net_open_response = self.cgate_commands.send_receive("net open " + self.cbus_network)
                        if net_open_response.startswith("200 OK"):
                            start_response = self.cgate_commands.send_receive("project start " + self.cgate_project)
                            if start_response.startswith("200 OK"):
                                state_response = self.cgate_commands.send_receive("get " + self.cbus_network + " state")
                                return_value = True

        # If CGate is working OK, open an event listener
        if return_value == True:
            self.cgate_events = cgate_client.CGateClient(self.ip_address, self.event_port)
            self.cgate_events.open_no_listen()

        return return_value


    # Given a GroupAddress number, in string form, return the name of the group.
    def get_group_name(self, group_address):
        group_name = cbus_config.cbus_groups.get(group_address, "Unknown")
        return group_name


    # Given a Unit number, in string form, return the name of the unit.
    def get_unit_name(self, unit_address):
        group_name = cbus_config.cbus_units.get(unit_address, "Unknown")
        return group_name


    # Given a single CGate event, in string format, unpick
    # it and act as required. Not all events are logged,
    # only certain ones we are interested in.
    #
    # Example event string:
    #   "lighting on //MYHOME/254/56/104  #sourceunit=66 OID=4d5304c0-80e3-1031-aaf4-ca61021dd969"
    def process_event(self, event):
        print(event)

        # Only handle lighting events. Avoid non-lighting events.
        if event.startswith("lighting"):
            # Capture date/time of event
            current_date = time.strftime("%d/%m/%y")
            current_time = time.strftime("%H:%M:%S")

            # Get key information from the CBus event
            group_index = event.find(self.cbus_project_id)
            space_index = event.find(" ", group_index)
            group_number = event[group_index + len(self.cbus_project_id) : space_index]
            group_name = self.get_group_name(group_number)
            unit_index = event.find("#sourceunit=")
            space_index = event.find(" ", unit_index)
            unit_number = event[unit_index + 12 : space_index]
            unit_name = self.get_unit_name(unit_number)
            new_level = "unknown"

            # Get lighting level
            if event.startswith("lighting on"):
                new_level = "255"
            if event.startswith("lighting off"):
                new_level= "0"
            if event.startswith("lighting ramp"):
                group_string = self.cbus_project_id + group_number
                group_string_index = event.find(group_string)
                level_index = group_string_index + group_string.__len__() + 1
                space_index = event.find(" ", level_index)
                new_level = event[level_index : space_index]
            
            # Log and message the event if necessary
            new_log_message = cbus_config.event_actions.get((group_number,new_level),"")
            if new_log_message.__len__() > 0:
                new_log_message += "\r\n"
                new_log_message += current_date + " " + current_time + "\r\n"
                new_log_message += "From " + unit_name + "\r\n"

                self.interval_log += "------------------------\r\n"
                self.interval_log += new_log_message
                self.interval_log += "New Level=" + new_level + "\r\n"
                self.interval_log += event + "\r\n"
                self.interval_log += "------------------------\r\n"

                # Send individual message to Twitter
                self.messenger.send_twitter_api_msg(new_log_message)
       

    # This runs on a thread simultaneously with the run_cgate_monitor method.
    # run_cgate_monitor create log entries, this writes them occasionally.
    def run_logger(self):
        print("run_logger() has started")
        interval = 3 # seconds
        last_time = time.time()
        while True:
            # TODO lock
            if time.time() - last_time > interval:
                if self.interval_log.__len__() > 0:
                    print(self.interval_log)
                    self.interval_log = ""
                last_time = time.time()
            time.sleep(1)
            # TODO unlock


    # This runs on a thread simultaneously with the run_logger method.
    # This connects to CGate, then continues to listen for events
    # and logs them so run_logger can then process them.
    def run_cgate_monitor(self):
        print("run_cgate_monitor() has started")

        self.ip_address = cbus_config.cgate_config["ip_address"]
        self.command_port = cbus_config.cgate_config["command_port"]
        self.event_port = cbus_config.cgate_config["event_port"]
        self.cgate_project = cbus_config.cgate_config["cgate_project"]
        self.cbus_network = cbus_config.cgate_config["cbus_network"]
        self.cbus_application = cbus_config.cgate_config["cbus_application"]

        self.cbus_project_id = "//" + self.cgate_project + "/" + self.cbus_network + "/" + self.cbus_application + "/"

        max_connection_attempts = cbus_config.startup_config["max_connection_attempts"]
        connection_retry_interval = cbus_config.startup_config["connection_retry_interval"]

        print("Sleeping for ",connection_retry_interval," seconds to wait for CGate to start... ")
        time.sleep(connection_retry_interval)
        print("OKAY")

        attempts = 10
        result = False

        for attempts in range(1, max_connection_attempts):
            print("Connecting to CGate, attempt #",attempts,"... ")
            if self.cgate_connect() == True:
                result = True
                break;
            else:
                print("Failed.")
                time.sleep(5)

        if result == False:
            print("Failed to connect to CGate after ", max_connection_attempts, " attempts, giving up.")
            return
        else:
            print("SUCCESS!!!!")
        
            # Process events forever
            # TODO: Move this out of the cgate_connect method
            while True:
                print("Waiting for event")
                event = self.cgate_events.receive()
                print("Received event: ", event)
                self.process_event(event)
    

##############################################################
### START CGATE MONITOR
##############################################################

if __name__ == "__main__":
    cgate_monitor = CGateMonitor()

    # Start Logger Thread
    logger = threading.Thread(target=cgate_monitor.run_logger, args=())
    logger.daemon = False
    logger.start()
    pass

    time.sleep(1)
            
    # Start Monitor Thread
    monitor = threading.Thread(target=cgate_monitor.run_cgate_monitor, args=())
    monitor.daemon = False
    monitor.start()
	