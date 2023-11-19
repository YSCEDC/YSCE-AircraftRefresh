import os
import csv

def import_dat(fpath):
    with open(fpath, mode='r') as file:
        data = [x[:-1] for x in file.readlines()]
    return data

def write_dat(fpath, lines):
    with open(fpath, mode='w') as file:
        file.writelines("%s\n" % place for place in lines)

def find_dat_files(fpath):
    dat_files = list()
    for root, subdir, files in os.walk(fpath):
        for file in files:
            fpath = os.path.join(root, file)
            if file.endswith(".dat"):
                dat_files.append(fpath)
    return dat_files

def run_dat_scrape(dat_fpath):
    """Get key performance DAT Variables from YSF DAT Files"""
    dat_files = find_dat_files(dat_fpath)

    headers = ["AC_IDENTIFY","SUBSTNAM","RADARCRS","BMBAYRCS","BOMBINBAY","STRENGTH","GUNPOWER","GUNINTVL","# MACHINE GUNS",
               "INITGUN","Damage/Second","Firing Time","THRAFTBN","THRMILIT",
               "WEIGHCLN","WEIGFUEL","FUELABRN","FUELMILI","MXIPTAOA","MXIPTSSA",
               "MXIPTROL","CRITAOAP","CRITAOAM","MANESPD1","MANESPD2","CPITMANE",
               "CPITSTAB","CYAWMANE","CYAWSTAB","CROLLMAN","CRITSPED","MAXSPEED",
               "REFVCRUS","REFACRUS","REFTCRUS","REFVLAND","REFAOALD","REFLNRWY",
               "REFTHRLD","CTLLDGEA","CTLBRAKE","CTLSPOIL","CTLABRNR","CTLTHROT",
               "CTLIFLAP","CTLINVGW","CTLATVGW","CLVARGEO","CDVARGEO","CLBYFLAP",
               "CDBYFLAP","CDBYGEAR","CDSPOILR","VGWSPED1","VGWSPED2"]
    dat_vars = ["IDENTIFY","SUBSTNAM","RADARCRS","BMBAYRCS","BOMBINBAY","STRENGTH","GUNPOWER","GUNINTVL","# MACHINE GUNS",
               "INITGUN","THRAFTBN","THRMILIT",
               "WEIGHCLN","WEIGFUEL","FUELABRN","FUELMILI","MXIPTAOA","MXIPTSSA",
               "MXIPTROL","CRITAOAP","CRITAOAM","MANESPD1","MANESPD2","CPITMANE",
               "CPITSTAB","CYAWMANE","CYAWSTAB","CROLLMAN","CRITSPED","MAXSPEED",
               "REFVCRUS","REFACRUS","REFTCRUS","REFVLAND","REFAOALD","REFLNRWY",
               "REFTHRLD"]
    units = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","s","N/A","N/A","N/A","N/A","kg","kg",
             "kg","kg","kg","kg","deg","deg","deg","deg","deg","kt","kt","N/A","N/A",
             "N/A","N/A","N/A","MACH","MACH","MACH","ft","N/A","kt","deg","m","N/A","N/A",
             "N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","kt","kt"]
    numerics = ".0123456789"

    all_units = ['m','t','kg','lb','MACH','kt','ft','deg', "s"]


    output = list()
    for fpath in dat_files:
        dat = import_dat(fpath)
        row = [""] * len(headers)
        machine_gun_count = 0

        # Make a dict of all the dat variables we are looking for
        data = dict()
        for var in dat_vars:
            data[var] = ""

        for line in dat:
            var = line[:8]

            if var in dat_vars and var in headers:
                output_idx = headers.index(var)

            # IDENTIFY and SUBSTNAM have " delimiters compared to whitespace delimiters for all variables
            if var == "IDENTIFY":
                data["IDENTIFY"] = line.split('"')[1]
            elif var == "SUBSTNAM":
                parts = line.split('"')
                if len(parts) > 1:
                    data["SUBSTNAM"] = line.split('"')[1]
                else:
                    data["SUBSTNAM"] = line
            elif var.startswith("MACHNG"):
                machine_gun_count += 1
            elif var in dat_vars:
                expected_units = units[output_idx]

                # Get the dat value
                parts = line.split()  # whitespace split
                value = parts[1]

                if expected_units != "N/A":
                    if value.endswith(expected_units):
                        value = float(value.replace(expected_units, ''))
                    else:
                        # Some other units that need to be taken care of
                        if expected_units == "ft" and value.endswith("m"):
                            value = float(value[:-1]) * 3.28084
                        elif expected_units == "m" and value.endswith("ft"):
                            value = float(value[:-2]) / 3.28084
                        elif expected_units == "kg" and value.endswith("t"):
                            value = float(value[:-1]) * 2000
                        elif expected_units == "kg" and value.endswith("lb"):
                            value = float(value[:-2]) * 0.453592
                        elif expected_units == "kt" and value.endswith("km/h"):
                            value = float(value[:-4]) * 0.539957
                        elif expected_units == "MACH" and value.endswith("kt"):
                            value = float(value[:-2]) / 666.739
                        elif expected_units == "MACH" and value.endswith("km/h"):
                            # convert to knots then to MACH
                            value = float(value[:-4]) * 0.539957 / 666.739
                        elif expected_units == "s" and value.endswith("s"):
                            value = float(value)
                        elif expected_units == "MACH" and value.lower().endswith("mach"):
                            value = float(value[:-4])
                        else:
                            value = float(value)
                else:
                    value = float(value)
                            
                data[var] = value

        # Fill in default values
        if machine_gun_count > 0 and data["GUNPOWER"] == "":
            data["GUNPOWER"] = 1
        if data["INITGUN"] == "" and machine_gun_count == 0:
           data["INITGUN"] = 0
           machine_gun_count = 0
        if data["RADARCRS"] == "":
            data["RADARCRS"] = 1
        if data["GUNINTVL"] == "":
            data["GUNINTVL"] = 0.075

        # Apply rounding to some values
        int_vars = ["STRENGTH","INITIGUN","THRAFTBN","THRMILIT","WEIGHCLN","WEIGFUEL","REFLNRWY","REFVLAND","REFACRUS"]
        three_vars = ["GUNINTVL","RADARCRS","FUELABRN","FUELMILI","MXIPTAOA","MXIPTSSA","MXIPTROL",
                      "CRITAOAP","CRITAOAM","CPITMANE","CPITSTAB","CYAWMANE","CYAWSTAB","CROLLMAN",
                      "CRITSPED","MAXSPEED","REFAOALD","REFTCRUS","REFTHRLD","REFVCRUS","BMBAYRCS"]
        for datvar in data:
            if datvar in int_vars and data[datvar] != '':
                data[datvar] = int(data[datvar])
            elif datvar in three_vars and data[datvar] != '':
                data[datvar] = "{:.3f}".format(data[datvar])
            elif isinstance(data[datvar],float):
                data[datvar] = "{:.3f}".format(data[datvar])

        # Build the output row
        row = [data["IDENTIFY"]]
        for name in headers[1:]:
            if name in list(data.keys()):
                row.append(data[name])
            else:
                row.append("")

        # Put in the derived data into the output row
        row[headers.index("# MACHINE GUNS")] = machine_gun_count
        
        

        output.append(row)

    output.insert(0, headers)

    fname = "YSFlight_DATVARs.csv"
    fpath = os.path.join(os.getcwd(), fname)

    with open(fpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(output)


def import_csv(fpath):
    data = list()
    with open(fpath, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for line in csv_reader:
            data.append(line)
    return data
        


def update_dats():    
    cwd = os.getcwd()
    # Expect to find 2 csv files, one called current, the other called JET DATs

    current_fpath = os.path.join(cwd, "YSFCE Tracker - Current.csv")
    dat_class_fpath = os.path.join(cwd, "YSFCE Tracker - JET DATs.csv")

    # Initialize data storage
    dat_classes = dict()
    units = dict()

    # Import DAT variable csv file
    dat_class_data = import_csv(dat_class_fpath)

    # Extract header and units information
    headers = dat_class_data[0][1:]
    unit_row = dat_class_data[1][1:]
    admin_headers = ["# MACHINE\nGUNS", "Damage/\nSecond", "Firing\nTime", "AB Time", "MIL Time"]

    # Store units information in the units dict
    for h, u in zip(headers, unit_row):
        units[h] = u

    # Make dict entries for the various dat classes
    for line in dat_class_data[2:]:
        class_dict = dict()
        for h, v in zip(headers, line[1:]):
            class_dict[h] = v
        dat_classes[line[0]] = class_dict

    # Get list of dat files in the subdirs
    dat_filepaths = find_dat_files()

    # Import the current csv file
    current_data = import_csv(current_fpath)

    # Iterate over the rows in the current CSV to find the dat files.
    for line in current_data[1:]:  # Skip the haeder row
        status = line[0]
        dat_class = line[3]
        dat_subfolder = line[17]
        dat_filename = line[18]
        identify = line[10]

        # Extract information for this dat
        if dat_class in dat_classes.keys():
            dat_update_dict = dat_classes[dat_class]

            # Eliminate blanks in the dict
            for var in dat_update_dict.keys():
                if len(dat_update_dict[var]) == 0:
                    del dat_update_dict[var]                
        else:
            print("Unable to process {} due to missing DAT Class".format(identify))

        # Only proccess dat files that are current in the pack
        if status.lower() != "current":
            continue

        # Determine what the filepath should end with
        dat_fpath_end = dat_subfolder + dat_filename

        # Find dat file that matches this criteria
        dat_fpath = ""
        for fpath in dat_filepaths:
            # use case-insensitive comparison
            if fpath.lower().endswith(dat_fpath_end.lower()):
                dat_fpath = fpath
                break

        # Skip this dat file if we do not have a valid filepath for the dat file
        if dat_fpath == "":
            print("Unable to find dat file: {}".format(dat_fpath_end))
            continue

        # Import the dat file into a list of strings
        dat_file = import_dat(dat_fpath)

        # Iterate through the dat file and find if there is a value to overwrite
        changes_made = False
        for idx, line in enumerate(dat_file):
            var = line[:8]

            if var in dat_update_dict.keys():
                if "#" in line:
                    ender = "#" + str(line.split("#")[1])
                else:
                    ender = ""
                
                if units[var] == "N/A":
                    new_line = "{} {}  {}".format(var, dat_update_dict[var], ender)
                else:
                    new_line = "{} {}{}  {}".format(var, dat_update_dict[var], units[var], ender)
                
                # Save the new line to the dat file
                dat_file[idx] = new_line
                changes_made = True

                # Delete this from the dat_update_dict so that we have a clean record of what should be added
                del dat_update_dict[var]

        # For any DAT variable that still remain, add these at the end since they were not in the
        # DAT File to begin with.
        wrap_up_lines = ["REM YSFCE Standardization Additions"]

        # Generate new lines
        for var in dat_update_dict.keys():
            if var not in admin_headers:
                if units[var] == "N/A":
                    new_line = "{} {}".format(var, dat_update_dict[var])
                else:
                    new_line = "{} {}{}".format(var, dat_update_dict[var], units[var])
                wrap_up_lines.append(new_line)

        
        if len(wrap_up_lines) > 1:
            changes_made = True

            # Find the end of the dat file
            if "AUTOCALC" in dat_file:
                end_idx = dat_file.index("AUTOCALC")
            else:
                end_idx = len(dat_file) - 1

            # Remove everything after the AUTOCALC and replace with wrap up
            dat_file = dat_file[:end_idx]
            dat_file.extend(wrap_up_lines)
            dat_file.append("AUTOCALC")
                
        
        # Save the file if we have applied an update
        if changes_made is True:
            write_dat(dat_fpath, dat_file)
            print("Updated: {}".format(dat_fpath_end))
    


run_dat_scrape(os.path.join(os.getcwd(), "YSFlight 2015 stock aircraft folder"))
# update_dats()
