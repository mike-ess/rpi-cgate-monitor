import logging
import sys
from config_ini import ConfigIni

LOGGING_INI_FILENAME="logging.ini"

class LoggerIni:

    @staticmethod
    def get_log_level_from_str(stringLevel):
        try:
            number_level = getattr(logging, stringLevel.upper(), None)
            if isinstance(number_level, int):
                return number_level
            else:
                # Default to info
                # TODO: RAISE EXCEPTION
                return logging.INFO
        except:
            # Default to info
            # TODO: RAISE EXCEPTION
            return logging.INFO

    @staticmethod
    def get_logger(moduleName):

        logging_config = ConfigIni(LOGGING_INI_FILENAME)    

        # Decide what section name we will be reading
        # loggin config from in the ini file.
        if logging_config.section_exists(moduleName):
            section = moduleName
        else:
            section = "Default"

        logger = logging.getLogger(moduleName)

        if section == "Default" and not logging_config.section_exists(section):
            # Not configured very well. Either file didn't exist, or did not contain
            # the right information, so let's use a set of defaults.

            # Set log level.
            logger.setLevel(logging.DEBUG)

            # Set log format.
            format = "[%(levelname)-5s]%(asctime)s:%(module)5s:%(funcName)s[%(lineno)d]:%(message)s"
            formatter = logging.Formatter(format)

            # Set output to stdout
            file_handler = logging.StreamHandler(sys.stdout)       
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        else:
            # Logger is configured so let's use the configuration.
        
            # Set log level.
            stringLevel = logging_config.get_value(section, "Level")
            level = LoggerIni.get_log_level_from_str(stringLevel)
            logger.setLevel(level)

            # Set log format.
            format = logging_config.get_value(section, "Format")
            formatter = logging.Formatter(format)

            # Set output file / stream / null
            filename = logging_config.get_value(section, "Filename")
            if filename == "" or filename == "stdout":
                print("filename = stdout")
                file_handler = logging.StreamHandler(sys.stdout)       
            elif filename == "null":
                #print("filename = null")
                file_handler = logging.NullHandler()       
            else:
                #print("filename =", filename)
                file_handler = logging.FileHandler(filename, mode="a")            
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        logger.propagate = False

        return logger

##############################################################
### UNIT TESTS (uncomment as necessary)
##############################################################

if __name__ == "__main__":

    # Set logging to console for testing purposes

    # Expect a section called [__main__]
    logger = LoggerIni.get_logger(__name__)

    logger.error("Error statement.")
    logger.warn ("Warning statement.")
    logger.info ("Info statement.")
    logger.debug("Debug statement.")
