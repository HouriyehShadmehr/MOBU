    ## -*- coding: cp1252 -*-

## ============================================================================== ##
##                                                                                ##
## Authors:       Jeff Kelliher, Kenneth Conway & Houriyeh Shadmehr               ##
##                                                                                ##
## Purpose:       MOBU (or MO-del BU-ilder) script                                ##
##                                                                                ##
## Version:       MAY 2022                                                        ##
##                                                                                ##
## ============================================================================== ##

print "                                                    "
print "         ##       ##     ###     ######    ###  ###     "
print "         ###     ###    #####    ### ###   ###  ###     "
print "         ####   ####   ### ###   ###  ###  ###  ###     "
print "         ###########  ###   ###  ### ###   ###  ###     "
print "         ### ### ###  ###   ###  ######    ###  ###     "
print "         ###  #  ###  ###   ###  ######    ###  ###     "
print "         ###     ###  ###   ###  ### ###   ###  ###     "
print "         ###     ###   ### ###   ###  ###  ###  ###     "
print "         ###     ###    #####    ### ###   ########     "
print "         ###     ###     ###     ######    ##### ##     "
print "                                                        "
print " A model builder script for connection feasibility analysis   "

####################################################################################
##                                   USER INPUT                                   ##
####################################################################################


## Set to True for debugging option
global debug
debug = True

## MAIN USER-DEFINED OPTIONS:
##  [A] add a ciruit
##  [B] add a station to an existing circuit
##  [C] add a load
##  [D] add a generator
##  [E] add reactive compensation in the form of a STATCOM machine model

add_stations_to_model              = False
add_loads_to_model                 = False
add_machines_to_model              = True
add_circuits_to_model              = False
add_reactive_compensation_to_model = False

generation_increment               = 40.0 ## i.e. generation connection is increased by this increment (sometimes 100 MW is used)

run_n_minus_one_analysis           = True  ## Run a general N-1 on the entire system

option_to_set_res_to_min           = False ## Set wind & solar generation types to minimum value (i.e. 0 Mvar)

option_to_set_res_to_max           = True  ## Set wind & solar generation to high level of output
res_increase_assumptions           = {
                                     # "summer peak": {
                                     #            'onshore':  [100.0, [5, 6, 8, 9, 10, 12]],
                                     #            'offshore': [100.0, [5, 6, 8, 9, 10, 11, 12]],
                                     #            'solar':    [100.0, [5, 6, 8, 9, 10, 11, 12]]
                                     #            },
                                     # "winter peak": {
                                     #            'onshore':  [100.0, [4, 5, 6, 8, 9, 10, 12]],
                                     #            'offshore': [100.0, [4, 5, 6, 8, 9, 10, 11, 12]],
                                     #            'solar':    [100.0, [4, 5, 6, 8, 9, 10, 11, 12]]
                                     #            },
                                    "summer peak": {
                                               'onshore':  [100.0, [3, 4, 5, 8, 11]],
                                               'offshore': [100.0, [3, 4, 5, 8, 11]],
                                               'solar':    [100.0, [3, 4, 5, 8, 11]]
                                               },
                                    "winter peak": {
                                               'onshore':  [100.0, [3, 4, 5, 8, 11]],
                                               'offshore': [100.0, [3, 4, 5, 8, 11]],
                                               'solar':    [100.0, [3, 4, 5, 8, 11]]
                                               },
                                    # "summer valley": {
                                    #             'onshore':  [70.0, [4, 5, 6, 8, 9, 10, 12]],
                                    #             'offshore': [70.0, [4, 5, 6, 8, 9, 10, 11, 12]],
                                    #             'solar':    [0.0, [4, 5, 6, 8, 9, 10, 11, 12]]
                                    #             }
                                      }                            

change_data_centre_level           = False   ## Based on scaling the portfolio given in the EirGrid model(s)
new_data_centre_total              = 1010        #1250.0 ## In MW for 2030 year study

change_offshore_wind_level         = False   ## Based on scaling the portfolio in the model
new_offshore_wind_total            = 2500.0 ## In MW

make_tytfs_base_case_changes       = False ## Enabling this allows for adding future reinforcements

shl_export_split                   = False ## Splitting SHL for export

alter_2029_case                    = False ## Editing the 2029 cases to resolve issues

add_soef_projects                  = False ## Make SOEF changes - based on user selection

remove_generators_from_model       = False ## Remove user-specified circuits from the model

add_renewable_generation           = False ## Add new renewable generation to the case

enhance_voltage_profile            = False ## Updates setpoints for machines, transformers & shunts to provide a better solution

sort_out_ckm_pst                   = False ## Use optimisation to determine the least worst phase angle

change_peak_demand_level           = True ## E.g. if using a 2029 case and need a 2025 load level

Min_Set_units_Option               = True
uprate_all_110kv_to_standard       = False ## Uprate ALL 110 kV circuits to the EirGrid standards
uprate_particular_circuits         = False ## Uprate user-specified circuits
global adjust_transformer_taps
adjust_transformer_taps            = False ## When solving, enable/disable transformer taps
use_mobu_merit_order               = True  ## Set to True to use the merit order below - otherwise work from EirGrid base-line

global pst_angle_for_n, pst_angle_for_n_1
pst_angle_for_n   = 0.0 ## Default PST angle values
pst_angle_for_n_1 = 0.0 ## Default PST angle values

## *** Review sequence of actions ***

## Add a circuit
##     Note: Format for each circuit entry:
##           "Circuit description": [bus number #1, bus number #2, circuit identifier, length (km), technology ('ohl' / 'ugc']
add_circuits_dict = {}

## Add a looped in station
##     Note: Format for each load entry:
##           "Station description": [station bus number, circuit bus number #1, circuit bus number #2, circuit identifier, fraction from bus number #1 (< 1.0)]
add_stations_dict = {'Derrygreenagh': [9999, 4384, 5464, "1", 0.5],
                     'Maynooth': [99900, 3851, 13219, "1", 0.5],
                     'Ennis': [99901, 2361, 2121, "1", 0.5],
                     'Great Island': [99902, 5501, 2741, "1", 0.5],
                     'CullDun': [99903, 2001, 2141, "1", 0.5]
                     }

## Add a load
##     Note: Format for each load entry:
##           "Load description": [bus number, load identifier, MIC (MW), power factor]
## *** NOTE: ADD FIXED LOAD OPTION! ***
add_loads_dict = {}

## Add a generator - this is defined for RES at the moment
##     Note: Format for each generator entry:
##           "Generator description": [bus number, generator identifier, PMAX (MW), PMIN (MW), power factor, RES technology ('offshore', 'onshore', 'solar']
add_machines_dict = {
                #'Derrygreenagh': [9999, "GT", 600.0, 0.0, 0.95, 'gas turbine'],
                'Derrygreenagh': [9999, "GT", 520.0, 0.0, 0.95, 'gas turbine'],
                }

## Add a STATCOM or reactive compensation model - this is done like adding a machine
##     Note: To model a STATCOM set power factor entry (i.e. 0.95) to the Mvar range magnitide required (i.e. for +/- 200 Mvar use 200)  
add_reactive_compensation_dict = {
                #'BALLYVOUSKILL': [1211, "1", 0.0, 0.0, 100.0, 'statcom'],
                #'BALLYNAHULLA': [3331, "1", 0.0, 0.0, 100.0, 'statcom'],
                'BELCAMP': [1472, "XX", 0.0, 0.0, 250.0, 'statcom'],
                'DUNSTOWN': [2202, "XX", 0.0, 0.0, 250.0, 'statcom'],
                }

## Change the rating / status or an existing circuit (overhead line or underground cable)
## Note "Circuit description": [from bus number, to bus number, circuit identifier, status, summer rating, winter rating]
update_particular_circuit_details = {
                                'Aughinish Kilpaddoge 220kV': [1261, 3282, "1", 1, 740, 740],
                                    }
## Define list of generators that will be removed
remove_these_generators = [
                        [39471, "1"], #MP1
                        [39472, "2"], #MP2
                        #[39473, "3"], #MP3
                        [35074, "4"], #LR4
                        [49474, "4"], #WO4
                        [10471, "1"], #AD1
                        [10472, "11"], #AT11
                        #[51471, "1"], #TB1
                        #[51472, "2"], #TB2
                        [51473, "3"], #TB3
                        [51474, "4"], #TB4
                        [39675, "GT"], #MR1
                        [42475, "5"] #NW5
                        ]

## User-defined merit order list
# merit_order = {
#              "23": ["DB1", 31271, "1"],
#              "2": ["HN2", 29673, "2"],
#              "3": ["AD2", 10470, "1"],
#              "4": ["WG1", 28571, "1"],
#              "5": ["GI4", 27474, "1"],
#              "6": ["C30-GT", 75516, "GT"],
#              "7": ["C30-ST", 75515, "ST"],
#              "8": ["TYC-CT", 51771, "CT"],
#              "9": ["TYC-ST", 51772, "ST"],
#              "10": ["PBC-14", 50274, "14"],
#              "11": ["PBC-15", 50275, "15"],
#              "12": ["PBC-16", 50276, "16"],
#              "13": ["B31-A", 70513, "A"],
#              "14": ["B31-B", 70514, "B"],
#              "15": ["B31-C", 70515, "C"],
#              "16": ["HNC-CT", 29672, "CT"],
#              "17": ["HNC-ST", 29671, "ST"],
#              "18": ["B10", 70516, "D"],
#              "19": ["Evermore", 74518, "1"],
#              "20": ["ED1", 19471, "1"],
#              "21": ["MP1", 39471, "1"],
#              "22": ["MP2", 39472, "2"],
#              "1": ["MP3", 39473, "3"],
#              "24": ["RP1", 22671, "1"],
#              "25": ["RP2", 22672, "2"],
#              "26": ["TP1", 52476, "1"],
#              "27": ["TP3", 52477, "1"],
#              "28": ["AT1", 10472, "11"],
#              "29": ["AT2", 10473, "12"],
#              "30": ["AT4", 10474, "14"],
#              "31": ["TB3", 51473, "3"],
#              "32": ["TB4", 51474, "4"],
#              "33": ["Lumcloon", 35771, "1"],
#              "34": ["Derrycarney", 49471, "1"],
#              "35": ["Derrycarney", 49472, "1"],
#              #"43": ["NW5", 42475, "5"],
#              ##"30": ["EWIC", 54630, "1"],
#              ##"31": ["Moyle", 86220, "1"],
#              ##"38": ["Greenlink", 2752, "~I"],
#              ##"39": ["Celtic", 5471, "~I"],
#              #"34": ["TH1", 52071, "1"],
#              #"35": ["TH2", 52072, "2"],
#              #"36": ["TH3", 52073, "3"],
#              #"37": ["TH4", 52074, "4"],
#                 }
# merit_order = {
#              "1": ["MP3", 39473, "3"],
#              "2": ["DB1", 31271, "1"],
#              "3": ["HN2", 29673, "2"],
#              "4": ["AD2", 10470, "1"],
#              "5": ["WG1", 28571, "1"],
#              "6": ["GI4", 27474, "1"],
#              "7": ["C30-GT", 75516, "GT"],
#              "8": ["C30-ST", 75515, "ST"],
#              "9": ["TYC-CT", 51771, "CT"],
#              "10": ["TYC-ST", 51772, "ST"],
#              "11": ["PBC-14", 50274, "14"],
#              "12": ["PBC-15", 50275, "15"],
#              "13": ["PBC-16", 50276, "16"],
#              "14": ["B31-A", 70513, "A"],
#              "15": ["B31-B", 70514, "B"],
#              "16": ["B31-C", 70515, "C"],
#              "17": ["HNC-CT", 29672, "CT"],
#              "18": ["HNC-ST", 29671, "ST"],
#              "19": ["B10", 70516, "D"],
#              "20": ["Evermore", 74518, "1"],
#              "21": ["ED1", 19471, "1"],
#              "22": ["MP1", 39471, "1"],
#              "23": ["MP2", 39472, "2"],
#              "24": ["RP1", 22671, "1"],
#              "25": ["RP2", 22672, "2"],
#              "26": ["TP1", 52476, "1"],
#              "27": ["TP3", 52477, "1"],
#              "28": ["AT1", 10472, "11"],
#              "29": ["AT2", 10473, "12"],
#              "30": ["AT4", 10474, "14"],
#              "31": ["TB3", 51473, "3"],
#              "32": ["TB4", 51474, "4"],
#              "33": ["Lumcloon", 35771, "1"],
#              "34": ["Derrycarney", 49471, "1"],
#              "35": ["Derrycarney", 49472, "1"]}
merit_order = {
             "1": ["MP3", 39473, "3"],
             "2": ["DB1", 31271, "1"],
             "3": ["HN2", 29673, "2"],
             "4": ["AD2", 10470, "1"],
             "5": ["WG1", 28571, "1"],
             "6": ["GI4", 27474, "1"],
             "7": ["C30-GT", 75516, "GT"],
             "8": ["C30-ST", 75515, "ST"],
             "9": ["TYC-CT", 51771, "CT"],
             "10": ["TYC-ST", 51772, "ST"],
             "11": ["PBC-14", 50274, "14"],
             "12": ["PBC-15", 50275, "15"],
             "13": ["PBC-16", 50276, "16"],
             "14": ["B31-A", 70513, "A"],
             "15": ["B31-B", 70514, "B"],
             "16": ["B31-C", 70515, "C"],
             "17": ["HNC-CT", 29672, "CT"],
             "18": ["HNC-ST", 29671, "ST"],
             "19": ["B10", 70516, "D"],
             "20": ["Evermore", 74518, "1"],
             "21": ["ED1", 19471, "1"],
             "22": ["MP1", 39471, "1"],
             "23": ["MP2", 39472, "2"],
             "24": ["RP1", 22671, "1"],
             "25": ["RP2", 22672, "2"],
             "26": ["TP1", 52476, "1"],
             "27": ["TP3", 52477, "1"],
             "28": ["AT1", 10472, "11"],
             "29": ["AT2", 10473, "12"],
             "30": ["AT4", 10474, "14"],
             "31": ["TB3", 51473, "3"],
             "32": ["TB4", 51474, "4"],
             "33": ["Lumcloon", 35771, "1"],
             "34": ["Derrycarney", 49471, "1"],
             "35": ["Derrycarney", 49472, "1"]}
Must_Runs_List = {"DB1", "HN2", "C30-GT", "B31-A", "B31-B"}
## Various RES categories defined by Owner
global solar_categories, onshore_categories, offshore_categories, conventional_categories
solar_categories        = [23, 45] 
onshore_categories      = [17, 18, 19, 20, 21, 22, 42, 43, 44]
offshore_categories     = [16, 41]
conventional_categories = [8, 9, 10, 11, 12]

####################################################################################
##                              END OF USER INPUT                                 ##
####################################################################################

no_of_units = 0
for k, v in merit_order.items(): no_of_units += 1
print "\nMerit order check: no. of units =", no_of_units

####################################################################################
##                            DEFINE SOME FUNCTIONS                               ##
####################################################################################

import os
import string
import win32com.client

## Define source files for future projects/generation
import glob
print "\nIdentified the following input files:"
tytfs_file_name = str(glob.glob("*Network*Data.xlsx")[0])
print " -", tytfs_file_name
generation_file_name = str(glob.glob("Renewable*Generators*.xlsx")[0])
print " -", generation_file_name

global ie_zones, ni_zones, ai_zones
ie_zones = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
ni_zones = [13, 14]
ai_zones = ie_zones + ni_zones

global res_categories

filelocation = os.getcwd()


## Make model adjustments to the published EirGrid model
## =====================================================
def make_fixes_to_eirgrid_model(each_raw_file):

    ## Switch out the cross-border PSTs
    err_sbn = psspy.branch_chng(3581,89516,r"""1""",[0],[])
    err_enk = psspy.branch_chng(1981,79016,r"""1""",[0],[])
    if err_sbn == 0 and err_enk == 0:
        print "\nThe cross-border PSTs are open - this is a good assumption!"
    else:
        print "\nWarning! There may be an issue with the cross-border PSTs! Please investigate!"

    ## Remove DC link representation of Moyle + correct PMIN issue coming from PLANET  
    psspy.movemac(86221,r"""1""",86220,r"""1""")
    psspy.machine_chng_2(86220,r"""1""",[_i,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,-400.0,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])
    psspy.two_terminal_dc_line_data(r"""1""",[0,_i],[_f,_f,_f,_f,_f,_f,_f,_f],r"""R""")
    psspy.two_terminal_dc_line_data(r"""2""",[0,_i],[_f,_f,_f,_f,_f,_f,_f,_f],r"""R""")
    psspy.machine_chng_2(86220,r"""1""",[_i,_i,_i,_i,_i,_i],[_f,_f,0.0,0.0])
    psspy.dscn(86221)
    psspy.switched_shunt_chng_3(86220,[_i,_i,_i,_i,_i,_i,_i,_i,2],[],_s)

    ## Fix Belcamp area number
    psspy.bus_chng_3(1472,[_i,2,_i,_i],[_f,_f,_f,_f,_f,_f,_f],_s)

    ## Fix Greenlink capacity
    psspy.machine_chng_2(3662,r"""1""",[],[_f,_f,_f,_f,_f,-500.0])
    psspy.bus_chng_3(3662,[],[],r"""GREENLINK""")
    psspy.machine_chng_2(3662,r"""1""",[_i,_i,_i,_i,_i,2],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f, 0.95])

    ## Remove dated Oriel model
    psspy.purgmac(67086, "OS")

    ## Sliabh Bawn Voltage Fix
    psspy.plant_data(66095,_i,[ 1.065,_f])
    psspy.switched_shunt_chng_3(66095,[_i,_i,_i,_i,_i,_i,_i,_i,0,66094,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f, 15.0,_f],_s)
    psspy.two_winding_chng_4(66094,66095,r"""1""",[_i,_i,_i,_i,_i,_i,_i,_i,_i,66094,-1,_i,_i,_i,_i], \
                             [_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f, 1.065,_f,_f,_f,_f],[r"""SLIABH B""",""])

    psspy.machine_chng_2(53071,r"""XX""",[0,_i,_i,_i,_i,0],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f, 1.0]) ## Thurles STATCOM fix [KC]
   
    if alter_2029_case:

        print "\n ***** Fixing issues in 2029 cases *****"
        if "wp" in each_raw_file.lower():

            ## Dublin voltage correction - WP only
            psspy.plant_data(54630,_i,[ 1.055,_f])
            psspy.plant_data(31271,_i,[ 1.065,_f])
            psspy.plant_data(29673,_i,[ 1.072,_f])

            ## Reduce Whitegate output to bring on TH for peak (TH at 75 MW) - WP only
            ## psspy.machine_chng_2(28571,r"""1""",[_i,_i,_i,_i,_i,_i],[ 285.0,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])
            
        elif "sp" in each_raw_file.lower():

            ## Dublin voltage correction - SP only
            psspy.plant_data(31271,_i,[ 1.055,_f])
            psspy.plant_data(29673,_i,[ 1.07,_f])
            psspy.plant_data(54630,_i,[ 1.04,_f])
            psspy.plant_data(86220,_i,[ 1.03,_f]) # Moyle correction
            psspy.switched_shunt_chng_3(17462,[_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,0,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],"") # Switch out CKM reactor for peak

            ## Reduce Whitegate output to bring on TH for peak (TH at 75 MW) - SP only
            ## psspy.machine_chng_2(28571,r"""1""",[_i,_i,_i,_i,_i,_i],[ 225.0,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])
            
        else:
            ## Dublin voltage correction - SV only
            psspy.plant_data(54630,_i,[ 1.035,_f])
            psspy.plant_data(29672,_i,[ 1.02,_f])
            psspy.plant_data(29671,_i,[ 1.02,_f])
            psspy.plant_data(29673,_i,[ 1.02,_f])
            psspy.plant_data(50274,_i,[ 1.02,_f])
            psspy.plant_data(50275,_i,[ 1.02,_f])
            psspy.plant_data(31271,_i,[ 1.018,_f]) 
    
    '''
    ## Option to make sure that Celtic is in the case
    err = psspy.bus_chng_3(5470,[2],[],_s)
    err = psspy.plant_data(5470,0,[ 1.05, 100.0])
    err = psspy.machine_data_2(5470,r"""~I""",[_i,49,_i,_i,_i,2], \
                               [0.0,_f,_f,_f, 700.0,-700.0, 750.0,_f,_f, 0.001, 0.01,_f,_f,_f,_f,_f, 0.95])

    ## Option to make sure that Greenlink is in the case
    psspy.bus_data_3(2752,[2,6,9,49],[ 220.0,_f,_f,_f,_f,_f,_f],r"""GREENLINK""")
    psspy.branch_data(2742,2752,r"""1""",[_i,_i,_i,_i,_i,_i],[_f,_f,_f, 999.0, 999.0, 999.0])
    psspy.plant_data(2752,0,[ 1.05, 100.0])
    psspy.machine_data_2(2752,r"""~I""",[_i,49,_i,_i,_i,2], \
                         [0.0,_f,_f,_f, 500.0,-500.0, 550.0,_f,_f, 0.001, 0.01,_f,_f,_f,_f,_f, 0.95])
    '''


## Function for generation re-dispatch following the addition of a load or generator
## =================================================================================
if Min_Set_units_Option == False:
    #print('YES')
    def execute_redispatch(merit_order, redispatch_target):

        import string

        print "\nExecuting redispatch of generation:"

        if redispatch_target > 0:
            print " -> Need to increase generation by:", round(redispatch_target, 1), "MW"
        else:
            print " -> Need to decrease generation by:", round(redispatch_target, 1), "MW"

        for redispatch_loop in range(1, 20):

            if redispatch_loop == 1:
                print "\nRe-dispatch loop #1: utilising the on-line plant..."
            elif abs(redispatch_target) < 50.0:
                print "\nRe-dispatch loop #1: exiting as re-dispatch is successful!"
                break
            elif redispatch_target > 50.0:
                print "\nRe-dispatch loop #" + str(redispatch_loop) + ":"
                print " - Activating off-line plant to address", round(redispatch_target, 1), "MW"
                err, generator_buses = psspy.amachint(-1, 4, 'NUMBER')
                err, generator_status = psspy.amachint(-1, 4, 'STATUS')
                err, generator_types = psspy.amachint(-1, 4, 'OWN1')
                err, generator_ids = psspy.amachchar(-1, 4, 'ID')
                err, generator_pmax = psspy.amachreal(-1, 4, 'PMAX')
                err, generator_pmin = psspy.amachreal(-1, 4, 'PMIN')
                err, generator_pgen = psspy.amachreal(-1, 4, 'PGEN')
                for gen_bus, gen_id, gen_type, gen_pmax, gen_pmin, gen_status in \
                    zip(generator_buses[0], generator_ids[0], generator_types[0], generator_pmax[0], \
                    generator_pmin[0], generator_status[0]):
                    if gen_type in conventional_categories and gen_status == 0 and gen_pmax > 95.0:
                        print " - Dispatch off-line unit", gen_id, "at bus", gen_bus
                        err = psspy.machine_chng_2(gen_bus, gen_id,[1],[0.1])
                        break

            ## Identify current schedule in case
            unit_tally = {}
            err, generator_buses = psspy.amachint(-1, 4, 'NUMBER')
            err, generator_status = psspy.amachint(-1, 4, 'STATUS')
            err, generator_types = psspy.amachint(-1, 4, 'OWN1')
            err, generator_ids = psspy.amachchar(-1, 4, 'ID')
            err, generator_pmax = psspy.amachreal(-1, 4, 'PMAX')
            err, generator_pmin = psspy.amachreal(-1, 4, 'PMIN')
            err, generator_pgen = psspy.amachreal(-1, 4, 'PGEN')

            if debug: print "\nCheck on dispatch of large units"

            for gen_bus, gen_id, gen_type, gen_pmax, gen_pmin, gen_status, gen_pgen in \
                zip(generator_buses[0], generator_ids[0], generator_types[0], generator_pmax[0], \
                generator_pmin[0], generator_status[0], generator_pgen[0]):

                if gen_type in conventional_categories and gen_pgen > 0.0 and gen_pmax >= 70.0:

                    ## Schedule with what is defined in the merit order
                    for k, v in merit_order.items():
                        #print v[0]
                        if gen_bus in v and string.rstrip(string.lstrip(gen_id)) in v:

                            ## Ensure that out-of-service machines are not dispatched!
                            if gen_status == 0:
                                psspy.machine_chng_2(gen_bus, gen_id,[0],[0.0])
                                if debug: print " -", v[0], "0.0 MW"
                                unit_tally[v[0]] = 0.0
                            else:
                                if debug: print " -", v[0], round(gen_pgen, 1), "MW"
                                unit_tally[v[0]] = gen_pgen
                # if len(unit_tally) == 6:
                #     print unit_tally
                #     break
            print('large units:', len(unit_tally))
            if len(unit_tally) == 0:
                print "\nOh no! No more large conventional plant to consider!"
                break

            ## Loop through the units and redispatch per user-defined merit order
            merit_order_number = 1 ## Initialise merit order count, i.e. starting at "1" means starting at merit order list entry
            stop_tolerance = 5.0 ## Stop redispatching once we've reached a small generation/demand imbalance
            conventional_cap_factor = 0.975 ## to prevent a machine reaching a Pmax limit - set to 1.0 to allow machines to reach Pmax
            while merit_order_number <= len(merit_order):

                if redispatch_target > 0.0 and abs(redispatch_target) > stop_tolerance:# and merit_order[str(merit_order_number)][0] not in List_Gen_Not_dispatch:

                    if debug: print "\nNeed to increase generation by", round(redispatch_target), "MW"
                    try:
                        if debug: print "    - Consider:", merit_order[str(merit_order_number)][0]
                    except:
                        if debug: print "\n    - Merit order not available:", merit_order_number
                        merit_order_number += 1
                        continue

                    ## Is the units on?
                    if merit_order[str(merit_order_number)][0] in unit_tally:
                        pgen = round(unit_tally[merit_order[str(merit_order_number)][0]], 1)
                        if debug: print "    - Pgen:", pgen, "MW"
                    else:
                        pgen = 0.0
                        if debug:
                            print "    - Pgen:", pgen, "MW"
                        if not use_mobu_merit_order:
                            merit_order_number += 1
                            continue

                    ## Unit capability - i.e. get Pmin & Pmax
                    err, pmin = psspy.macdat(merit_order[str(merit_order_number)][1], \
                                             merit_order[str(merit_order_number)][2], "PMIN")
                    err, pmax = psspy.macdat(merit_order[str(merit_order_number)][1],\
                                             merit_order[str(merit_order_number)][2], "PMAX")
                    if err in [1, 2]:
                        if debug: print "    - Skip: Unit does not appear to be in the case"
                        merit_order_number += 1
                        continue

                    pmax = pmax * conventional_cap_factor
                    if debug: print "    - Range:", round(pmin, 1), "to", round(pmax, 1), "MW"

                    ## Determine schedule change capability for the unit
                    if pgen < pmax:
                        if debug: print "    - Availability:", round(pmax - pgen, 1), "MW"
                        if pmax - pgen < redispatch_target:
                            delta_pgen = round(pmax - pgen, 1)
                        else:
                            delta_pgen = round(redispatch_target, 1)

                            ## Skip dispatch if can't reach Pmin
                            if pgen + delta_pgen < pmin:
                                if debug: print "    - Skip: pgen is less than pmax"
                                merit_order_number += 1
                                continue

                        if debug: print "    - Increase:", delta_pgen, "MW"
                        new_dispatch = round(pgen + delta_pgen, 1)
                        if debug: print "    - New dispatch:", new_dispatch, "MW"

                        ## Make the change in the model
                        err = psspy.machine_chng_2(merit_order[str(merit_order_number)][1], \
                                                   merit_order[str(merit_order_number)][2], \
                                                   [1],[new_dispatch])
                        if err != 0:
                            print "***** Warning! Error when making change to dispatch! *****"
                        else:
                            if debug: print "    - Confirmed dispatch of", merit_order[str(merit_order_number)][0], \
                               "to", new_dispatch, "MW"

                        unit_tally[merit_order[str(merit_order_number)][0]] = new_dispatch
                        redispatch_target -= round(delta_pgen, 1)

                    else:
                        ## Skip dispatch because, maybe(!), Pgen > Pmax
                        if debug: print "    - Skip: dispatch capability is not sufficient"

                    if debug: print "    - Energy imbalance:", round(redispatch_target, 0), "MW"

                if abs(redispatch_target) < stop_tolerance:
                    break

                merit_order_number += 1

            ## Loop through the units and redispatch per user-defined merit order
            merit_order_number = len(merit_order) ## Initialise merit order count, i.e. starting at "1" means starting at merit order list entry
            while merit_order_number >= 1:

                if redispatch_target < 0 and abs(redispatch_target) > stop_tolerance:# and merit_order[str(merit_order_number)][0] not in List_Gen_Not_dispatch:

                    print "\nNeed to decrease generation by", round(redispatch_target, 1), "MW"
                    try:
                        if debug: print "    - Consider:", merit_order[str(merit_order_number)][0]
                        if merit_order[str(merit_order_number)][0].lower() in ['ewic', 'moyle', 'celtic', 'greenlink']:
                            conventional_cap_factor = 1.0   ## Allow full range of interconnection capability
                        else:
                            conventional_cap_factor = 0.975 ## Prevent machines from reaching PMAX
                    except:
                        if debug: print "\n    - Merit order not available:", merit_order_number
                        merit_order_number -= 1
                        continue

                    ## Is the unit on?
                    if merit_order[str(merit_order_number)][0] in unit_tally:
                        pgen = round(unit_tally[merit_order[str(merit_order_number)][0]], 1)
                        if debug: print "    - Pgen:", pgen, "MW"
                    else:
                        pgen = 0.0
                        if debug: print "    - Pgen:", pgen, "MW"

                    ## Unit capability - i.e. get Pmin & Pmax
                    err_a, pmin = psspy.macdat(merit_order[str(merit_order_number)][1], \
                                             merit_order[str(merit_order_number)][2], "PMIN")
                    err_b, pmax = psspy.macdat(merit_order[str(merit_order_number)][1],\
                                             merit_order[str(merit_order_number)][2], "PMAX")
                    if err_a in [1, 2] or err_b in [1, 2]:
                        if debug: print "    - Not able to identify this machine - it may not be added yet"
                        merit_order_number -= 1
                        continue
                    else:
                        pmax = pmax * conventional_cap_factor
                        if debug: print "    - Range:", round(pmax, 1), "to", round(pmin, 1), "MW"

                    ## Determine schedule change capability for the unit
                    if pgen > 0:
                        if debug: print "    - Availability:", round(pgen, 1), "MW"
                        if pgen > abs(redispatch_target):
                            if debug: print "    - Decrease:", round(redispatch_target, 1), "MW"
                            new_dispatch = round(pgen - abs(redispatch_target), 1)
                            delta_pgen = redispatch_target
                        else:
                            if debug: print "    - Decrease:", round(round(pgen, 1), 1), "MW"
                            new_dispatch = round(0.0, 1)
                            delta_pgen = pgen * -1.0

                        if debug: print "    - New dispatch:", new_dispatch, "MW"

                        ## Make the change in the model
                        err = psspy.machine_chng_2(merit_order[str(merit_order_number)][1], \
                                                   merit_order[str(merit_order_number)][2], \
                                                   [1],[new_dispatch])
                        if err != 0:
                            print "***** Warning! Error when making change to dispatch! *****"
                        else:
                            if debug:
                                print "    - Confirmed dispatch of", merit_order[str(merit_order_number)][0], \
                                      "to", new_dispatch, "MW"

                        unit_tally[merit_order[str(merit_order_number)][0]] = new_dispatch
                        redispatch_target -= round(delta_pgen, 1)
                    else:
                        ## Skip dispatch because, maybe(!), Pgen > Pmax
                        if debug: print "    - Skip: dispatch capability is not sufficient"

                    if debug: print "    - Energy imbalance:", round(redispatch_target, 0), "MW"

                if abs(redispatch_target) < stop_tolerance:
                    break

                merit_order_number -= 1

        err = psspy.rawd_2(0,1,[1,1,1,0,0,0,0],0, filelocation + "\\Simulation " + \
                           time_stamp + "\\Debug\\case_after_res-change_and_re-dispatch.raw")

        return redispatch_target
## Execute Dispatch for Min_Set_units:
## =============================
if Min_Set_units_Option == True:
    print "YES"
    def execute_redispatch(merit_order, redispatch_target):

        import string

        print "\nExecuting redispatch of generation:"

        if redispatch_target > 0:
            print " -> Need to increase generation by:", round(redispatch_target, 1), "MW"
        else:
            print " -> Need to decrease generation by:", round(redispatch_target, 1), "MW"

        for redispatch_loop in range(1, 20):

            if redispatch_loop == 1:
                print "\nRe-dispatch loop #1: utilising the on-line plant..."
            elif abs(redispatch_target) < 50.0:
                print "\nRe-dispatch loop #1: exiting as re-dispatch is successful!"
                break
            elif redispatch_target > 50.0:
                print "\nRe-dispatch loop #" + str(redispatch_loop) + ":"
                print " - Activating off-line plant to address", round(redispatch_target, 1), "MW"
                err, generator_buses = psspy.amachint(-1, 4, 'NUMBER')
                err, generator_status = psspy.amachint(-1, 4, 'STATUS')
                err, generator_types = psspy.amachint(-1, 4, 'OWN1')
                err, generator_ids = psspy.amachchar(-1, 4, 'ID')
                err, generator_pmax = psspy.amachreal(-1, 4, 'PMAX')
                err, generator_pmin = psspy.amachreal(-1, 4, 'PMIN')
                err, generator_pgen = psspy.amachreal(-1, 4, 'PGEN')
                for gen_bus, gen_id, gen_type, gen_pmax, gen_pmin, gen_status in \
                        zip(generator_buses[0], generator_ids[0], generator_types[0], generator_pmax[0], \
                            generator_pmin[0], generator_status[0]):
                    if gen_type in conventional_categories and gen_status == 0 and gen_pmax > 95.0:
                        print " - Dispatch off-line unit", gen_id, "at bus", gen_bus
                        err = psspy.machine_chng_2(gen_bus, gen_id, [1], [0.1])
                        break

            ## Identify current schedule in case
            unit_tally = {}
            err, generator_buses = psspy.amachint(-1, 4, 'NUMBER')
            err, generator_status = psspy.amachint(-1, 4, 'STATUS')
            err, generator_types = psspy.amachint(-1, 4, 'OWN1')
            err, generator_ids = psspy.amachchar(-1, 4, 'ID')
            err, generator_pmax = psspy.amachreal(-1, 4, 'PMAX')
            err, generator_pmin = psspy.amachreal(-1, 4, 'PMIN')
            err, generator_pgen = psspy.amachreal(-1, 4, 'PGEN')

            if debug: print "\nCheck on dispatch of large units"

            for gen_bus, gen_id, gen_type, gen_pmax, gen_pmin, gen_status, gen_pgen in \
                    zip(generator_buses[0], generator_ids[0], generator_types[0], generator_pmax[0], \
                        generator_pmin[0], generator_status[0], generator_pgen[0]):

                if gen_type in conventional_categories and gen_pgen > 0.0 and gen_pmax >= 70.0:

                    ## Schedule with what is defined in the merit order
                    for k, v in merit_order.items():
                        # print v[0]
                        if gen_bus in v and string.rstrip(string.lstrip(gen_id)) in v:

                            ## Ensure that out-of-service machines are not dispatched!
                            if gen_status == 0:
                                psspy.machine_chng_2(gen_bus, gen_id, [0], [0.0])
                                if debug: print " -", v[0], "0.0 MW"
                                unit_tally[v[0]] = 0.0
                            else:
                                if debug: print " -", v[0], round(gen_pgen, 1), "MW"
                                unit_tally[v[0]] = gen_pgen
                # if len(unit_tally) == 6:
                #     print unit_tally
                #     break
            print('large units:', len(unit_tally))
            if len(unit_tally) == 0:
                print "\nOh no! No more large conventional plant to consider!"
                break

            ## Loop through the units and redispatch per user-defined merit order
            merit_order_number = 1  ## Initialise merit order count, i.e. starting at "1" means starting at merit order list entry
            stop_tolerance = 5.0  ## Stop redispatching once we've reached a small generation/demand imbalance
            conventional_cap_factor = 0.975  ## to prevent a machine reaching a Pmax limit - set to 1.0 to allow machines to reach Pmax
            while merit_order_number <= len(merit_order):

                if redispatch_target > 0.0 and abs(
                        redispatch_target) > stop_tolerance:  # and merit_order[str(merit_order_number)][0] not in List_Gen_Not_dispatch:

                    if debug: print "\nNeed to increase generation by", round(redispatch_target), "MW"
                    try:
                        if debug: print "    - Consider:", merit_order[str(merit_order_number)][0]
                    except:
                        if debug: print "\n    - Merit order not available:", merit_order_number
                        merit_order_number += 1
                        continue

                    ## Is the units on?
                    if merit_order[str(merit_order_number)][0] in unit_tally:
                        pgen = round(unit_tally[merit_order[str(merit_order_number)][0]], 1)
                        if debug: print "    - Pgen:", pgen, "MW"
                    elif merit_order[str(merit_order_number)][0] not in unit_tally and merit_order[str(merit_order_number)][0] in Must_Runs_List:
                        err, pmin = psspy.macdat(merit_order[str(merit_order_number)][1], \
                                                 merit_order[str(merit_order_number)][2], "PMIN")
                        pgen = pmin
                        if debug: print "    - Pgen:", pgen, "MW"
                    else:
                        pgen = 0.0
                        if debug:
                            print "    - Pgen:", pgen, "MW"
                        if not use_mobu_merit_order:
                            merit_order_number += 1
                            continue

                            ## Unit capability - i.e. get Pmin & Pmax
                    err, pmin = psspy.macdat(merit_order[str(merit_order_number)][1], \
                                             merit_order[str(merit_order_number)][2], "PMIN")
                    err, pmax = psspy.macdat(merit_order[str(merit_order_number)][1], \
                                             merit_order[str(merit_order_number)][2], "PMAX")
                    if err in [1, 2]:
                        if debug: print "    - Skip: Unit does not appear to be in the case"
                        merit_order_number += 1
                        continue

                    pmax = pmax * conventional_cap_factor
                    if debug: print "    - Range:", round(pmin, 1), "to", round(pmax, 1), "MW"

                    ## Determine schedule change capability for the unit
                    if pgen < pmax:
                        if debug: print "    - Availability:", round(pmax - pgen, 1), "MW"
                        if pmax - pgen < redispatch_target:
                            delta_pgen = round(pmax - pgen, 1)
                        else:
                            delta_pgen = round(redispatch_target, 1)

                            ## Skip dispatch if can't reach Pmin
                            if pgen + delta_pgen < pmin:
                                if debug: print "    - Skip: pgen is less than pmin"
                                merit_order_number += 1
                                continue

                        if debug: print "    - Increase:", delta_pgen, "MW"
                        new_dispatch = round(pgen + delta_pgen, 1)
                        if debug: print "    - New dispatch:", new_dispatch, "MW"

                        ## Make the change in the model
                        err = psspy.machine_chng_2(merit_order[str(merit_order_number)][1], \
                                                   merit_order[str(merit_order_number)][2], \
                                                   [1], [new_dispatch])
                        if err != 0:
                            print "***** Warning! Error when making change to dispatch! *****"
                        else:
                            if debug: print "    - Confirmed dispatch of", merit_order[str(merit_order_number)][0], \
                                "to", new_dispatch, "MW"

                        unit_tally[merit_order[str(merit_order_number)][0]] = new_dispatch
                        redispatch_target -= round(delta_pgen, 1)

                    else:
                        ## Skip dispatch because, maybe(!), Pgen > Pmax
                        if debug: print "    - Skip: dispatch capability is not sufficient"

                    if debug: print "    - Energy imbalance:", round(redispatch_target, 0), "MW"

                if abs(redispatch_target) < stop_tolerance:
                    break

                merit_order_number += 1

            ## Loop through the units and redispatch per user-defined merit order
            merit_order_number = len(
                merit_order)  ## Initialise merit order count, i.e. starting at "1" means starting at merit order list entry
            while merit_order_number >= 1:

                if redispatch_target < 0 and abs(
                        redispatch_target) > stop_tolerance:  # and merit_order[str(merit_order_number)][0] not in List_Gen_Not_dispatch:

                    print "\nNeed to decrease generation by", round(redispatch_target, 1), "MW"
                    try:
                        if debug: print "    - Consider:", merit_order[str(merit_order_number)][0]
                        if merit_order[str(merit_order_number)][0].lower() in ['ewic', 'moyle', 'celtic', 'greenlink']:
                            conventional_cap_factor = 1.0  ## Allow full range of interconnection capability
                        else:
                            conventional_cap_factor = 0.975  ## Prevent machines from reaching PMAX
                    except:
                        if debug: print "\n    - Merit order not available:", merit_order_number
                        merit_order_number -= 1
                        continue

                    ## Is the unit on?
                    if merit_order[str(merit_order_number)][0] in unit_tally:
                        pgen = round(unit_tally[merit_order[str(merit_order_number)][0]], 1)
                        if debug: print "    - Pgen:", pgen, "MW"
                    elif merit_order[str(merit_order_number)][0] in Must_Runs_List:
                        err_a, pmin = psspy.macdat(merit_order[str(merit_order_number)][1], \
                                                   merit_order[str(merit_order_number)][2], "PMIN")
                        pgen = pmin
                        if debug: print "    - Pgen:", pgen, "MW"
                    else:
                        pgen = 0.0
                        if debug: print "    - Pgen:", pgen, "MW"

                    ## Unit capability - i.e. get Pmin & Pmax
                    err_a, pmin = psspy.macdat(merit_order[str(merit_order_number)][1], \
                                               merit_order[str(merit_order_number)][2], "PMIN")
                    err_b, pmax = psspy.macdat(merit_order[str(merit_order_number)][1], \
                                               merit_order[str(merit_order_number)][2], "PMAX")
                    if err_a in [1, 2] or err_b in [1, 2]:
                        if debug: print "    - Not able to identify this machine - it may not be added yet"
                        merit_order_number -= 1
                        continue
                    else:
                        pmax = pmax * conventional_cap_factor
                        if debug: print "    - Range:", round(pmax, 1), "to", round(pmin, 1), "MW"

                    ## Determine schedule change capability for the unit
                    if pgen > 0:
                        if debug: print "    - Availability:", round(pgen, 1), "MW"
                        if pgen > abs(redispatch_target) and merit_order[str(merit_order_number)][0] not in Must_Runs_List:
                            if debug: print "    - Decrease:", round(redispatch_target, 1), "MW"
                            new_dispatch = round(pgen - abs(redispatch_target), 1)
                            delta_pgen = redispatch_target
                        elif pgen > abs(redispatch_target) and merit_order[str(merit_order_number)][0] in Must_Runs_List:
                            if debug: print "    - Decrease:", round(redispatch_target, 1), "MW"
                            if pgen > pmin and pgen - pmin >= pmin:
                               new_dispatch = round(pgen - pmin, 1)
                               delta_pgen = redispatch_target
                            else:
                               new_dispatch = pmin
                               delta_pgen = redispatch_target
                        elif pgen < abs(redispatch_target) and merit_order[str(merit_order_number)][0] not in Must_Runs_List:
                            if debug: print "    - Decrease:", round(round(pgen, 1), 1), "MW"
                            new_dispatch = round(0.0, 1)
                            delta_pgen = pgen * -1.0
                        elif pgen < abs(redispatch_target) and merit_order[str(merit_order_number)][0] in Must_Runs_List:
                            if debug: print "    - Decrease:", round(round(pgen, 1), 1), "MW"
                            new_dispatch = round(pmin, 1)
                            delta_pgen = pgen * -1.0
                        if debug: print "    - New dispatch:", new_dispatch, "MW"

                        ## Make the change in the model
                        err = psspy.machine_chng_2(merit_order[str(merit_order_number)][1], \
                                                   merit_order[str(merit_order_number)][2], \
                                                   [1], [new_dispatch])
                        if err != 0:
                            print "***** Warning! Error when making change to dispatch! *****"
                        else:
                            if debug:
                                print "    - Confirmed dispatch of", merit_order[str(merit_order_number)][0], \
                                    "to", new_dispatch, "MW"

                        unit_tally[merit_order[str(merit_order_number)][0]] = new_dispatch
                        redispatch_target -= round(delta_pgen, 1)
                    else:
                        ## Skip dispatch because, maybe(!), Pgen > Pmax
                        if debug: print "    - Skip: dispatch capability is not sufficient"

                    if debug: print "    - Energy imbalance:", round(redispatch_target, 0), "MW"

                if abs(redispatch_target) < stop_tolerance:
                    break

                merit_order_number -= 1

        err = psspy.rawd_2(0, 1, [1, 1, 1, 0, 0, 0, 0], 0, filelocation + "\\Simulation " + \
                           time_stamp + "\\Debug\\case_after_res-change_and_re-dispatch.raw")

        return redispatch_target


## Simple solution for load-flow
## =============================
def general_model_solution():

    print "\nSolving the powerflow..."

    solution_iterations = 10

    ## Flat start - with FDNS, shunts enabled, transformers locked and Mvars applied immediately
    psspy.fdns([0,0,0,0,1,1,0,0])
    
    for solution_tries in range(0, solution_iterations):

        if adjust_transformer_taps:
            psspy.fdns([1,0,1,0,0,0,0,0]) ## Only allow transformer tapping & phase shift adjustment
        psspy.fdns([0,0,0,0,1,0,0,0]) ## Only allow/enable all shunts
        if adjust_transformer_taps:
            psspy.fdns([1,0,1,0,1,0,0,0]) ## Allow transformers, PSTs & all shunts
        mis = psspy.sysmsm()
        if debug: print str(solution_tries + 1) + ". Mismatch:", round(mis, 3), "MVA" 
        if mis < system_mismatch_target:
            print "\nSolution indication is awesome! Mismatch:", round(mis, 3), "MVA" 
            break

    return mis


## Function that performs basic script set-up tasks
## ================================================
def run_inital_setup_activities(): 

    ## Identify the location/path of the PSSE installation
    import os
    import sys
    filelocation = os.getcwd()
    psse_location = r"C:\\Program Files (x86)\\PTI\\PSSE33\\PSSBIN\\"
    sys.path.append(psse_location)
    os.environ['PATH'] = os.environ['PATH'] + ';' + psse_location

    ## Initialise the PSSE application
    global psspy
    global pssarrays

    import psspy
    import pssarrays
    import redirect

    redirect.psse2py()
    bus_dimension = 150000 ## From POM: 1K, 4K, 12K, 50K or 150K 
    init_err = psspy.psseinit(buses = bus_dimension)

    ## Initialise the three variable types
    global _i, _f, _s
    _i = psspy.getdefaultint()
    _f = psspy.getdefaultreal()
    _s = psspy.getdefaultchar()

    return psspy, pssarrays, _i, _f, _s


## Function that reads the various available *.raw files
## Usually expecting the following:
##  - summer peak;
##  - summer valley; and
##  - winter peak
## =====================================================
def read_raw_files_in_working_folder():

    import glob
    initial_list_of_raw_files = glob.glob("*.raw")

    print "\nThe following *.raw files have been detected for analysis:"
    list_of_raw_files = []
    for ilorf in initial_list_of_raw_files:

        ## Don't want to update files that are ALREADY updated! 
        if 'mobu' in ilorf.lower() or 'solution' in ilorf.lower() or 'issue' in ilorf.lower() or \
           'case_before' in ilorf.lower() or 'case_after' in ilorf.lower() or 'connectivity' in ilorf.lower():
            if debug: print "[Not assessing: " + ilorf + "]" 
            continue           
        else:
            list_of_raw_files.append(ilorf)
            print "", chr(27), ilorf

    return list_of_raw_files 


## This function adds a new branch to the grid model
## =================================================
def add_a_new_circuit(add_circuits_dict):

    print "\nAdding branch data as follows:"

    ## Impedance data
    rxb_data = {    
                'ohl': {'110.0': [0.000628, 0.003248, 0.000352], 
                        '220.0': [0.000135868, 0.000853512, 0.001357857],             
                        '380.0': [0.000019, 0.000222,	0.005047]
                        }, 
                'ugc': {'110.0': [0.0003, 0.001, 0.011],           ## Based on 1000 XLPE Cu from PLANET
                        '220.0': [0.00002, 0.000389, 0.02737],     ## Based on 1600 XLPE Cu from PLANET [Planet: 0.000032, 0.000389, 0.02737]
                        '380.0': [0.000003, 0.00001, 0.035],       ## JK estimate - to be updated
                        }
                }

    ## Rating data
    rating_data = {
        
        'ohl': {
            '110.0': {'summer': 178.0, 'winter': 210.0, 'autumn': 194.0, 'type': "430 mm2 ACSR 'Bison'"},
            '220.0': {'summer': 434.0, 'winter': 513.0, 'autumn': 474.0, 'type': "600 mm2 ACSR 'Curlew'"},
            ##'220_uprate': {'summer': 793.0, 'winter': 824.0, 'autumn': 808.0, 'type': "586 mm2 GZTACSR 'Traonach'"},
            '380.0': {'summer': 1578.0, 'winter': 1867.0, 'autumn': 1722.0, 'type': "2 x 600 mm2 ACSR 'Curlew'"}        
                },
        'ugc': {
            '110.0': {'summer': 196.0, 'winter': 221.0, 'autumn': 202.0, 'type': '1000 mm2 Cu XLPE'}, ## assumed trefoil duct formation
            '220.0': {'summer': 537.0, 'winter': 606.0, 'autumn': 556.0, 'type': '1600 mm2 Cu XLPE'}, ## assumed direct buried flat formation        
            '380.0': {'summer': 1218.0, 'winter': 1377.0, 'autumn': 1264.0, 'type': '2500 mm2 Cu XLPE'} ## assumed flat formation
                }
        }

    for each_circuit_name, circuit_details in add_circuits_dict.items():

        if circuit_details[4] not in ['ohl', 'ugc']:
            print "\nError with branch technology! Please review:", circuit_details[4]
            quit()
        else:
            print "", chr(27), each_circuit_name
            
        ## Check that base voltages area ok
        err_i, base_i = psspy.busdat(circuit_details[0], 'BASE')
        err_j, base_j = psspy.busdat(circuit_details[1], 'BASE')
        if err_i != 0 and err_j == 0:
            print "\nError with branch details! Please review!"
            quit()

        if base_i == base_j:
            print "     Buses have same base voltage - therefore proceeding to add branch..."
            err = psspy.branch_data(circuit_details[0], circuit_details[1], circuit_details[2], [], \
                                      [circuit_details[3] * rxb_data[circuit_details[4]][str(base_i)][0], \
                                       circuit_details[3] * rxb_data[circuit_details[4]][str(base_i)][1], \
                                       circuit_details[3] * rxb_data[circuit_details[4]][str(base_i)][2], \
                                       rating_data[circuit_details[4]][str(base_i)]['summer'], \
                                       rating_data[circuit_details[4]][str(base_i)]['summer'], \
                                       rating_data[circuit_details[4]][str(base_i)]['summer'], \
                                       _f,_f,_f,_f, circuit_details[3]])
            if err != 0:
                print "\nError creating circuit that connects buses", circuit_details[0], "and", circuit_details[1]
            else:
                print "     Successfully added branch", circuit_details[2], "connecting buses", circuit_details[0], "and", circuit_details[1]
        else:
            print "\nError! Buses do not have the same base voltage! Please review inputs!"
            quit()

            
## Add a new substation
## ====================
def add_a_new_station(add_stations_dict):

    print "\nAdding a new station as follows:"

    for each_station_name, station_details in add_stations_dict.items():

        print "", chr(27), each_station_name

        ## Check that base voltages area ok
        err_i, base_i = psspy.busdat(station_details[1], 'BASE')
        err_j, base_j = psspy.busdat(station_details[2], 'BASE')
        if err_i != 0 and err_j == 0:            
            print "\nError with branch details! Please review!"
            quit()

        ## Create a looped-in station
        print "\nCreating a loop-in station between buses", station_details[0], \
                    "and", station_details[1]
        err = psspy.ltap(station_details[1], station_details[2], station_details[3], \
                         station_details[4], station_details[0], each_station_name, base_i)
        if err != 0:
            print "     Error", err, "creating station at bus", station_details[0], \
                  "- check if circuit exists?"
            quit()
        else:
            print "     Successfully added station at bus", station_details[0], \
                  station_details[4] * 100.0, "% distant from bus numer", station_details[1]
            

## Function that adds user-defined loads at existing nodes
## =======================================================
def add_load_to_an_existing_station(add_loads_dict):

    import math
    
    print "\nAdding load data as follows:"
    
    define_a_new_bus = True
    rating_of_load_circuit = 999.0
    r, x, b = 0.001, 0.01, 0.01 
    bus_code_type = 1
    
    for each_load_name, load_details in add_loads_dict.items():
        #connection_increment = load_details[2] #KC only if not an incremental connection
        print "", chr(27), each_load_name

        redispatch_remainder = execute_redispatch(merit_order, connection_increment)

        if define_a_new_bus:
            
            new_load_bus_number = int(str(load_details[0]) + "88")
            
            err, area_data = psspy.busint(load_details[0], "AREA")
            err, zone_data = psspy.busint(load_details[0], "ZONE")
            err, owner_data = psspy.busint(load_details[0], "OWNER")
            err, load_bus_base_kV = psspy.busdat(load_details[0], "BASE")
            if err != 0:
                print "     Error! check if bus", load_details[0], "exists! Maybe station has yet to be created?"
                quit()

            ## Adding station model
            err = psspy.bus_data_3(new_load_bus_number,[bus_code_type, area_data, zone_data, owner_data], \
                                   [load_bus_base_kV, 1.0, 0.0, 1.091, 0.9, 1.2, 0.8], each_load_name)
            if err > 0:
                print "     Error", err, "creating load bus number", new_load_bus_number
            else:
                print ""
                print "     Successfully added load bus number", new_load_bus_number
                
            err = psspy.branch_data(load_details[0], new_load_bus_number, "LD", [], \
                                      [r, x, b, rating_of_load_circuit, rating_of_load_circuit, rating_of_load_circuit])
            if err != 0:
                print "     Error creating circuit that connects buses", load_details[0], "and", new_load_bus_number
            else:
                print "     Successfully added branch connecting buses", load_details[0], "and", new_load_bus_number

            ## Determine Mvar            
            mvar_load = math.sqrt((connection_increment * connection_increment - \
                                   load_details[3] * load_details[3] * connection_increment * connection_increment) / load_details[3] * load_details[3])
            err = psspy.load_data_4(new_load_bus_number, load_details[1], [], [connection_increment, mvar_load])
            if err != 0:
                print "     Error creating load at bus", new_load_bus_number
            else:
                print "     Successfully added", connection_increment, "MW load at bus", new_load_bus_number

    return connection_increment
        

## Function that adds user-defined generators at existing nodes
## ============================================================
def add_machine_to_an_existing_station(add_any_type_of_machine_dict):

    import math
    
    print "\nAdding generator/STATCOM data as follows:"
    
    define_a_new_bus = True
    rating_of_generator_circuit = 999.0
    r, x, b = 0.001, 0.001, 0.001 
    gen_trafo_r = 0.001
    gen_trafo_x = 0.01
    bus_code_type = 2
    machine_status = 1
    pf_mode = 2

    for each_generator_name, generator_details in add_any_type_of_machine_dict.items():

        print "", chr(27), each_generator_name

        ## Determine the type of RES technology
        if 'onshore' in generator_details[5].lower():
            generator_technology = 20
            tech_name = "onshore wind farm"
        elif 'offshore' in generator_details[5].lower():
            generator_technology = 16 
            tech_name = "offshore wind farm"
        elif 'solar' in generator_details[5].lower():
            generator_technology = 23
            tech_name = "solar PV farm"
        elif 'interconnector' in generator_details[5].lower():
            generator_technology = 49
            tech_name = "interconnector"
        elif 'statcom' in generator_details[5].lower():
            generator_technology = 28
            tech_name = "statcom"
        elif 'gas turbine' in generator_details[5].lower():     #SH: define the conventional generator
            generator_technology = 30
            tech_name = "gas turbine"
        elif 'battery' in generator_details[5].lower():
            generator_technology = 14
            tech_name = "battery"

        generator_vintage = 883

        if define_a_new_bus:

            if tech_name == 'statcom':
                new_generator_bus_number = int(str(generator_details[0]) + "7")
            else:
                new_generator_bus_number = int(str(generator_details[0]) + "9")
                
            err, area_data = psspy.busint(generator_details[0], "AREA")
            err, zone_data = psspy.busint(generator_details[0], "ZONE")
            err, owner_data = psspy.busint(generator_details[0], "OWNER")
            err, generator_bus_base_kV = psspy.busdat(generator_details[0], "BASE")
            if err != 0:
                print "     Error! check if bus", generator_details[0], "exists! Maybe station has yet to be created?"
                quit()
        
            err = psspy.bus_data_3(new_generator_bus_number,[bus_code_type, area_data, zone_data, owner_data], \
                                   [generator_bus_base_kV, 1.0, 0.0, 1.091, 0.9, 1.2, 0.8], each_generator_name)
            if err > 0:
                print "     Error", err, "creating generator bus number", new_generator_bus_number
            else:
                print "     Successfully added generator bus number", new_generator_bus_number
                
            err = psspy.branch_data(generator_details[0], new_generator_bus_number, "G", [], \
                                      [r, x, b, rating_of_generator_circuit, rating_of_generator_circuit, rating_of_generator_circuit])
            if err != 0:
                print "     Error creating circuit that connects buses", generator_details[0], "and", new_generator_bus_number
            else:
                print "     Successfully added branch connecting buses", generator_details[0], "and", new_generator_bus_number

            ## Add plant data to bus
            err = psspy.plant_data(new_generator_bus_number, generator_details[0],[1.05, 100.0])
            if err != 0:
                print "     Error", err, "creating plant at bus", new_generator_bus_number
            else:
                print "     Successfully added plant data at bus", new_generator_bus_number

            ## Add machine data to bus
            if tech_name == 'statcom':
                machine_pmax = 0.0
                machine_pmin = 0.0
                machine_pgen = 0.0               
                err = psspy.machine_data_2(new_generator_bus_number, generator_details[1], [machine_status, generator_technology, generator_vintage], \
                                           [_f, _f, generator_details[4], generator_details[4] * -1.0, generator_details[2], generator_details[3], \
                                            generator_details[4] * 1.1, _f,_f, gen_trafo_r, gen_trafo_x])
                if err != 0:
                    print "     Error", err, "creating", tech_name, "at bus", new_generator_bus_number
                else:
                    print "     Successfully added", machine_pmax, "MW", tech_name, "at bus", new_generator_bus_number
            else:
                if connection_increment == 0:                    
                    machine_pmax = generator_details[2]
                    machine_pmin = generator_details[3]
                    machine_pgen = 0.0
                else:
                    machine_pmax = connection_increment
                    machine_pmin = generator_details[3]
                    machine_pgen = connection_increment
                if machine_pmax == 0.0:
                    machine_base = 1.0
                else:
                    machine_base = machine_pmax * 1.1
                    
                err = psspy.machine_data_2(new_generator_bus_number, generator_details[1], [machine_status, generator_technology, generator_vintage,_i,_i,pf_mode], \
                                           [machine_pgen, _f, _f, _f, machine_pmax, machine_pmin, \
                                            machine_base, _f,_f, gen_trafo_r, gen_trafo_x, _f,_f,_f,_f,_f, generator_details[4]])
                if err != 0:
                    print "     Error", err, "creating", tech_name, "at bus", new_generator_bus_number
                else:
                    print "     Successfully added", machine_pmax, "MW", tech_name, "at bus", new_generator_bus_number

                print "\n  -> Generation dispatch:", connection_increment, "MW"
                
                redispatch_remainder = execute_redispatch(merit_order, connection_increment * -1.0)

        ## Add extra cable connection if offshore connection is large - based on assumption that a single submarine cable is rated at c. 400 MVA
        if 'offshore' in generator_details[5].lower() and machine_pmax > 400.0 and connection_increment > 0.0: 

            ## Re-label the existing brach
            psspy.branch_chng(generator_details[0], new_generator_bus_number, r"""G""",[],[])
            psspy.mbidbrn(generator_details[0], new_generator_bus_number,r"""G""",r"""G1""")

            ## Create a second branch
            psspy.branch_data(generator_details[0], new_generator_bus_number,r"""G2""",[],[ 0.001, 0.001, 0.001, 999.0, 999.0, 999.0,_f,_f,_f,_f,_f,_f,_f,_f,_f])

            ## Seperate out the machines            
            psspy.machine_chng_2(new_generator_bus_number,r"""OS""",[],[ machine_pmax / 2.0,_f,_f,_f, machine_pmax / 2.0, _f, machine_pmax * 1.1 / 2.0,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])
            psspy.machine_data_2(new_generator_bus_number,r"""PS""",[_i,16,883,_i,_i,_i],[ machine_pmax / 2.0, _f, _f, _f, machine_pmax / 2.0,0.0, machine_pmax * 1.1 / 2.0, 0.0, 1.0, 0.001, 0.01, 1.0, 0.5, 0.5, 1.0, 1.0, 0.95])

            ## Split the generation to different buses
            extra_offshore_bus = int(str(generator_details[0]) + '8')            
            psspy.splt(new_generator_bus_number,extra_offshore_bus,each_generator_name, 220.0)
            psspy.movebrn(generator_details[0],new_generator_bus_number,r"""G2""",extra_offshore_bus,r"""G2""")
            psspy.movemac(new_generator_bus_number,r"""PS""",extra_offshore_bus,r"""PS""")
            psspy.branch_chng(new_generator_bus_number,extra_offshore_bus,r"""1""",[0],[])

    return connection_increment
        

## This function uprates all 110 kV overhead lines that are below the standard rating policy
## =========================================================================================
def uprate_110kv_lines_to_standard_ratings(operational_scenario):

    print "\nUprating the following circuits to",

    ## List to help exlude underground cables from uprating
    exlude_these_branches = []

    standard_rating_dict = {'summer': 178.0, 'winter': 210.0}

    if 'summer'in operational_scenario:
        apply_this_rating = standard_rating_dict['summer']
    else:
        apply_this_rating = standard_rating_dict['winter']

    print apply_this_rating, "MVA"

    exclude_these_areas = [1, 20] ## Dublin DSO & Northern Ireland

    err, from_brn = psspy.abrnint(-1, 1, 1, 1, 1, 'FROMNUMBER')     
    err, to_brn = psspy.abrnint(-1, 1, 1, 1, 1, 'TONUMBER')         
    err, id_brn = psspy.abrnchar(-1, 1, 1, 1, 1, 'ID')             
    err, rating = psspy.abrnreal(-1, 1, 1, 1, 1, 'RATEB')

    for a, b, c, d in zip(from_brn[0], to_brn[0], id_brn[0], rating[0]):

        ## Exlude based on voltage level
        err, a_base = psspy.busdat(a, 'BASE')
        err, b_base = psspy.busdat(b, 'BASE')
        if a_base != 110.0 or b_base != 110.0: continue

        ## Exclude based on area
        err, a_area = psspy.busint(a, 'AREA')
        err, b_area = psspy.busint(b, 'AREA')
        if a_area in exclude_these_areas or b_area == exclude_these_areas: continue
        
        ## Exclude based on bus types
        err, a_name = psspy.notona(a)
        err, b_name = psspy.notona(b)
        if "_cap" in a_name.lower() or "_cap" in b_name.lower(): continue
        if "_svc" in a_name.lower() or "_svc" in b_name.lower(): continue

        ## If the rating is not at policy standard, then uprate it
        if d < apply_this_rating * 0.9:
            err = psspy.branch_chng(a, b, c,[],[_f,_f,_f,apply_this_rating,apply_this_rating,apply_this_rating])
            if err != 0:
                print "Error changing the rating of circuit", a, b, c
            else:
                print " -", a_name, b_name, d, "->", apply_this_rating


## Function that adds user-defined generators at existing nodes
## ============================================================
def read_and_add_generation_data():

    print "\nReading new generation data..."

    import math

    ## Reading the generation data
    new_generation_dict = {}
    xls = win32com.client.gencache.EnsureDispatch("excel.application") ## Opens Excel - no workbook/worksheets
    xls.DisplayAlerts = False ## Disables prompts
    xls.Visible = True  
    wb = xls.Workbooks.Open(filelocation + '\\' + generation_file_name, UpdateLinks = False)
    ws = xls.Worksheets("Wind & Solar Nov 21")
    row, col = 2, 1
    while 1:        

        if ws.Cells(row, col).Value == None:
            break

        if str(ws.Cells(row, col + 7).Value) == "None":
            new_generation_dict[str(ws.Cells(row, col + 1).Value)] = \
                                                  [int(ws.Cells(row, col + 2).Value), str(ws.Cells(row, col + 3).Value), float(ws.Cells(row, col + 10).Value)]
        else:
            if debug:
                print " - Not considering:", str(ws.Cells(row, col + 1).Value), "from", int(ws.Cells(row, col + 7).Value)
 
        row += 1
    wb.Close()
    
    print "\nAdding generator data as follows:"
    define_a_new_bus = True
    rating_of_generator_circuit = 999.0
    r, x, b = 0.001, 0.01, 0.01 
    gen_trafo_r = 0.001
    gen_trafo_x = 0.01
    bus_code_type = 2
    machine_status = 1
    pf_mode = 2

    for each_generator_name, generator_details in new_generation_dict.items():

        generator_name_for_psse = each_generator_name[:12] 

        print "", chr(27), each_generator_name
        ## Determine the type of RES technology
        ## Define technology - solar PV or onshore wind
        if generator_details[1].lower() == "wf":
            tech_owner = 20
            tech_name = "wind"
        elif generator_details[1].lower() == "sf":
            tech_owner = 23
            tech_name = "solar"
        elif generator_details[1].lower() == "owf":
            tech_owner = 16
            tech_name = "offshore wind"

        generator_vintage = 883 

        if define_a_new_bus:

            if tech_name == "wind":
                new_generator_bus_number = int(str(generator_details[0]) + "7") # wind bus
            elif tech_name == "offshore wind":
                new_generator_bus_number = int(str(generator_details[0]) + "8") # offshore wind bus
            else:
                new_generator_bus_number = int(str(generator_details[0]) + "9") # solar bus
           
            err, area_data = psspy.busint(generator_details[0], "AREA")
            err, zone_data = psspy.busint(generator_details[0], "ZONE")
            err, owner_data = psspy.busint(generator_details[0], "OWNER")
            err, generator_bus_base_kV = psspy.busdat(generator_details[0], "BASE")
            if err != 0:
                print "     Error! check if bus", generator_details[0], "exists! Maybe station has yet to be created?"
                quit()
        
            err = psspy.bus_data_3(new_generator_bus_number,[bus_code_type, area_data, zone_data, owner_data], \
                                   [generator_bus_base_kV, 1.0, 0.0, 1.091, 0.9, 1.2, 0.8], generator_name_for_psse)
            if err > 0:
                print "     Error", err, "creating generator bus number", new_generator_bus_number
            else:
                if debug:
                    print "     Successfully added generator bus number", new_generator_bus_number
                
            err = psspy.branch_data(generator_details[0], new_generator_bus_number, "G", [], \
                                      [r, x, b, rating_of_generator_circuit, rating_of_generator_circuit, rating_of_generator_circuit])
            if err != 0:
                print "     Error creating circuit that connects buses", generator_details[0], "and", new_generator_bus_number
            else:
                if debug:
                    print "     Successfully added branch connecting buses", generator_details[0], "and", new_generator_bus_number

            ## Add plant data to bus
            err = psspy.plant_data(new_generator_bus_number, generator_details[0],[1.05, 100.0])
            if err != 0:
                print "     Error", err, "creating plant at bus", new_generator_bus_number
            else:
                if debug:
                    print "     Successfully added plant data at bus", new_generator_bus_number

            ## Add machine data to bus
            if tech_name == "wind" or tech_name == "solar" or tech_name == "offshore wind": #add if wind or solar
                          
                machine_pmax = generator_details[2]
                machine_pmin = 0.0
                machine_pgen = 0.0
                    
                err = psspy.machine_data_2(new_generator_bus_number,r"""1""",[_i,tech_owner,_i,_i,_i,2], \
                                   [0.0,0.0, 9999.0,-9999.0, generator_details[2], 0, generator_details[2] * 1.1,0.0, 1.0,0.0,0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.95])
                if err != 0:
                    print "     Error", err, "creating", tech_name, "at bus", new_generator_bus_number
                else:
                    if debug:
                        print "     Successfully added", machine_pmax, "MW", tech_name, "at bus", new_generator_bus_number


## Add base case data via Excel input - derived from a recent Ten Year Forecast Statement
## This data should align with the assumptions of the study in question
## ======================================================================================
def read_base_case_data(debug, tytfs_file_name):

    import os; filelocation = os.getcwd()

    base_case_changes_dict = {}
    
    xls_1 = win32com.client.gencache.EnsureDispatch("excel.application")
    xls_1.DisplayAlerts = False
    xls_1.Visible = True
    wb_1 = xls_1.Workbooks.Open(filelocation + "\\" + tytfs_file_name, UpdateLinks = False)
    ws_1 = xls_1.Worksheets("Network_Data")
    row, col = 2, 1
    while 1:        
        if ws_1.Cells(row, col).Value == None:
            break
        else:
            ## Description of grid change
            grid_element       = str(ws_1.Cells(row, col + 3).Value)
            if debug: print "\nGrid element:", grid_element 
            type_of_change     = str(ws_1.Cells(row, col + 2).Value)
            if debug: print " - Type of element:", type_of_change 
            ## From bus number
            try: i_bus         = int(ws_1.Cells(row, col + 5).Value)
            except: i_bus      = 0
            if debug: print " - To bus:", i_bus
            ## To bus number
            try: j_bus         = int(ws_1.Cells(row, col + 6).Value)
            except: j_bus      = 0
            if debug: print " - From bus:", j_bus
            ## Third bus number - for tertiary winding of transformers
            try: k_bus         = int(ws_1.Cells(row, col + 7).Value)
            except: k_bus      = 0
            if debug: print " - Tertiary bus (if required):", k_bus
            ## Circuit identifier
            try:
                cct_id = str(int(ws_1.Cells(row, col + 4).Value))
                if cct_id == "None": cct_id = "1"
                if debug: print " - Circuit identifier:", cct_id
            except:
                cct_id     = "1"
                if debug: print " - Circuit identifier:", cct_id
            ## Ratings
            try: sum_rating    = float(ws_1.Cells(row, col + 8).Value)
            except: sum_rating = _f
            try: win_rating    = float(ws_1.Cells(row, col + 10).Value)
            except: win_rating = _f
            ## Circuit length
            try: cct_km        = float(ws_1.Cells(row, col + 11).Value)
            except: cct_km     = _f
            ## Impedance data
            try: r             = float(ws_1.Cells(row, col + 12).Value)
            except: r          = _f
            try: x             = float(ws_1.Cells(row, col + 13).Value)
            except: x          = _f
            try: b             = float(ws_1.Cells(row, col + 14).Value)
            except: b          = _f

            ## Create dictionary that will contain the data from the Excel spreadsheet
            base_case_changes_dict[grid_element + " " + cct_id] = {
                                        type_of_change: \
                                            [i_bus, j_bus, cct_id, sum_rating, win_rating, cct_km, r, x, b, k_bus]
                                            }
        row += 1
    xls_1.Quit()
    
    return base_case_changes_dict


## If possible, derive a contingency name using bus numbers
## ========================================================
def get_contingency_name(contingency_temp):

    import re
    cont_numbers = re.findall(r'\d+', contingency_temp)

    try:
        err, cont_ibus_name = psspy.notona(int(cont_numbers[0]))
        err, cont_jbus_name = psspy.notona(int(cont_numbers[1]))
        contingency = cont_numbers[0] + " " + cont_ibus_name + " " + cont_numbers[1] + " " + cont_jbus_name + " " + cont_numbers[2]
    except:
        contingency = contingency_temp
    
    return contingency
    

## Identify Non-Converged Contingencies
## ====================================
def non_convergence(n_1_file):                     

    print "\nChecking for non-converged contingency solutions:"

    nc_list = []
  
    nc_bus_mis_lmt = 0.5
    nc_sys_mis_lmt = 1.0

    ncr_name = "Non-Convergence_Report" ## Report containing non-converged contingency data    

    ## Create 'Non-Convergence_Report.dat' report
    psspy.lines_per_page_one_device(1, 100)    
    psspy.report_output(2, ncr_name + '.dat', [0,0])

    ## Extra fields in new version of 'accc_single_run_report_outport_x' - e.g. identifies lost load
    nd_err = psspy.accc_single_run_report_4([5, _i, _i, _i, _i, _i, _i, _i, _i, _i, _i, 1], [_i, _i, _i, _i, _i], \
                                            [nc_bus_mis_lmt, nc_sys_mis_lmt, _f, _f, _f, _f, _f], n_1_file)                                
    if nd_err == 0:
        print " " + chr(26) + " Non-converged report created successfully"
    else:
        print "***** ERROR WITH NON-CONVERGED REPORT! *****"
    
    ## Re-direct to the report output
    psspy.lines_per_page_one_device(1, 100)
    psspy.report_output(1, "", [0,0])

    non_convergence_file = open(ncr_name + '.dat')        

    non_convergence_file_line = non_convergence_file.readline()                                     
    
    nc_label = "X----- CONTINGENCY LABEL ------X X-- BUS ---X X- SYSTEM -X TERMINATION CONDITION" ## For PSS®E33 & 34 - not PSS®E 32
 
    while 1:

        if string.find(non_convergence_file_line, "NO SYSTEM CONDITIONS SATISFY THE FILTER CRITERIA") == 0 or \
           string.find(non_convergence_file_line, "No system conditions satisfy the filter criteria") == 0:                
            print " " + chr(26) + " All solutions have converged"
            break ## No non-convergence identified - therefore exit!

        if string.find(non_convergence_file_line, nc_label) == 0:
            print "\nNON-CONVERGED SOLUTIONS:"            
            print " " + chr(26) + " Reading non-converged solutions..."           

            while 1:                

                non_convergence_file_line = non_convergence_file.readline()              ## Read in the next line from the file...
                nc_description = string.rstrip(string.lstrip(non_convergence_file_line[6:20]))
                
                if len(non_convergence_file_line) == 1:                                  ## If length of string is zero...                                
                    break                                                                ## ...then there are no more contingencies
                elif string.rstrip(string.lstrip(non_convergence_file_line[:30])) == "": ## If there is no contingency description
                    continue                                                             ## ...then skip the line and go to the next one                
                
                ## Read the bus mismatch -> & 'clean' up the value
                ## Sometime the mismatch can be very small/large, e.g. 123456E+04
                nc_bus_mis = non_convergence_file_line[31:43]          
                if 'E' in nc_bus_mis:
                    nc_bus_mis = nc_bus_mis.replace('E', '')
                if '-' in nc_bus_mis:
                    nc_bus_mis = nc_bus_mis.replace('-', '')
                if '+' in nc_bus_mis:
                    nc_bus_mis = nc_bus_mis.replace('+', '')                    
                nc_bus_mis = round(float(nc_bus_mis), 1)

                ## Read the system mismatch -> & 'clean' up the value
                ## Sometime the mismatch can be very small/large, e.g. 123456E+04
                nc_sys_mis = non_convergence_file_line[45:58]          
                if 'E' in nc_sys_mis:
                    nc_sys_mis = nc_sys_mis.replace('E', '')
                if '-' in nc_sys_mis:
                    nc_sys_mis = nc_sys_mis.replace('-', '')
                if '+' in nc_sys_mis:
                    nc_sys_mis = nc_sys_mis.replace('+', '')                    
                nc_sys_mis = round(float(nc_sys_mis), 1)
                
                nc_term_cond = string.lstrip(string.rstrip(non_convergence_file_line[59:100]))

                nc_list.append([nc_description, nc_sys_mis, nc_term_cond])

            break

        non_convergence_file_line = non_convergence_file.readline()

    ## Close the file...
    non_convergence_file.close()              

    return nc_list


## Function that runs a basic N-1
## ==============================
def run_n_minus_one(each_raw_file):

    print "\nRunning N-1 for a connection of", connection_increment, "MW\n"

    ## Some file names
    dfax_file_name = "Distribution_Factors.dfx"
    n_1_file = "N-1_Results.acc"

    ## Subsystem definition
    subsystem_name = 'Ireland'

    ## Make *.mon file
    print " - Making *.mon file"
    mon_file_name = "temp_monitor.mon"
    mon_file = open(mon_file_name, "w")
    mon_file.write("MONITOR BRANCHES IN SUBSYSTEM '" + subsystem_name + "'\n")
    mon_file.write("MONITOR VOLTAGE RANGE SUBSYSTEM '" + subsystem_name + "' 0.9 1.091\n")
    mon_file.write("MONITOR VOLTAGE DEVIATION SUBSYSTEM '" + subsystem_name + "' 0.1 0.1\n")
    mon_file.write("END\n")
    mon_file.close()

    ## Make *.con file
    print " - Making *.con file"
    con_file_name = "temp_contingency.con"
    con_file = open(con_file_name, "w")
    con_file.write("SINGLE BRANCH IN SUBSYSTEM '" + subsystem_name + "'\n")
    con_file.write("END\n")
    con_file.close()
    
    ## Make *.sub file
    print " - Making *.sub file"
    sub_file_name = "temp_subsystem.sub"
    sub_file = open(sub_file_name, "w")
    sub_file.write("SUBSYSTEM '" + subsystem_name + "'\n")
    sub_file.write("     JOIN 'GROUP 1'\n")
    sub_file.write("          AREA 1\n")
    sub_file.write("          AREA 2\n")
    sub_file.write("          AREA 3\n")
    sub_file.write("          AREA 4\n")
    sub_file.write("          AREA 5\n")
    sub_file.write("          AREA 6\n")
    sub_file.write("          AREA 7\n")
    sub_file.write("          AREA 8\n")
    sub_file.write("          AREA 9\n")
    sub_file.write("          AREA 10\n")
    sub_file.write("          KVRANGE 110 400\n")
    sub_file.write("     END\n")
    sub_file.write("END\n")
    sub_file.write("\nEND\n")
    sub_file.close()

    ## Make *.inlf ile
    print " - Making *.inl file"
    inl_file_name = "temp_inlf_file.inl" 
    inl_file = open("temp_inlf_file.inl", "w")

    conventional_plant_owners = [8, 9, 10, 11, 1, 14, 15, 36, 37, 38, 39, 40, 49]
    battery_owners            = [28, 46, 58, 59] 
    
    lamda_droop         = 0.05 ## Typical/default value 
    lamda_h             = 4.5  ## Simple average inertia value - not going to use it
    lamda_damped_factor = 0.0  ## Default zero value

    ## Include machines with low Pmin: Aghada CTs, TH and SK3/SK4
    size_of_machine_to_consider = 70.0 ## MW
    
    err, generator_buses = psspy.amachint(-1, 4, 'NUMBER')    
    err, generator_status = psspy.amachint(-1, 4, 'STATUS')    
    err, generator_types = psspy.amachint(-1, 4, 'OWN1')    
    err, generator_ids = psspy.amachchar(-1, 4, 'ID')
    err, generator_names = psspy.amachchar(-1, 4, 'EXNAME')
    err, generator_pmax = psspy.amachreal(-1, 4, 'PMAX')    
    err, generator_pmin = psspy.amachreal(-1, 4, 'PMIN')    
    err, generator_base = psspy.amachreal(-1, 4, 'MBASE')    
    err, generator_pgen = psspy.amachreal(-1, 4, 'PGEN')    

    ## Only select conventional plants
    ## Note: PMIN & PMAX must be given in p.u. of base MVA
    inl_rounding   = 4
    inl_text_space = ", "
    for gen_bus, gen_id, gen_type, gen_pmax, gen_pmin, gen_name, gen_status, gen_base, gen_pgen in \
        zip(generator_buses[0], generator_ids[0], generator_types[0], generator_pmax[0], \
            generator_pmin[0], generator_names[0], generator_status[0], generator_base[0], generator_pgen[0]):

            ## Select in-service machines - i.e. any battery & conventional plant of a certain size            
            if gen_type in battery_owners or \
               ((gen_type in conventional_plant_owners or gen_id == "ZZ") and gen_pmax >= size_of_machine_to_consider) and \
               gen_status == 1:
                
                sort_pmin = (gen_pmin/gen_base)
                ## if sort_pmin <= 0.0: sort_pmin = 1.0
                inl_file.write(str(gen_bus) + inl_text_space + \
                               "'" + str(gen_id) + "'" + \
                               inl_text_space + str(lamda_h) + inl_text_space + \
                               str(round(gen_pmax/gen_base, inl_rounding)) + inl_text_space + \
                               str(round(sort_pmin, inl_rounding)) + inl_text_space + \
                               str(lamda_droop) + inl_text_space + str(lamda_damped_factor) + " \n")
    inl_file.write("0\n")
    inl_file.close()

    if sort_out_ckm_pst:
        
        print "\nUsing PSCOPF to sort out the CKM PST"

        global pst_angle_for_n, pst_angle_for_n_1

        psspy.save("pre-pscopf_case") 
        
        treatment_of_shunts = 1     ## Set to '0' to disable shunts / '1' for all / '2' for continuous
        voltage_tol         = 999.0 ## Voltage tolerance in linear programming (%) - good to have some bandwidth
        thermal_tol         = 0.001 ## Flow tolerance in linear programming (%) - good to get accurate thermal performance
        pscopf_mis          = 10.0
        pscopf_n_loading    = 100.0
        pscopf_n1_loading   = 110.0
        subsystem_name      = "Ireland"
        
        ## PSCOPF execution options:
        online_gen_disp_option  = 0
        load_shed_option        = 0
        pst_option              = 1
        offline_gen_disp_option = 0
        trafo_adjust_option     = 0
        shunt_adjust_option     = 0

        ## PSCOPF weighting options:
        ## Keeping weightings low to best activate PSCOPF & keep within thermal limits etc.
        ## Keeping weightings too low can be problematic - e.g. avoid 0.1
        online_gen_weight       = 1.0
        load_shed_weight        = 1.0
        pst_weight              = 0.1
        offline_gen_weight      = 1.0
        trafo_adjust_weight     = 1.0
        shunts_weight           = 1.0

        ## Creat empty *.con file
        blank_con_filename = "Contingency_file_for_n_pscopf.con"
        blank_con_file = open(blank_con_filename, 'w')
        blank_con_file.write("END\n")        
        blank_con_file.close()                   

        ## Give stations a REALLY high emergency voltage range - don't want voltage issues distracting the PSCOPF
        err, pscopf_buses = psspy.abusint(-1, 2, 'NUMBER')
        for pb in pscopf_buses[0]: err = psspy.bus_chng_3(pb,[],[_f,_f,_f,_f,_f, 1.3, 0.7],_s)

        ## Run DFAX activity
        dfx_err = psspy.dfax([1,0], sub_file_name, mon_file_name, blank_con_filename, dfax_file_name)
        if dfx_err != 0:
            print "Warning! Error creating DFAX file!"
            quit()

        if debug: print "\nPreparing PSCOPF for N..."    
        pscopf_report_name = "pscopf_report_n.opf" ## Name of results file
        psspy.lines_per_page_one_device(1, 60)
        psspy.report_output(2, pscopf_report_name, [0,0])

        ## Run PSCOPF on base case - don't need activate INLF capability & deal with only very high overload
        base_case_option = 1 ## Set to '0' to skip base case assessment - not advisable to set this to '1'
        inlf_option_for_pscopf = 0
        pscopf_err_n = psspy.pscopf_2([0,0,0,0,treatment_of_shunts,0,1,0,0,0,0,0,treatment_of_shunts, 0, \
                                       inlf_option_for_pscopf,2,2,2,2,99,10, \
                                       base_case_option, online_gen_disp_option, load_shed_option, pst_option, \
                                       offline_gen_disp_option, trafo_adjust_option, shunt_adjust_option], \
                                      [pscopf_mis, pscopf_n_loading, pscopf_n_loading, voltage_tol, thermal_tol, \
                                       online_gen_weight, load_shed_weight, pst_weight, offline_gen_weight, \
                                       trafo_adjust_weight, shunts_weight], \
                                      [subsystem_name, subsystem_name, subsystem_name, subsystem_name, subsystem_name, subsystem_name, subsystem_name], \
                                      dfax_file_name, "", "")
        psspy.lines_per_page_one_device(2,1000000)
        psspy.report_output(1,"",[0,0])

        ## Remove temporary empty *.con file
        os.remove(blank_con_filename)
        #os.remove(dfax_file_name) #KC

        ## Solution to account for changes & prepare for N-1 in ACLF
        print "\nSolving to ensure changes are captured accurately"
        ## Carry out a solution to guage how the case is
        err = psspy.rawd_2(0,1,[1,1,1,0,0,0,0],0, filelocation + "\\Simulation " + \
                           time_stamp + "\\Debug\\pre-solution_file.raw")
        psspy.fdns([0,0,0,0,1,1,0,0]) ## Flat start
        for solution_tries in range(1, 99):
            psspy.fdns([0,0,0,0,1,0,0,0])
            mis = psspy.sysmsm()
            if debug: print " -Mismatch:", round(mis, 3), "MVA"
            if mis <= system_mismatch_target:
                print "\nSolution indication is good! Mismatch:", round(mis, 3), "MVA" 
                break
        if mis > system_mismatch_target:
            print "\nSolution is NOT good! Mismatch:", round(mis, 3), "MVA"

        post_pscopf_mis = psspy.sysmsm()        
        if pscopf_err_n > 0 or post_pscopf_mis > system_mismatch_target:
            print "\nError running base case PSCOPF is", pscopf_err_n, "& solution mismatch =", round(post_pscopf_mis, 3), "MVA"
            print "\nContinuing by re-reading the pre-PSCOPF case..."
        else:
            print "\nSuccessfull PSCOPF N (base case) operation -> PSCOPF error:", pscopf_err_n

        inlf_option_for_pscopf = 4 ## Set to '0' to disable or '4' to activate

        ## Run DFAX activity
        dfx_err = psspy.dfax([1,0], sub_file_name, mon_file_name, con_file_name, dfax_file_name)
        if dfx_err != 0:
            print "Warning! Error creating DFAX file!"
            quit()

        ## Run PSCOPF for N-1
        base_case_option = 0

        if debug: print "\nPreparing PSCOPF for N-1..."    
        pscopf_report_name = "pscopf_report_n-1.opf" ## Name of results file
        psspy.lines_per_page_one_device(1, 60)
        psspy.report_output(2, pscopf_report_name, [0,0])

        pscopf_err_n1 = psspy.pscopf_2([0,0,0,0,treatment_of_shunts,0,1,0,0,0,0,0,treatment_of_shunts, 0, \
                                        inlf_option_for_pscopf,2,3,2,2,99,10, \
                                        base_case_option, online_gen_disp_option, load_shed_option, pst_option, \
                                        offline_gen_disp_option, trafo_adjust_option, shunt_adjust_option], \
                                       [pscopf_mis, pscopf_n1_loading, pscopf_n1_loading, voltage_tol, thermal_tol, \
                                        online_gen_weight, load_shed_weight, pst_weight, offline_gen_weight, \
                                        trafo_adjust_weight, shunts_weight], \
                                       [subsystem_name, subsystem_name, subsystem_name, subsystem_name, subsystem_name, subsystem_name, subsystem_name], \
                                       dfax_file_name, inl_file_name, "")        

        psspy.lines_per_page_one_device(2,1000000)
        psspy.report_output(1,"",[0,0])

        ## Carry out a solution to guage how the case is
        err = psspy.rawd_2(0,1,[1,1,1,0,0,0,0],0, filelocation + "\\Simulation " + \
                           time_stamp + "\\Debug\\pre-solution_file.raw")
        psspy.fdns([0,0,0,0,1,1,0,0]) ## Flat start
        for solution_tries in range(1, 99):
            psspy.fdns([0,0,0,0,1,0,0,0])
            mis = psspy.sysmsm()
            if mis < system_mismatch_target:
                print "\nSolution indication is good! Mismatch:", round(mis, 3), "MVA" 
                break
            else:
                print "\nSolution is NOT good! Mismatch:", round(mis, 3), "MVA"

        ## Read OPF files
        import glob
        detected_pst_file_names = glob.glob("*.opf")
        for dpfn in detected_pst_file_names:
            print "\nReading:", dpfn            
            each_pst_file = open(dpfn, 'r')
            line_count = 0
            while 1:
                each_pst_file_line = each_pst_file.readline()
                if line_count == 100:
                    pst_angle_for_n_1 = "N/A"
                    break                    
                if "<----------------- PHASE SHIFTER ----------------->" in each_pst_file_line:
                    each_pst_file_line = each_pst_file.readline()
                    new_angle = each_pst_file_line.split()[-2]
                    err, ckm_flow = psspy.brnflo(1742, 17431, "1")
                    print "Angle:", new_angle, "| MW:", ckm_flow.real, "& Mvar:", ckm_flow.imag
                    if 'n-1' in dpfn:
                        pst_angle_for_n_1 = round(ckm_flow.real, 1)
                    else:
                        pst_angle_for_n = round(ckm_flow.real, 1)
                    break
                line_count += 1
                
    mis = general_model_solution()
    if mis > system_mismatch_target:
        print "\nSolution is NOT great! Mismatch:", round(mis, 3), "MVA"
        print "\nContinuing by re-reading the pre-PSCOPF case..."
        psspy.save("problem_pscopf_case")
        psspy.case("pre-pscopf_case")

    ## Run DFAX activity
    print " - Making *.dfx file"
    dfx_err = psspy.dfax([1,0], sub_file_name, mon_file_name, con_file_name, dfax_file_name) 
    if dfx_err != 0:
        print "Warning! Error creating DFAX file!"
        quit()


    ## Run N-1 activity
    '''
                  **** Issue with earlier versions of PSSE 33? ****
                  
    inlf_option = 4
    accc_err = psspy.accc_with_dsp_3(1.0,[0,0,0,0,2,1,0,0,0,4,0], subsystem_name, \
                                     dfax_file_name, n_1_file, "", inl_file_name, "")
    '''

    ## accc_err = psspy.accc(1.0, [0, 0, 0, 0, 1, 0, 0], dfax_file_name, n_1_file, "") ## This works with 33.4/33.5

    accc_err = psspy.accc_with_dsp_2(5.0,[0,0,0,0,2,1,0,0,0,4], subsystem_name, dfax_file_name, n_1_file, "", inl_file_name)
        
    if not debug:
        #os.remove(dfax_file_name) KC
        os.remove(inl_file_name)
        os.remove(mon_file_name)
        os.remove(con_file_name)
        os.remove(sub_file_name)

    print "\nCreating N-1 summary text file..." 

    ## To avoid clutter, save the cases in a folder
    if not os.path.isdir("Simulation " + time_stamp + "\\Violations"):
        os.makedirs("Simulation " + time_stamp + "\\Violations")

    ## Create simple text file version of ACCC output data
    v_err = pssarrays.accc_violations_report(accfile = n_1_file, \
                                             stype = 'contingency', \
                                             busmsm = 0.1, sysmsm = 1.0, \
                                             rating = 'B', \
                                             flowlimit = 100.0, \
                                             rptfile = filelocation + "\\Simulation " + time_stamp + "\\Violations" \
                                             "\\Violations_" + each_raw_file[:-4] + \
                                             "_" + str(int(connection_increment)) + "MW.dat")
    if v_err != 0:
        print "Warning! Error running ACCC!"
        quit()

    nc_list = non_convergence(n_1_file)
    if not debug: os.remove(n_1_file)

    return nc_list


## This function makes sure that the shunt voltage targets are aligned with those of nearby machines
## In particular, if machine voltage targets are changed, the shunts also need to be considered.
## =================================================================================================
def check_vsched_alignment_with_shunts(debug):

    err, check_these_shunts      = psspy.aswshint(-1, 4, 'NUMBER')
    err, check_these_shunt_iregs = psspy.aswshint(-1, 4, 'IREG')
    err, check_these_shunt_modes = psspy.aswshint(-1, 4, 'MODE')
    err, check_these_shunt_vhis  = psspy.aswshreal(-1, 4, 'VSWHI')
    err, check_these_shunt_vlos  = psspy.aswshreal(-1, 4, 'VSWLO')

    shunts_that_need_checking = {}
    for each_shunt, shunt_mode, shunt_vhi, shunt_vlo, each_ireg in zip(check_these_shunts[0], check_these_shunt_modes[0], \
                                                                       check_these_shunt_vhis[0], check_these_shunt_vlos[0], \
                                                                       check_these_shunt_iregs[0]):
        err, each_shunt_zone = psspy.busint(each_shunt, 'ZONE')
        if each_shunt_zone in ie_zones and each_ireg != 0 and round(shunt_vhi, 3) == round(shunt_vlo, 3):
            shunts_that_need_checking[str(each_ireg)] = [each_shunt, round((shunt_vhi + shunt_vlo) * 0.5 , 3)] 

    return shunts_that_need_checking


## Function that identifies/changes scheduled voltages if too low/high
## ===================================================================
def fix_mvar_limits():

    ## Objective: generators achieve scheduled voltages with something to spare
    ## This routine tries to create a system-wide balance between target & actual voltages
    ## If target voltages are too high, LAMDA will try to bring them lower that the original actual voltage
    
    if debug: print "\nIdentifying generation outside Mvar limits"
   
    ## Voltage target range
    use_pscopf = True
    if use_pscopf: min_vsched = 0.9; max_vsched = 1.1
    else: min_vsched = 0.98; max_vsched = 1.075
    vsched_adjustment_factor = 0.001
    vsched_rnd = 4 ## Rounding limit

    ## For now keep changes to Ireland - & not Northern Ireland
    agenbusint_flag = 4
    err, check_these_gen_bus_nums      = psspy.agenbusint(-1, agenbusint_flag, 'NUMBER')
    err, check_these_controlled_buses  = psspy.agenbusint(-1, agenbusint_flag, 'IREG')
    err, check_these_vscheds           = psspy.agenbusreal(-1, agenbusint_flag, 'VSPU')
    err, check_these_actual_vltgs      = psspy.agenbusreal(-1, agenbusint_flag, 'IREGPU')
    err, check_these_statuses          = psspy.agenbusint(-1, agenbusint_flag, 'STATUS')
    err, check_these_types             = psspy.agenbusint(-1, agenbusint_flag, 'TYPE')
    err, check_these_controlling_bases = psspy.agenbusreal(-1, agenbusint_flag, 'BASE')
    err, check_these_controlled_bases  = psspy.agenbusreal(-1, agenbusint_flag, 'IREGBASE')
    err, check_these_qmaxes            = psspy.agenbusreal(-1, agenbusint_flag, 'QMAX')
    err, check_these_qmins             = psspy.agenbusreal(-1, agenbusint_flag, 'QMIN')
    err, check_these_qgens             = psspy.agenbusreal(-1, agenbusint_flag, 'QGEN')

    shunts_that_need_checking = check_vsched_alignment_with_shunts(debug)

    ## Identify controlled buses that have machines at Mvar limits
    machines_at_var_limits = {}
    significant_mvar_output = 999.0 ## Mvar capability being considered
    for controlling_bus, controlled_bus, status, qmax, qmin, qgen, controlling_bus_type in \
        zip(check_these_gen_bus_nums[0], check_these_controlled_buses[0], check_these_statuses[0], \
            check_these_qmaxes[0], check_these_qmins[0], check_these_qgens[0], check_these_types[0]):

        err, controlling_bus_zone = psspy.busint(controlling_bus, 'ZONE')
        if controlling_bus_zone in ie_zones and status in [0, 1] and (qmax > 0.0 and qmin < 0.0) and \
           (qgen == qmax or qgen == qmin) and abs(qgen) > significant_mvar_output and controlling_bus_type != 3:

            ## Ignore temporary machine models - these don't have a Mvar range
            err, rval_temp = psspy.macdat(controlling_bus, "XX", 'Q')
            if err == 0: continue
            err, rval_temp = psspy.macdat(controlling_bus, "$$", 'Q')
            if err == 0: continue           

            ## Used to have this but it created a lot of non-convergence:
            ## err, rval_temp = psspy.macdat(controlling_bus, sco_id, 'Q')
            ## if err == 0: continue

            ## Otherwise consider the machine
            machines_at_var_limits[controlled_bus] = qgen    

    machine_relationships = {}
    for controlling_bus, controlled_bus, controlling_bus_type in zip(check_these_gen_bus_nums[0], check_these_controlled_buses[0], check_these_types[0]):

        err, controlling_bus_zone = psspy.busint(controlling_bus, 'ZONE')
        if controlling_bus_zone in ie_zones and controlling_bus_type in [2, 3]:
            if controlled_bus == 0: controlled_bus = controlling_bus
            if controlled_bus not in machine_relationships.keys(): machine_relationships[controlled_bus] = [controlling_bus]
            else: machine_relationships[controlled_bus].append(controlling_bus)

    ## Make changes if required
    done_these_vscheds = {}
    remote_bus_count   = {}
    no_of_vsched_changes = 0
    for controlling_bus, controlled_bus, vsched, actual_vltg, status, gen_bus_base, reg_bus_base, \
        gen_qmax, gen_qmin, qgen, controlling_bus_type in \
        zip(check_these_gen_bus_nums[0], check_these_controlled_buses[0], \
            check_these_vscheds[0], check_these_actual_vltgs[0], check_these_statuses[0], \
            check_these_controlling_bases[0], check_these_controlled_bases[0], \
            check_these_qmaxes[0], check_these_qmins[0], check_these_qgens[0], check_these_types[0]):

        ## *** not considering NI for now ***
        err, controlling_bus_zone = psspy.busint(controlling_bus, 'ZONE')
        if controlling_bus_zone in ie_zones and controlling_bus_type != 3: ## and status in [0, 1] and (gen_qmax > 0.0 and gen_qmin < 0.0)

            ## Try to pull back machines from achieveing a very high voltage
            ## So instead of 1.05 pu, try for 1.045 pu & instead of 1.075 pu, try for 1.07 pu
            if controlled_bus in done_these_vscheds.keys():
                if debug: print "\n" + chr(187) + " Already assessed a Vsched linked to bus", controlled_bus, \
                   "-> therefore set Vsched of machine at bus", controlling_bus, "to", round(done_these_vscheds[controlled_bus], vsched_rnd), "pu"
                psspy.plant_data(controlling_bus,_i,[done_these_vscheds[controlled_bus],_f])
                
            else:
                if actual_vltg > vsched:
                    
                    if debug:
                        print "\n- Vsched", round(vsched, vsched_rnd), "pu is LOW for bus", controlling_bus, "- actual voltage at", controlled_bus, \
                              "is", round(actual_vltg, vsched_rnd), "pu [difference =", round(actual_vltg - vsched, vsched_rnd), "pu]"
                    
                    if controlled_bus in machines_at_var_limits.keys():
                        if machines_at_var_limits[controlled_bus] > 0:
                            proposed_new_vsched = actual_vltg - ((actual_vltg - vsched) / 2.0)
                            vsched_change = 'decrease'
                        else:
                            proposed_new_vsched = vsched + ((actual_vltg - vsched) / 2.0)
                            vsched_change = 'increase'
                        if debug:
                            print "- HOWEVER some local machines (e.g. at bus " + str(controlling_bus) + ") are at var limits:", \
                                  machines_at_var_limits[controlled_bus], "and machine(s) could benefit from a Vsched", vsched_change, "to", \
                                  proposed_new_vsched, "pu"
                    else:
                       
                        proposed_new_vsched = actual_vltg ## vsched + ((actual_vltg - vsched) / 2.0)
                        if debug: print " ", chr(187), "Iterating Vsched higher to", round(proposed_new_vsched, vsched_rnd), "pu"
                            
                    if proposed_new_vsched > max_vsched:
                        if debug: print " ", chr(26), "Vsched is a bit too HIGH therefore keeping at", max_vsched, "pu"               
                        proposed_new_vsched = max_vsched
                            
                elif vsched > actual_vltg:

                    if debug:
                        print "\n- Vsched", round(vsched, vsched_rnd), "pu is HIGH for bus", controlling_bus, "- actual voltage at", controlled_bus, \
                              "is", round(actual_vltg, vsched_rnd), "pu [difference =", round(actual_vltg - vsched, vsched_rnd), "pu]"
                    
                    if controlled_bus in machines_at_var_limits.keys():
                        if machines_at_var_limits[controlled_bus] > 0:
                            proposed_new_vsched = vsched - ((vsched - actual_vltg) / 2.0)
                            vsched_change = 'decrease'
                        else:
                            proposed_new_vsched = actual_vltg + ((vsched - actual_vltg) / 2.0)
                            vsched_change = 'increase'
                        if debug:
                            print "- HOWEVER some local machines (e.g. at bus " + str(controlling_bus) + ") are at var limits:", \
                                  machines_at_var_limits[controlled_bus], "and machine(s) could benefit from a Vsched", vsched_change, "to", \
                                  proposed_new_vsched, "pu"
                    else:                    
                        proposed_new_vsched = actual_vltg ## actual_vltg + ((vsched - actual_vltg) / 2.0)
                        if debug: print " ", chr(187), "Iterating Vsched lower to", round(proposed_new_vsched, vsched_rnd), "pu"
                        
                    if proposed_new_vsched < min_vsched:
                        if debug: print " ", chr(26), "Vsched is a bit too LOW therefore keeping at", min_vsched, "pu"               
                        proposed_new_vsched = min_vsched
                
                ## If vsched looks ok but machine is at max. leading/lagging, adjust voltage target                    
                elif actual_vltg == vsched:
                    '''
                    if controlled_bus in machines_at_var_limits.keys():

                        if machines_at_var_limits[controlled_bus] > 0:                            
                            proposed_new_vsched = vsched - vsched_adjustment_factor
                            if debug: print "\n- Scheduled/actual voltages ok at bus", controlled_bus, "HOWEVER some machines are var-limited:", \
                               machines_at_var_limits[controlled_bus], \
                               "& machine(s) will benefit from Vsched decrease to", proposed_new_vsched, "pu"                                               
                        else:                            
                            proposed_new_vsched = vsched + vsched_adjustment_factor
                            if debug: print "\n- Scheduled/actual voltages ok at bus", controlled_bus, "HOWEVER some machines are var-limited:", \
                               machines_at_var_limits[controlled_bus], \
                               "& machine(s) will benefit from Vsched increase to", proposed_new_vsched, "pu"
                    else:
                    '''
                    continue
                
                ## Log ongoing changes
                if controlled_bus == 0: done_these_vscheds[controlling_bus] = proposed_new_vsched
                else: done_these_vscheds[controlled_bus] = proposed_new_vsched

                ## Make the 'Vsched' adjustment
                err = psspy.plant_data(controlling_bus,_i,[proposed_new_vsched,_f])
                if controlling_bus in machine_relationships[controlled_bus]:
                    for other_controlling_buses in machine_relationships[controlled_bus]:
                        if other_controlling_buses != controlling_bus:
                            if debug: print "Also changing Vsched of machine at bus", other_controlling_buses, "to", proposed_new_vsched, "pu"
                            err = psspy.plant_data(other_controlling_buses,_i,[proposed_new_vsched,_f])                                            
                no_of_vsched_changes += 1                

                ## Check to see if some shunts might need a set point adjustment
                if str(controlled_bus) in shunts_that_need_checking.keys():
                    if proposed_new_vsched != shunts_that_need_checking[str(controlled_bus)][1]:
                        if debug: print "* Adjusting shunt at bus", shunts_that_need_checking[str(controlled_bus)][0], \
                           "to ensure that bus", controlled_bus, "is being controlled at", proposed_new_vsched, "pu"
                        err = psspy.switched_shunt_chng_3(shunts_that_need_checking[str(controlled_bus)][0],[], \
                                                          [_f,_f,_f,_f,_f,_f,_f,_f, proposed_new_vsched, proposed_new_vsched],_s)
                        if err > 0:
                            if debug: print err
                            quit()
                        

## Function that assess the sub-transmission transformer set up
## =============================================================
def fix_transformers(operational_season):

    ## *** need to add transformer check for the likes of Garvagh ***
    
    print "\nAssessing two winding transformers for", operational_season, "case"

    ierr, twt_from_buses      = psspy.atrnint(-1, 2, 3, 2, 1, 'FROMNUMBER')
    ierr, twt_to_buses        = psspy.atrnint(-1, 2, 3, 2, 1, 'TONUMBER')
    ierr, twt_ids             = psspy.atrnchar(-1, 2, 3, 2, 1, 'ID')
    ierr, tap_numbers         = psspy.atrnint(-1, 2, 3, 2, 1, 'NTPOSN')
    ierr, control_modes       = psspy.atrnint(-1, 2, 3, 2, 1, 'CODE')
    ierr, controlled_buses    = psspy.atrnint(-1, 2, 3, 2, 1, 'ICONTNUMBER')
    ierr, transformer_ratings = psspy.atrnreal(-1, 2, 3, 2, 1, 'RATEB')
    ierr, upper_voltage_limit = psspy.atrnreal(-1, 2, 3, 2, 1, 'VMAX')
    ierr, lower_voltage_limit = psspy.atrnreal(-1, 2, 3, 2, 1, 'VMIN')

    for twt_from_bus, twt_to_bus, twt_id, tap_number, control_mode, controlled_bus, transformer_rating, \
        transformer_hv, transformer_lv in \
        zip(twt_from_buses[0], twt_to_buses[0], twt_ids[0], tap_numbers[0], control_modes[0], controlled_buses[0], \
            transformer_ratings[0], upper_voltage_limit[0], lower_voltage_limit[0]):

        '''
        ## If the transformer is a generator transformer...
        ## ...check if the transformer rating is sufficiently sized        
        err, from_bus_type = psspy.busint(twt_from_bus[0][t], 'TYPE')        
        if from_bus_type == 2 or from_bus_type == 3:
            err = psspy.inimac(twt_from_bus[0][t])
            if err == 0:
                while 1:
                    err, mac_id = psspy.nxtmac(twt_from_bus[0][t])
                    if err == 1: ## No more machines
                        break
                    else:
                        err, mac_pmax = psspy.macdat(twt_from_bus[0][t], mac_id, 'PMAX')                    
                        if transformer_rating[0][t] < mac_pmax:
                            if debug:
                                print " ", chr(26), round(mac_pmax, 1), \
                                      "MW machine", mac_id, "at bus", twt_from_bus[0][t], \
                                      "does not have adequate transformer capacity", round(transformer_rating[0][t], 1), "MW"
            err = psspy.inimac(twt_to_bus[0][t])
            if err == 0:
                while 1:                    
                    err, mac_id = psspy.nxtmac(twt_to_bus[0][t])                    
                    if err == 1: ## No more machines
                        break
                    else:                        
                        err, mac_pmax = psspy.macdat(twt_to_bus[0][t], mac_id, 'PMAX')                    
                        if transformer_rating[0][t] < mac_pmax:
                            if debug:
                                print " ", chr(26), round(mac_pmax, 1), \
                                      "MW machine", mac_id, "at bus", twt_to_bus[0][t], \
                                      "does not have adequate transformer capacity", round(transformer_rating[0][t], 1), "MW"
        '''
        err, from_bus_type = psspy.busint(twt_from_bus, 'TYPE')
        err, to_bus_type = psspy.busint(twt_to_bus, 'TYPE')
        err, from_bus_base = psspy.busdat(twt_from_bus, 'BASE')
        err, to_bus_base = psspy.busdat(twt_to_bus, 'BASE')
        if from_bus_type not in [2, 3] and to_bus_type not in [2, 3]:

            if debug: print "\nAssessing transformer with numbers/id:", twt_from_bus, twt_to_bus, twt_id

            ## Checking transformers with usually enabled capability - tap numbers usually in excess of three
            err, twt_from_bus_zone = psspy.busint(twt_from_bus, 'ZONE')               
            err, twt_to_bus_zone = psspy.busint(twt_to_bus, 'ZONE')               
            if tap_number > 3 and twt_from_bus_zone in ie_zones and twt_to_bus_zone in ie_zones:

                ## Check for base errors - this happens every now and then!
                if from_bus_base == 33.0:
                    if debug: print "Error! Changing base voltage of bus ", twt_from_bus, "to 38 kV"
                    err = psspy.bus_chng_3(twt_from_bus,[],[38.0],_s)
                    err, from_bus_base = psspy.busdat(twt_from_bus, 'BASE')
                if to_bus_base == 33.0:
                    if debug: print "Error! Changing base voltage of bus", twt_to_bus, "to 38 kV"
                    err = psspy.bus_chng_3(twt_to_bus,[],[38.0],_s)
                    err, to_bus_base = psspy.busdat(twt_to_bus, 'BASE')

                ## Review voltage ranges for non-generator transformers
                ## From ESB DSSPS:
                ##  - 38 kV: 0.96 - 1.132
                ##  - 20 kV: 1.01 - 1.11
                ##  - 10 kV: 1.01 - 1.11
                if from_bus_base in [110.0, 38.0] and to_bus_base in [110.0, 38.0]:
                    err = psspy.two_winding_chng_4(twt_from_bus, twt_to_bus, twt_id, \
                                                   [], [_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f, 1.132, 0.96],[])
                    if debug: print "Changing voltage limits of:", twt_from_bus, twt_to_bus, twt_id, "to 1.132 pu & 0.96 pu"
                elif ((from_bus_base in [110.0, 22.0, 20.0] and to_bus_base in [110.0, 22.0, 20.0]) or \
                     (from_bus_base in [38.0, 20.0] and to_bus_base in [38.0, 20.0]) or \
                     (from_bus_base in [38.0, 10.0] and to_bus_base in [38.0, 10.0]) or \
                     (from_bus_base in [110.0, 20.0, 11.0, 10.0] and to_bus_base in [110.0, 20.0, 11.0, 10.0])) and \
                     (from_bus_type not in [2, 3] and to_bus_type not in [2, 3]):
                    err = psspy.two_winding_chng_4(twt_from_bus, twt_to_bus, twt_id, \
                                                   [], [_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f, 1.11, 1.01],[])
                    if debug: print "Changing voltage limits of:", twt_from_bus, twt_to_bus, twt_id, "to 1.11 pu & 1.01 pu"
                else:
                    if debug: print "Not changing voltage ranges for this transformer:", \
                       twt_from_bus, twt_to_bus, twt_id, from_bus_base, to_bus_base

                ## Review control modes: 
                ##  a) If there is no control mode
                if control_mode == 0: 
                    if from_bus_base > to_bus_base:
                        if debug: print "" + chr(26) + " No voltage control:", \
                           twt_from_bus, twt_to_bus, twt_id, "- setting voltage control to:", twt_to_bus
                        psspy.two_winding_chng_4(twt_from_bus, twt_to_bus, twt_id, \
                                                 [_i,_i,_i,_i,_i,_i,_i,_i,twt_from_bus,twt_to_bus,_i,1], [], [])                       
                    else:
                        if debug: print "" + chr(26) + " No voltage control:", \
                           twt_from_bus, twt_to_bus, twt_id, "- setting voltage control to:", twt_from_bus
                        psspy.two_winding_chng_4(twt_from_bus, twt_to_bus, twt_id, \
                                                 [_i,_i,_i,_i,_i,_i,_i,_i,twt_to_bus,twt_from_bus,_i,1], [], [])
                ##  b) If control mode is set up incorrectly
                else:     
                    if from_bus_base > to_bus_base and controlled_bus == twt_from_bus:
                        if debug: print "" + chr(26) + " Incorrect voltage control set-up:", \
                           twt_from_bus, twt_to_bus, twt_id, "- setting voltage control to:", twt_to_bus
                        psspy.two_winding_chng_4(twt_from_bus, twt_to_bus, twt_id, \
                                                 [_i,_i,_i,_i,_i,_i,_i,_i,twt_from_bus,twt_to_bus,_i,1], [], [])   

                    elif to_bus_base > from_bus_base and controlled_bus == twt_to_bus:
                        if debug: print "" + chr(26) + " Incorrect voltage control set-up:", \
                           twt_from_bus, twt_to_bus, twt_id, "- setting voltage control to:", twt_from_bus
                        psspy.two_winding_chng_4(twt_from_bus, twt_to_bus, twt_id, \
                                                 [_i,_i,_i,_i,_i,_i,_i,_i,twt_to_bus,twt_from_bus,_i,1], [], [])  

        ## These trafos should not have a controlled bus - usually small generator transformers
        if tap_number == 3 and control_mode != 0: 
            if debug: print "\n       " + chr(187) + " Updating two winding transformer:", \
               twt_from_bus, twt_to_bus, twt_id, "- disabling control capability"
            psspy.two_winding_chng_4(twt_from_bus, twt_to_bus, twt_id, [_i,_i,_i,_i,_i,_i,_i,_i,_i,0,_i,0], [], [_s,_s])

        ## Check for significant/inactive generation transformers
        if tap_number > 3 and (control_mode == 0 or controlled_bus == 0) and (from_bus_type in [2, 3] or to_bus_type in [2, 3]):
            if debug: print "\n", chr(26), "WARNING! This transformer might need to be controlling a local generator:", \
               twt_from_bus, twt_to_bus, twt_id

        ## Identify transformers that may have a questionable range of operation
        if tap_number > 3 and transformer_hv >= 1.1 and control_mode == 1:
            if debug: print "Worth reviewing these voltage limits:", twt_from_bus, twt_to_bus, twt_id, \
               round(transformer_hv, 3), round(transformer_lv, 3)
            
    return


## This function reduces RES categories to 0 MW - and performs generation redispatch
## =================================================================================
def set_solar_and_wind_to_min(merit_order, each_raw_file, res_categories):
    
    print "\nSetting RES to zero & interconnectors to max. import"

    minimise_these_zones = [3, 4, 5, 8, 11] #KC - Area J is zone 11

    ## When redispatching for a zero RES situation, firstly assume that all interconnectors are on full import
    interconnector_categories = [49]

    err, generator_buses = psspy.amachint(-1, 4, 'NUMBER')    
    err, generator_ids = psspy.amachchar(-1, 4, 'ID')
    err, generator_status = psspy.amachint(-1, 4, 'STATUS')    
    err, generator_types = psspy.amachint(-1, 4, 'OWN1')    
    err, generator_pgen = psspy.amachreal(-1, 4, 'PGEN')
    err, generator_pmax = psspy.amachreal(-1, 4, 'PMAX')
    err, generator_vintage = psspy.amachint(-1, 4, 'OWN2')

    redispatch_target = 0.0
    #redispatch_target = 386.0
    for gen_bus, gen_id, gen_pgen, gen_type, gen_status, gen_pmax, gen_vintage in \
                        zip(generator_buses[0], generator_ids[0], generator_pgen[0], \
                            generator_types[0], generator_status[0], generator_pmax[0], generator_vintage[0]):

        err, gen_bus_zone = psspy.busint(gen_bus, 'ZONE') ## Identify the bus zone

        if gen_type in res_categories and gen_bus_zone in minimise_these_zones and gen_vintage != 883:

            err, gen_name = psspy.notona(gen_bus)

            ## Not switching off machines - just setting active power to 0.0 MW
            if gen_pgen > 0 and gen_status > 0:
                if debug: print " - RES -> 0 MW:", gen_bus, gen_id, round(gen_pgen, 1)
                err = psspy.machine_chng_2(gen_bus, gen_id,[1],[0.0, 0.0, 0.0, 0.0])
                redispatch_target += gen_pgen ## Therefore increase the redispatch target

        elif gen_type in interconnector_categories: #KC

            if "sv" in each_raw_file.lower() or "sm" in each_raw_file.lower() or "snv" in each_raw_file.lower():
                if debug: print " - Interconnection -> 50% import:", gen_bus, gen_id, gen_pmax / 2.0
                err = psspy.machine_chng_2(gen_bus, gen_id,[1],[gen_pmax / 2.0])
                redispatch_target -= gen_pmax / 2.0 - gen_pgen ## Therefore decrease the redispatch target
            else:
                if debug: print " - Interconnection -> 100% import:", gen_bus, gen_id, gen_pmax
                err = psspy.machine_chng_2(gen_bus, gen_id,[1],[gen_pmax])
                redispatch_target -= gen_pmax - gen_pgen ## Therefore decrease the redispatch target
        
    print "\nNeed to redispatch (increase other generation):", round(redispatch_target, 1), "MW"
    redispatch_remainder = execute_redispatch(merit_order, redispatch_target)
    

## This function sets RES categories to max - and performs generation redispatch
## =================================================================================
def set_solar_and_wind_to_max(merit_order, each_raw_file, operational_scenario, res_categories):

    print "\nSetting RES based on the following rules:"
    for k, v in res_increase_assumptions[operational_scenario].items():\
        print "   -", k, "->",  v, "%"
    print "Also setting output of interconnectors to maximum export"

    ## When redispatching for a zero RES situation, firstly assume that all interconnectors are on full import
    interconnector_categories = [49]

    err, generator_buses = psspy.amachint(-1, 4, 'NUMBER')    
    err, generator_ids = psspy.amachchar(-1, 4, 'ID')
    err, generator_status = psspy.amachint(-1, 4, 'STATUS')    
    err, generator_types = psspy.amachint(-1, 4, 'OWN1')    
    err, generator_pgen = psspy.amachreal(-1, 4, 'PGEN')
    err, generator_pmax = psspy.amachreal(-1, 4, 'PMAX')
    err, generator_pmin = psspy.amachreal(-1, 4, 'PMIN')
    err, generator_vintage = psspy.amachint(-1, 4, 'OWN2')

    redispatch_target = 0.0
    for gen_bus, gen_id, gen_pgen, gen_type, gen_status, gen_pmax, gen_pmin, gen_vintage in \
                        zip(generator_buses[0], generator_ids[0], generator_pgen[0], \
                            generator_types[0], generator_status[0], \
                            generator_pmax[0], generator_pmin[0], generator_vintage[0]):

        ## print "RDT:", redispatch_target
        
        err, gen_bus_zone = psspy.busint(gen_bus, 'ZONE') ## Identify the bus zone
      
        if gen_type in solar_categories and gen_bus_zone in res_increase_assumptions[operational_scenario]['solar'][1] and gen_vintage != 883: 

            err, gen_name = psspy.notona(gen_bus)

            if debug:
                print chr(27), "\nRES/solar | Zone:", gen_bus_zone, "| Details:", gen_name, gen_bus, gen_id, \
                      "| Re-dispatching from", round(gen_pgen, 1), "MW to", \
                      round(gen_pmax * res_increase_assumptions[operational_scenario]['solar'][0] / 100.0, 1), "MW -> i.e.", \
                      res_increase_assumptions[operational_scenario], "% of output"

            err = psspy.machine_chng_2(gen_bus, gen_id,[1],[(gen_pmax * res_increase_assumptions[operational_scenario]['solar'][0] / 100.0)])

            redispatch_target -= (gen_pmax * res_increase_assumptions[operational_scenario]['solar'][0] / 100.0) - gen_pgen 

            if debug: print "   - Redispatch =", round(redispatch_target, 1), "MW"

            ## Set the power factor to 0.95
            psspy.machine_chng_2(gen_bus, gen_id,[_i,_i,_i,_i,_i,2],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f, 0.95])
            psspy.plant_data(gen_bus,_i,[ 1.05,_f])

        elif gen_type in onshore_categories and gen_bus_zone in res_increase_assumptions[operational_scenario]['onshore'][1] and gen_vintage != 883: 

            err, gen_name = psspy.notona(gen_bus)

            if debug:
                print chr(27), "\nRES/onshore | Zone:", gen_bus_zone, "| Details:", gen_name, gen_bus, gen_id, \
                      "| Re-dispatching from", round(gen_pgen, 1), "MW to", \
                      round(gen_pmax * res_increase_assumptions[operational_scenario]['onshore'][0] / 100.0, 1), "MW -> i.e.", \
                      res_increase_assumptions[operational_scenario], "% of output"

            err = psspy.machine_chng_2(gen_bus, gen_id,[1],[(gen_pmax * res_increase_assumptions[operational_scenario]['onshore'][0] / 100.0)])

            redispatch_target -= (gen_pmax * res_increase_assumptions[operational_scenario]['onshore'][0] / 100.0) - gen_pgen 

            if debug: print "   - Redispatch =", round(redispatch_target, 1), "MW"

            ## Set the power factor to 0.95
            psspy.machine_chng_2(gen_bus, gen_id,[_i,_i,_i,_i,_i,2],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f, 0.95])
            psspy.plant_data(gen_bus,_i,[ 1.05,_f])

        elif gen_type in offshore_categories and gen_bus_zone in res_increase_assumptions[operational_scenario]['offshore'][1] and gen_vintage != 883: 

            err, gen_name = psspy.notona(gen_bus)

            if debug:
                print chr(27), "\nRES/offshore | Zone:", gen_bus_zone, "| Details:", gen_name, gen_bus, gen_id, \
                      "| Re-dispatching from", round(gen_pgen, 1), "MW to", \
                      round(gen_pmax * res_increase_assumptions[operational_scenario]['offshore'][0] / 100.0, 1), "MW -> i.e.", \
                      res_increase_assumptions[operational_scenario], "% of output"

            err = psspy.machine_chng_2(gen_bus, gen_id,[1],[(gen_pmax * res_increase_assumptions[operational_scenario]['offshore'][0] / 100.0)])

            redispatch_target -= (gen_pmax * res_increase_assumptions[operational_scenario]['offshore'][0] / 100.0) - gen_pgen 

            if debug: print "   - Redispatch =", round(redispatch_target, 1), "MW"

            ## Set the power factor to 0.95
            psspy.machine_chng_2(gen_bus, gen_id,[_i,_i,_i,_i,_i,2],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f, 0.95])
            psspy.plant_data(gen_bus,_i,[ 1.05,_f])

        elif gen_type in interconnector_categories:

            if "sv" in each_raw_file.lower() or "sm" in each_raw_file.lower() or "snv" in each_raw_file.lower():
                if debug: print "\n - Interconnection -> 50% export:", gen_bus, gen_id, gen_pmin / 2.0, \
                   "| Change from", gen_pgen, "to", gen_pmin / 2.0, "MW"
                err = psspy.machine_chng_2(gen_bus, gen_id,[1],[gen_pmin / 2.0])
                redispatch_target += abs((gen_pmin / 2.0) - gen_pgen) ## Therefore INCREASE the redispatch target
                if debug: print "   - Redispatch =", redispatch_target

            else:
                if debug: print "\n - Interconnection -> 100% export:", gen_bus, gen_id, \
                   "| Change from", gen_pgen, "to", gen_pmin, "MW"
                err = psspy.machine_chng_2(gen_bus, gen_id,[1],[gen_pmin])
                redispatch_target += abs(gen_pmin - gen_pgen) ## Therefore INCREASE the redispatch target
                if debug: print "   - Redispatch =", redispatch_target

    print "\nNeed to re-dispatch (change generation):", round(redispatch_target, 1), "MW"
    redispatch_remainder = execute_redispatch(merit_order, redispatch_target)
   
    if redispatch_remainder < -50.0:

        print "\nWarning! Still need to reduce generation to ensure a reasonable generation-demand balance!\n"

        err = psspy.rawd_2(0,1,[1,1,1,0,0,0,0],0, filelocation + "\\Simulation " + \
                           time_stamp + "\\Debug\\case_before_res_scaling_help.raw")

        ## Generation check
        err, pre_scal_system_generation = psspy.systot('GEN')
        print " - Pre-SCAL Generation:", round(pre_scal_system_generation.real, 1), "MW"

        ## Load check
        err, pre_scal_system_load = psspy.systot('LOAD')
        print " - Pre-SCAL Load:", round(pre_scal_system_load.real, 1), "MW"

        ## Identify zones to minimise
        minimise_these_zones = []
        maximise_these_zones = []
        for k, v in res_increase_assumptions[operational_scenario].items():
            for max_zone_data in v[1]:
                if max_zone_data not in maximise_these_zones:
                    maximise_these_zones.append(max_zone_data)
        for each_zone in ai_zones:
            if each_zone not in maximise_these_zones:
                minimise_these_zones.append(each_zone)

        print "\nCan minimise RES in these non-study area zones:", minimise_these_zones

        ## Select non-study area subsystems
        err = psspy.bsys(0,0,[ 0.4, 380.0],0,[],0,[],0,[],len(minimise_these_zones),minimise_these_zones)
        err = psspy.bsys(0,0,[ 0.4, 380.0],0,[],0,[],0,[],len(minimise_these_zones),minimise_these_zones)

        err, totals, moto = psspy.scal_2(0,0,1,[0,0,0,0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0])
        print "\nAvailable generation that can be scheduled down:", round(totals[2], 1), "MW"

        new_non_study_zone_total = totals[2] + redispatch_remainder
        print "\nReduce generation in non-study zones to:", round(new_non_study_zone_total, 1), "MW"

        ## Activate the scaling of RES in the non-study zones
        enforce_machine_limits = False
        if enforce_machine_limits:
            err, totals, moto = psspy.scal_2(0,1,2,[_i,1,1,1,0],[_f,new_non_study_zone_total,_f,_f,_f,_f,_f])
        else:
            err, totals, moto = psspy.scal_2(0,1,2,[_i,1,0,1,0],[_f,new_non_study_zone_total,_f,_f,_f,_f,_f])
        print "\nRemaining generation in the non-study zones:", round(totals[2], 1), "MW"

        ## Re-select subsystem selection
        psspy.bsys(0,0,[ 0.4, 380.],0,[],0,[],0,[],len(ai_zones),ai_zones)

        ## Generation check
        err, post_scal_system_generation = psspy.systot('GEN')
        print "\n - Post-SCAL Generation:", round(post_scal_system_generation.real, 1), "MW"
    
        ## Load check
        err, post_scal_system_load = psspy.systot('LOAD')
        print " - Post-SCAL Load:", round(post_scal_system_load.real, 1), "MW"

    err = psspy.rawd_2(0,1,[1,1,1,0,0,0,0],0, filelocation + "\\Simulation " + \
                       time_stamp + "\\Debug\\case_after_res_changes.raw")
    

## This function makes the shaping changes
## =================================================================================
def apply_soef_changes(operational_season):

    if operational_season == 'winter': seasonal_rating = 'winter'
    else: seasonal_rating = 'summer'

    soef_uprates = {

                 ## 110 kV uprates
                 'Crane Wexford 110kV': [1841, 5501, "1", 1, 178, 210],
                 'Athy Carlow 110kV': [1221, 1901, "1", 1, 178, 210],
                 'Maynooth Timahoe 110kV': [3841, 5211, "1", 1, 178, 210],
                 'Maynooth Rinawade 110kV': [3851, 4741, "1", 1, 178, 210],
                 'Kilteel Maynooth 110kV': [3241, 3841, "1", 1, 178, 210],
                 'Great Island Kilkenny 110kV': [2741, 3261, "1", 1, 178, 210],
                 'Baroda Monread 110kV': [1351, 4081, "1", 1, 178, 210],
                 'Killoteran Waterford 110kV': [3401, 5441, "1", 1, 178, 210],

                 ## Dublin cable uprates
                 'Carrickmines Poolbeg 220kV': [17431, 4472, "1", 1, 537, 606],
                 'Finglas North Wall 220kV': [2563, 4242, "1", 1, 537, 606],
                 'North Wall Poolbeg 220kV': [4242, 4462, "1", 1, 537, 606],
                 'Inchicore Poolbeg 220kV 1': [30820, 4472, "1", 1, 537, 606],
                 'Inchicore Poolbeg 220kV 2': [30820, 4472, "2", 1, 537, 606],

                 ## 220 kV uprates
                 'Great Island Kellis 220kV': [2742, 3342, "1", 1, 793, 824], 

                 ## *** NOT SOEF ***
                 'Arklow - Carrickmines 220kV': [1122, 1742, "1", 1, 793, 824], 
                 'Arklow - Ballybeg 220kV': [1122, 1302, "1", 1, 793, 824], 
                 'Ballybeg - Carrickmines 220kV': [1302, 1742, "1", 1, 793, 824],
                 'Great Island - Lodgewood 220kV': [2742, 3642, "1", 1, 793, 824],
                 'Arklow - Lodgewood 220kV': [1122, 3642, "1", 1, 793, 824],

                 }

    ## Impedance data
    rxb_data = {    
                'ohl': {'110.0': [0.000628, 0.003248, 0.000352], 
                        '220.0': [0.000135868, 0.000853512, 0.001357857],             
                        '380.0': [0.000019, 0.000222,	0.005047]
                        }, 

                'ugc': {'110.0': [0.0003, 0.001, 0.011],           ## Based on 1000 XLPE Cu from PLANET
                        '220.0': [0.00002, 0.000389, 0.02737],     ## Based on 1600 XLPE Cu from PLANET [Planet: 0.000032, 0.000389, 0.02737]
                        '380.0': [0.000003, 0.00001, 0.035],       ## JK estimate - to be updated
                        }
                }

    ## Rating data
    ratings_data = {
        
        'ohl': {
            '110.0': {'summer': 178.0, 'winter': 210.0, 'autumn': 194.0, 'type': "430 mm2 ACSR 'Bison'"},
            '220.0': {'summer': 434.0, 'winter': 513.0, 'autumn': 474.0, 'type': "600 mm2 ACSR 'Curlew'"},
            ##'220_uprate': {'summer': 793.0, 'winter': 824.0, 'autumn': 808.0, 'type': "586 mm2 GZTACSR 'Traonach'"},
            '380.0': {'summer': 1578.0, 'winter': 1867.0, 'autumn': 1722.0, 'type': "2 x 600 mm2 ACSR 'Curlew'"}        
                },
        'ugc': {
            '110.0': {'summer': 196.0, 'winter': 221.0, 'autumn': 202.0, 'type': '1000 mm2 Cu XLPE'}, ## assumed trefoil duct formation
            '220.0': {'summer': 537.0, 'winter': 606.0, 'autumn': 556.0, 'type': '1600 mm2 Cu XLPE'}, ## assumed direct buried flat formation        
            '380.0': {'summer': 1218.0, 'winter': 1377.0, 'autumn': 1264.0, 'type': '2500 mm2 Cu XLPE'} ## assumed flat formation
                }
        }
    
    ## Upvoltage Arklow - Ballybeg - Carrickmines circuit
    ## Remove 110 kV circuits
    psspy.purgbrn(1301, 17411, "1")
    psspy.purgbrn(1121, 1301, "1")
    
    ## Add Ballybeg 220 kV station & two transformers
    ## WARNING! Not using 13021 because it already exists in the case
    main_station_name = "Ballybeg"
    psspy.bus_data_3(1302, [_i,6,9,3], [220.0, _f, _f,_f,_f,_f,_f], main_station_name)    
    psspy.bus_data_3(13022, [_i,6,9,3], [10.5, _f, _f,_f,_f,_f,_f], main_station_name)

    psspy.three_wnd_imped_data_3(1302, 1301, 13022, r"""1""", \
                                 [1,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i], \
                                 [ 0.00048, 0.072, 0.002, 0.02,-0.199999E-04, 0.067,_f, 250.0,_f,_f,_f,_f,_f,_f,_f, 1.06424, 5.26142], \
                                 [main_station_name,""])

    psspy.three_wnd_imped_data_3(1302, 1301, 13022, r"""2""", \
                                 [1,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i], \
                                 [ 0.00048, 0.072, 0.002, 0.02,-0.199999E-04, 0.067,_f, 250.0,_f,_f,_f,_f,_f,_f,_f, 1.06424, 5.26142], \
                                 [main_station_name,""])

    ## Add model for upvoltaged circuit
    length_of_ckm_bge = 27.0
    psspy.branch_data(1742, 1302, "1",[_i,_i,1,_i,_i,_i], \
                      [rxb_data['ohl']['220.0'][0] * length_of_ckm_bge, \
                       rxb_data['ohl']['220.0'][1] * length_of_ckm_bge, \
                       rxb_data['ohl']['220.0'][2] * length_of_ckm_bge, \
                       ratings_data['ohl']['220.0'][seasonal_rating], \
                       ratings_data['ohl']['220.0'][seasonal_rating], \
                       ratings_data['ohl']['220.0'][seasonal_rating], \
                       _f,_f,_f,_f, length_of_ckm_bge,_f,_f,_f,_f])
    length_of_ark_ckm = 27.0
    psspy.branch_data(1122, 1302, "1",[_i,_i,1,_i,_i,_i], \
                      [rxb_data['ohl']['220.0'][0] * length_of_ckm_bge, \
                       rxb_data['ohl']['220.0'][1] * length_of_ckm_bge, \
                       rxb_data['ohl']['220.0'][2] * length_of_ckm_bge, \
                       ratings_data['ohl']['220.0'][seasonal_rating], \
                       ratings_data['ohl']['220.0'][seasonal_rating], \
                       ratings_data['ohl']['220.0'][seasonal_rating], \
                       _f,_f,_f,_f, length_of_ark_ckm,_f,_f,_f,_f])

    ## Add Carrickmines Inchicore
    length_of_ckm_inc = 20.0
    psspy.branch_data(1742, 3082, "1",[_i,_i,1,_i,_i,_i], \
                      [rxb_data['ugc']['220.0'][0] * length_of_ckm_inc, \
                       rxb_data['ugc']['220.0'][1] * length_of_ckm_inc, \
                       rxb_data['ugc']['220.0'][2] * length_of_ckm_inc, \
                       ratings_data['ugc']['220.0'][seasonal_rating], \
                       ratings_data['ugc']['220.0'][seasonal_rating], \
                       ratings_data['ugc']['220.0'][seasonal_rating], \
                       _f,_f,_f,_f, length_of_ckm_inc,_f,_f,_f,_f])
    
    
    print "\nChanging circuit parameters of the following circuits:"
    for k, v in soef_uprates. items():
        if debug:
            print " -", k
        if 'summer' in operational_season:
            err = psspy.branch_chng(v[0], v[1], v[2], [v[3]],[_f,_f,_f, v[4], v[4], v[4]])
        else:
            err = psspy.branch_chng(v[0], v[1], v[2], [v[3]],[_f,_f,_f, v[5], v[5], v[5]])
        if err != 0:
            print "***** Error! Check circuit details for", k, "! *****"
            quit()
    

####################################################################################
##                              START OF MAIN SCRIPT                              ##
####################################################################################

def run_mobu():
    
    ## Make sure the user is using the script correctly!
    if add_machines_to_model and add_loads_to_model:
        print "\nWARNING! The script isn't set up to increment both generation & load!\n"
        quit()
    if add_loads_to_model and option_to_set_res_to_max:
        print "\nWARNING! Incorrect to test a load connection with high RES!\n"
        quit()

    psspy, pssarrays, _i, _f, _s = run_inital_setup_activities()

    ## Deal with progress output - supress for now
    psspy.progress_output(2,"Progress_record",[0,0])
    psspy.lines_per_page_one_device(2,10000000)

    ## Add some base case data
    print "\nReading changes from", tytfs_file_name, "that are required for the base case..."
    if make_tytfs_base_case_changes:
        base_case_changes_dict = read_base_case_data(debug, tytfs_file_name)

    list_of_raw_files = read_raw_files_in_working_folder()
    if len(list_of_raw_files) == 0:
        print "\nALERT! No *.raw files detected!"
        quit()

    psse_major_version = 33

    global system_mismatch_target 
    system_mismatch_target = 5.0

    no_of_iterations = 999

    check_file = open("model_error_check_list.dat", "w")

    global connection_increment
    global connection_step_size

    ## If looking at a single load connection cosider increments
    if add_loads_to_model and len(add_loads_dict) == 1:
        for k, v in add_loads_dict.items():
            ultimate_connection_size = v[2]
        connection_increment = 0.0
        connection_step_size = 50.0

    ## If looking at a single generation connection cosider increments
    elif add_machines_to_model and len(add_machines_dict) == 1:
        for k, v in add_machines_dict.items():
            ultimate_connection_size = v[2]
        connection_increment = 0.0
        connection_step_size = generation_increment

    ## If looking at multiple load connections don't consider increments ##KC
    elif add_loads_to_model and len(add_loads_dict) > 1: ##KC
        for k, v in add_loads_dict.items(): ##KC
            ultimate_connection_size = v[2] ##KC
            connection_increment = 0.0 ##KC
            connection_step_size = v[2] ##KC

    ## Otherwise there is no connection
    else:
        connection_increment = 0.0
        ultimate_connection_size = 0.0

    ## Make the dispatch spreadsheet
    if run_n_minus_one_analysis:

        ## Kill Excel to ensure COM error doesn't appear
        import subprocess
        subprocess.call(["taskkill", "/f", "/im", "EXCEL.EXE"])
        
        xls_2 = win32com.client.gencache.EnsureDispatch("excel.application")
        xls_2.DisplayAlerts = False
        xls_2.Visible = True
        xls_2.Workbooks.Add()

        ws_2 = xls_2.Worksheets.Add()
        ws_2.Name = str("N-1 Results")

        ## Some basic headers
        if add_machines_to_model:
            header_input = "Generation\n(MW)"
        elif add_loads_to_model:
            header_input = "Load\n(MW)"
        else:                           #KC
            header_input = "Case\n"     #KC
        headers = ["Case Name\n", header_input, "STATCOM\n(Mvar)", "Overloaded Circuit\n", \
                       "Contingency\n", "Rating\n(MVA)", "Loading\n(% MVA)", "TH\n(MW)", "Losses\n(MW)", "Load Error\n(MW)", \
                       "System Mismatch\n(MVA)", "PST Angle [N]", "PST Angle [N-1]"]
        row, col = 1, 1
        for h in headers:
            ws_2.Cells(row, col).Value = h
            ws_2.Cells(row, col).Font.Bold = True
            col += 1
        row = 2

    plot_circuit_loadings_dict = {}
    plot_circuit_loadings_dict[add_machines_dict.keys()[0]] = {}

    ratings_dict = {}

    ## Identify time stamp
    global time_stamp
    import time
    from time import gmtime, strftime, localtime
    time_stamp = time.strftime("%d%b%Y_%H%M%S", localtime())

    while connection_increment <= ultimate_connection_size:

        ## Loop through each *.raw file
        for each_raw_file in list_of_raw_files:

            ## To avoid clutter, save the cases in a folder
            if not os.path.isdir("Simulation " + time_stamp + "\\Debug"):
                os.makedirs("Simulation " + time_stamp + "\\Debug")

            ## Read each *.raw file
            raw_file_err = psspy.readrawversion(0, str(psse_major_version), each_raw_file)
            if raw_file_err != 0:
                print"\nError reading the *.raw file:", each_raw_file 
                quit()
            else:                
                print "\nSuccessfully reading the *.raw file:", each_raw_file
                print "------------------------------------------------------"

            ## Set the data centre level
            ## Note that the Kellystown load is treated as a data centre by EirGrid
            if change_data_centre_level:

                print "\nChanging the data centre load to:", new_data_centre_total, "MW"

                ## Define Kellystown as part of the data centre load
                err = psspy.mbidload(33502,r"""I""",r"""DC""")

                ## Initial data centre load tally
                err, ld_nums = psspy.aloadint(-1, 4, 'NUMBER')
                err, ld_ids = psspy.aloadchar(-1, 4, 'ID')
                err, ld_status = psspy.aloadint(-1, 4, 'STATUS')
                err, ld_mw = psspy.aloadcplx(-1, 4, 'MVAACT')
                total_dc_load = 0.0
                for a, b, c, d in zip(ld_nums[0], ld_ids[0], ld_status[0], ld_mw[0]):
                    if b == "DC" and c == 1:
                        total_dc_load += d.real
                print " -> Exiting in-service data centre load:", round(total_dc_load, 1), "MW"

                ## Change the data centre loads
                dc_scalar = new_data_centre_total / total_dc_load
                for a, b, c, d in zip(ld_nums[0], ld_ids[0], ld_status[0], ld_mw[0]):
                    if b == "DC" and c == 1:
                        psspy.load_chng_4(a, b, [], [d.real * dc_scalar,_f,_f,_f,_f,_f])

                ## check data centre load tally
                err, ld_nums = psspy.aloadint(-1, 4, 'NUMBER')
                err, ld_ids = psspy.aloadchar(-1, 4, 'ID')
                err, ld_status = psspy.aloadint(-1, 4, 'STATUS')
                err, ld_mw = psspy.aloadcplx(-1, 4, 'MVAACT')
                check_dc_load = 0.0
                for a, b, c, d in zip(ld_nums[0], ld_ids[0], ld_status[0], ld_mw[0]):
                    if b == "DC" and c == 1:
                        check_dc_load += d.real
                print " -> Checking in-service data centre load:", round(check_dc_load, 1), "MW"
                if round(check_dc_load, 1) == round(new_data_centre_total, 1):
                    print " -> Data centre load has been updated successfully!"
                else:
                    print " -> Warning! It does not appear that the data load has not been scaled correctly!"
                    quit()

                print "\nRe-dispatching to keep the swing bus at a similar output:", \
                      round(new_data_centre_total - total_dc_load, 1), "MW"
                redispatch_remainder = execute_redispatch(merit_order, new_data_centre_total - total_dc_load)
                
            ## Clean dispatch - if a machine is off-line ensure that it is dispatched to 0 MW
            err, generator_buses = psspy.amachint(-1, 4, 'NUMBER')    
            err, generator_status = psspy.amachint(-1, 4, 'STATUS')    
            err, generator_ids = psspy.amachchar(-1, 4, 'ID')
            for gen_bus, gen_id, gen_status in zip(generator_buses[0], generator_ids[0], generator_status[0]):
                if gen_status == 0:
                    ## if debug: print " - Set off-line unit", gen_id, "at bus", gen_bus, "to zero"
                    err = psspy.machine_chng_2(gen_bus, gen_id,[],[0.])
        
            check_file.write("\n" + each_raw_file + "\n")

            ## Set solution parameters
            psspy.solution_parameters_4([_i, no_of_iterations],[])

            ## Give each *.raw file a meaningful internal title x 2
            if add_loads_to_model:
                err = psspy.case_title_data("MOBU Ireland Technical Analysis - Jeff Kelliher", \
                                            "LOAD STUDY: To test a load connection")
            if add_machines_to_model:
                err = psspy.case_title_data("MOBU Ireland Technical Analysis - Jeff Kelliher", \
                                            "GENERATION STUDY: To test a generation connection")

            ## Identify the season - based on the *.raw file name
            if "wp" in each_raw_file.lower():
                operational_scenario = 'winter peak'
            elif "sp" in each_raw_file.lower():
                operational_scenario = 'summer peak'
            else:
                operational_scenario = 'summer valley'
            print "\nThe case is a", operational_scenario, "*.raw file"

            ## Combine RES categories - not allowing the consider solar PV in summer valley
            if operational_scenario == 'summer valley':
                res_categories = onshore_categories + offshore_categories
            else:
                res_categories = solar_categories + onshore_categories + offshore_categories
                
            ## Scale the load if required
            if change_peak_demand_level:

                print "\nModifying the peak load as follows:"
                
                ## Slightly rounded-up median winter peak target based on TYTFS '20
                new_demand = 7690.0 ##2025 study year  #7795.0 ## 2026 study year

                ## Planet database assumes that summer peak load is 80% of the winter peak load
                if 'summer peak' in operational_scenario:                
                    new_demand = new_demand * 0.8
                    err, old_load = psspy.systot('LOAD')
                    redispatch_target = new_demand - round(old_load.real, 0)
                    print "\nNeed to redispatch (increase other generation):", round(redispatch_target, 1), "MW"
                    redispatch_remainder = execute_redispatch(merit_order, redispatch_target)
                    print " - Setting summer peak load to:", new_demand
                else:
                    err, old_load = psspy.systot('LOAD')
                    print " - Setting winter peak load to:", new_demand, old_load
                    redispatch_target = new_demand - round(old_load.real, 0)
                    print "\nNeed to redispatch (increase other generation):", round(redispatch_target, 1), "MW"
                    redispatch_remainder = execute_redispatch(merit_order, redispatch_target)
                ## Make sure we don't scale fixed loads - such as industrial or data centre
                err, ld_nums = psspy.aloadint(-1, 4, 'NUMBER')
                err, ld_ids = psspy.aloadchar(-1, 4, 'ID')
                do_not_scale_these = ["I", "MI", "DC"]
                for a, b in zip(ld_nums[0], ld_ids[0]):

                    ## Remove house load
                    if b == "HL": psspy.load_chng_4(a, b,[0],[])

                    ## Set industrial & data centre loads as non-scaleable
                    if string.lstrip(string.rstrip(b)) in do_not_scale_these:
                        psspy.load_chng_4(a, b,[_i,_i,_i,_i,0],[])
                    else:
                        psspy.load_chng_4(a, b,[_i,_i,_i,_i,1],[])
                
                ## Execute the load scaling
                err = psspy.scal_2(0,1,1,[0,0,0,0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0])
                print err
                err = psspy.scal_2(0,1,2,[_i,1,0,1,0],[new_demand, _f, _f, _f, _f, _f, _f])
                print err

            if enhance_voltage_profile:
                fix_transformers(operational_scenario)

            if run_n_minus_one_analysis:
                
                err = psspy.rawd_2(0,1,[1,1,1,0,0,0,0],0, filelocation + "\\Simulation " + \
                                   time_stamp + "\\Debug\\pre-solution_file.raw")

                mis = general_model_solution()
                if mis > system_mismatch_target:
                    print "\nSolution is NOT great! Mismatch:", round(mis, 3), "MVA"
                    print "\n -> Not performing N & N-1 analysis..."
                    continue

                print "\nSome key initial checks:"

                ## Load check
                err, initial_system_load = psspy.systot('LOAD')
                print " - Load:\t\t", round(initial_system_load.real, 1), "MW"

                ## Generation check
                err, initial_system_generation = psspy.systot('GEN')
                print " - Generation:\t\t", round(initial_system_generation.real, 1), "MW"

                ## Losses check
                err, initial_losses = psspy.systot('LOSS')
                print " - Losses:\t\t", round(initial_losses.real, 1), "MW"
                
                ## Initial Turlough Hill check
                initial_th_mw = 0.0
                for th_unit in range(1, 5):
                    err, temp = psspy.macdat(int(str(5207) + str(th_unit)), str(th_unit), "P")
                    initial_th_mw += temp
                print " - Turlough Hill:\t", round(initial_th_mw, 1), "MW"

                ## Re-set swing bus to close to zero MW
                if option_to_set_res_to_max:
                    redispatch_remainder = execute_redispatch(merit_order, initial_th_mw)

                ## Basic solve & check
                psspy.fdns([0,0,0,0,1,0,0,0])
                
                ## Another Turlough Hill check
                initial_th_mw = 0.0
                for th_unit in range(1, 5):
                    err, temp = psspy.macdat(int(str(5207) + str(th_unit)), str(th_unit), "P")
                    initial_th_mw += temp
                print " - Turlough Hill:\t", round(initial_th_mw, 1), "MW"

            ## Fix some errors in the Eirgrid *.raw files
            make_fixes_to_eirgrid_model(each_raw_file)

            ## Add projects from the 'Shaping Our Electricity Future' roadmap
            if add_soef_projects: apply_soef_changes(operational_scenario)
           
            ## Make adjustments based on TYTFS data
            ## ====================================
            if make_tytfs_base_case_changes:
                    
                ## First, add new stations
                ## -----------------------
                print "\nAdding station data:"
                import re
                for k1, v1 in base_case_changes_dict.items():
                    for k2, v2 in v1.items():
                        if 'station' in k2.lower():

                            if debug: print k1, k2, v2,
                            ## Get station base voltage
                            try:
                                station_voltage = float(re.findall(r'\d+', k1)[-2])
                                if station_voltage == 400.0: station_voltage = 380.0
                            except:
                                print " WARNING! No station base voltage available for", k1
                                check_file.write("     Missing station voltage data: " + k1 + "\n")
                                continue      
                            if debug: print station_voltage,

                            ## Get the station name
                            station_name = k1.split()[0]
                            if debug: print station_name

                            ## Get the station bus numer
                            station_bus_num = v2[0] 
                            if debug: print station_name

                            err = psspy.bus_data_3(station_bus_num,[],[station_voltage,_f,_f, 1.091, 0.95, 1.091, 0.9], station_name)
                            if err != 0:
                                print " ***** Error", err, "adding station data for", k1, "*****"
                                if err == 1:
                                    check_file.write("     Invalid bus number for: " + k1 + "\n")
                                else:
                                    check_file.write("     New station data: " + k1 + "\n")
                            else:
                                print " Successfully added station data for", k1
                                

                ## Second, add circuits stations
                ## -----------------------------
                print "\nAdding new circuit data (OHL or UGC):"
                for k1, v1 in base_case_changes_dict.items():
                    for k2, v2 in v1.items():
                        if 'add' in k2.lower() and 'circuit' in k2.lower():

                            print " \n Adding a branch between", v2[0], "and", v2[1], "- id:", v2[2]
                            
                            if 'summer' in operational_scenario: rating = v2[3]
                            else: rating = v2[4]
                            err = psspy.branch_data(v2[0], v2[1], str(v2[2]), [], [v2[6], v2[7], v2[8], rating, rating, rating, _f, _f, _f, _f, v2[5]])

                            ## Deal with buses that may not exist
                            if err == 1:
                                print "   Initial problem with branch data - station may not exist..."
                                ## Does from bus exist?
                                err = psspy.busexs(v2[0])
                                if err != 0:
                                    print "      The 'from' bus", v2[0], "does not exist ->",
                                    station_voltage = float(re.findall(r'\d+', k1)[-2])
                                    if station_voltage == 400.0: station_voltage = 380.0  
                                    station_name = k1.split()[0]
                                    print station_name
                                    err = psspy.bus_data_3(v2[0],[],[station_voltage,_f,_f, 1.091, 0.95, 1.091, 0.9], station_name)
                                ## Does to bus exist?
                                err = psspy.busexs(v2[1])
                                if err != 0:
                                    print "      The 'to' bus", v2[1], "does not exist ->",
                                    station_voltage = float(re.findall(r'\d+', k1)[-2])
                                    if station_voltage == 400.0: station_voltage = 380.0
                                    station_name = k1.split()[1]
                                    print station_name
                                    err = psspy.bus_data_3(v2[1],[],[station_voltage,_f,_f, 1.091, 0.95, 1.091, 0.9], station_name)
                                err = psspy.branch_data(v2[0], v2[1], str(v2[2]), [], [v2[6], v2[7], v2[8], rating, rating, rating, _f, _f, _f, _f, v2[5]])
                                if err != 0:
                                    print "         Still an error", err
                                    check_file.write("     New circuit data issue: " + k1 + "\n")
                                else:
                                    print "         Successfully added branch data between buses", v2[0], "and", v2[1]                                                
                            elif err != 0:
                                print " ***** Error", err, "adding branch data between buses", v2[0], "and", v2[1], "*****"
                                check_file.write("     New circuit data: " + k1 + "\n")
                            else:
                                print "    Successfully added branch data between buses", v2[0], "and", v2[1]

                ## Third, remove circuits
                ## ----------------------
                print "\nRemoving circuit data:"
                for k1, v1 in base_case_changes_dict.items():
                    for k2, v2 in v1.items():
                        if 'remove' in k2.lower() and 'circuit' in k2.lower():

                            if debug: print " Removing the circuit with buses", v2[0], v2[1]
                            err = psspy.purgbrn(v2[0], v2[1], str(v2[2]))
                            if err != 0:
                                print " ***** Error", err, "removing circuit data connecting buses", v2[0], v2[1], "*****"
                                err = psspy.busexs(v2[0])
                                if err != 0: print "The bus", v2[0], "doesn't appear to exist!"
                                err = psspy.busexs(v2[1])
                                if err != 0: print "The bus", v2[1], "doesn't appear to exist!"
                                if err == 2: print "Branch not found"
                                check_file.write("     Removing circuit issue (bus number or id): " + k1 + "\n")
                            else:
                                print " Successfully removed circuit data connecting buses", v2[0], v2[1]


                ## Fourth, amending/uprating circuits
                ## ----------------------------------
                print "\nAmending/uprating data:"
                for k1, v1 in base_case_changes_dict.items():
                    for k2, v2 in v1.items():
                        if 'amend' in k2.lower() and 'circuit' in k2.lower():

                            if debug: print " Amending the circuit with buses", v2[0], v2[1]
                            if 'summer' in operational_scenario: rating = v2[3]
                            else: rating = v2[4]
                            err = psspy.branch_data(v2[0], v2[1], str(v2[2]), [], [v2[6], v2[7], v2[8], rating, rating, rating, _f, _f, _f, _f, v2[5]])
                            if err != 0:
                                print " ***** Error", err, "amending branch data between buses", v2[0], "and", v2[1], "*****"
                                check_file.write("     Amending circuit data: " + k1 + "\n")
                            else:
                                print " Successfully amended circuit data connecting buses", v2[0], v2[1]
                                

                ## Fifth, removing transformer data
                ## --------------------------------
                print "\nRemoving transformer data:"
                for k1, v1 in base_case_changes_dict.items():
                    for k2, v2 in v1.items():
                        if 'remove' in k2.lower() and 'transformer' in k2.lower():

                            if debug: print " Removing transformer with buses", v2[0], v2[1], v2[-1]
                            err = psspy.purg3wnd(v2[0], v2[1], v2[-1], v2[2])
                            if err != 0:
                                print " ***** Error", err, "removing transformer data between buses", v2[0], v2[1], "and", v2[-1], "*****"
                                check_file.write("     Removing transformer data issue: " + k1 + "\n")                    
                            else:
                                print " Successfully removed transformer data connecting buses", v2[0], v2[1], v2[2]
                                psspy.bsysinit(1)
                                psspy.bsyso(1, v2[-1])
                                psspy.extr(1,0,[0,0])


                ## Sixth, adding new transformer data
                ##  Assume:
                ##  - 220/110 kV: 250 MVA
                ##  - 400/110, 400/220 & 400/275 kV: 500 MVA
                ## -----------------------------------------
                print "\nAdding transformer data:"
                for k1, v1 in base_case_changes_dict.items():
                    for k2, v2 in v1.items():
                        if 'add' in k2.lower() and 'transformer' in k2.lower():

                            print " \nAdding transformer with buses", v2[0], v2[1], v2[-1]
                            
                            transformer_name = k1.split()[0]
                            tertiary_winding_voltage = 10.5                
                            err = psspy.bus_data_3(v2[-1],[],[tertiary_winding_voltage], transformer_name)
                            if err == 0:
                                if debug: print " Ensuring there is a tertiary winding bus:", v2[-1]
                            else:
                                print " ***** Error with tertiary winding bus! *****"                    
                            
                            ## What voltage levels are we dealing with? 400/220 kV, 400/110 kV or 220/110 kV
                            err, i_bus_voltage = psspy.busdat(v2[0], 'BASE')
                            err, j_bus_voltage = psspy.busdat(v2[1], 'BASE')

                            ## Add the various transformer types
                            if i_bus_voltage in [110.0, 220.0] and j_bus_voltage in [110.0, 220.0]:
                                if i_bus_voltage == j_bus_voltage:
                                    print " ***** Error! Base voltages of two transformer buses are the same! *****"
                                    quit()
                                err, temp = psspy.three_wnd_imped_data_3(v2[0], v2[1], v2[-1], str(v2[2]), [], \
                                                                         [0.001, 0.0646, 0.002, 0.02, 0.0005, 0.0596,_f, 250.0], \
                                                                         [transformer_name,""])
                            elif i_bus_voltage in [400.0, 380.0, 275.0, 220.0] and j_bus_voltage in [400.0, 380.0, 275.0, 220.0]:
                                if i_bus_voltage == j_bus_voltage:
                                    print "Error! Base voltages of two transformer buses are the same!"
                                    quit()
                                err, temp = psspy.three_wnd_imped_data_3(v2[0], v2[1], v2[-1], str(v2[2]), [], \
                                                                         [0.0003, 0.026, 0.0001, 0.18, 0.0001, 0.23, _f, 500.0], \
                                                                         [transformer_name,""])
                            elif i_bus_voltage in [400.0, 380.0, 110.0] and j_bus_voltage in [400.0, 380.0, 110.0]:
                                if i_bus_voltage == j_bus_voltage:
                                    print "Error! Base voltages of two transformer buses are the same!"
                                    quit()
                                err, temp = psspy.three_wnd_imped_data_3(v2[0], v2[1], v2[-1], str(v2[2]),[], \
                                                                         [ 0.00048, 0.072, 0.002, 0.02,-0.199999E-04, 0.067,_f, 500.0], \
                                                                         [transformer_name,""])
                            if err != 0:
                                print " ***** Error", err, "adding transformer data between buses", v2[0], v2[1], "and", v2[-1], "*****"
                                check_file.write("     Adding transformer data issue: " + k1 + "\n")

                                ## Also delete the tertiary winding bus that was just added
                                print " [Also removing the teriary winding bus that was just created]"
                                psspy.bsysinit(1)
                                psspy.bsyso(1,v2[-1])
                                psspy.extr(1,0,[0,0])

                            else:
                                print " Successfully added circuit data connecting buses", v2[0], v2[1]

                            ## Update winding rating data
                            for winding_number in range(1, 4):
                                psspy.three_wnd_winding_data_3(v2[0], v2[1], v2[-1], str(v2[2]), winding_number, [], \
                                                               [_f,_f,_f, v2[3], v2[3], v2[3]])

                ## Sixth, adding interconnector data
                ## ---------------------------------
                print "\nAdding interconnector data:"
                interconnector_owner = 49
                for k1, v1 in base_case_changes_dict.items():
                    for k2, v2 in v1.items():            
                        if 'add' in k2.lower() and 'interconnector' in k2.lower():
                            
                            if debug: print "\nAdding interconnector between buses", v2[0], "and", v2[1]

                            rating_of_ic_circuit = 999.0
                            if 'celtic' in k1.lower(): interconnector_size = 700.0
                            elif 'greenlink' in k1.lower(): interconnector_size = 500.0

                            ## Identify which bus exists & wich one doesn't exist
                            print "-", k1
                            print '   First check:', v2[0], 
                            err_1 = psspy.busexs(v2[0])
                            if err_1 != 0:
                                print "-> bus does not exist", err_1
                                make_this_bus_number = v2[0]
                                err, base_voltage = psspy.busdat(v2[1], "BASE")
                                err, area_data = psspy.busint(v2[1], "AREA")
                                err, zone_data = psspy.busint(v2[1], "ZONE")
                                control_this_bus = v2[1]
                            else:
                                print "-> bus exists"

                            print '   Second check:', v2[1],
                            err_2 = psspy.busexs(v2[1])                            
                            if err_2 != 0:
                                print "-> bus does not exist", err_2
                                make_this_bus_number = v2[1]
                                err, base_voltage = psspy.busdat(v2[0], "BASE")
                                err, area_data = psspy.busint(v2[0], "AREA")
                                err, zone_data = psspy.busint(v2[0], "ZONE")
                                control_this_bus = v2[0]
                            else:
                                print "-> bus exists"

                            if err_1 != 0 and err_2 != 0:
                                print "***** Major problem! Both interconnector buses do not exist! *****"
                                quit()

                            err = psspy.bus_data_3(int(make_this_bus_number), [2, area_data, zone_data, interconnector_owner], \
                                                   [base_voltage, 1.0, 0.0, 1.091, 0.9, 1.2, 0.8], k1.split()[0])
                            if err > 0:
                                print "   Error", err, "creating converter station location bus number", v2[0]
                            else:
                                print "   Successfully added converter station location bus number", v2[0]

                            if err_1 != 0 or err_2 != 0:                      
                                err = psspy.branch_data(v2[0], v2[1], "IC", [], [0.001, 0.01, 0.1, \
                                                                                rating_of_ic_circuit, rating_of_ic_circuit, rating_of_ic_circuit])
                                if err != 0:
                                    print "   Error", err, "creating interconnector between buses", v2[0], "and", v2[1]
                                else:
                                    print "   Successfully added interconnector between buses", v2[0], "and", v2[1]
                            else:
                                print "   No need to add a branch - already exists"
                                
                            ## Add plant data to bus
                            err = psspy.plant_data(make_this_bus_number, control_this_bus, [1.05, 100.0])
                            if err != 0:
                                print "   Error", err, "creating plant data at bus", make_this_bus_number
                            else:
                                print "   Successfully added plant data at bus", make_this_bus_number

                            ## Add machine data to bus
                            hvdc_mvar_capability = 250.0
                            err = psspy.machine_data_2(make_this_bus_number, "~I", [1,_i,_i,_i,_i,1], \
                                                       [0.0, _f, hvdc_mvar_capability, hvdc_mvar_capability * -1.0, \
                                                        interconnector_size, interconnector_size * -1.0, \
                                                        interconnector_size * 1.1, _f,_f, 0.001, 0.01])
                            if err != 0:
                                print "   Error", err, "creating machine data at bus", make_this_bus_number
                            else:
                                print "   Successfully added machine data at bus", make_this_bus_number

            ## Read & add new generation
            if add_renewable_generation: read_and_add_generation_data()

            ## Change the level of offshore wind generation
            if change_offshore_wind_level:

                print "\nScaling the offshore geeneration portfolio to", new_offshore_wind_total, "MW"
                err, gen_buses = psspy.amachint(-1, 4, 'NUMBER')    
                err, gen_ids = psspy.amachchar(-1, 4, 'ID')
                err, gen_types = psspy.amachint(-1, 4, 'OWN1')
                err, gen_pmaxs = psspy.amachreal(-1, 4, 'PMAX')

                '''
                ## Create offshore zone in Zone J -> Zone 99
                for a, b, c, d in zip(gen_buses[0], gen_ids[0], gen_types[0], gen_pmaxs[0]):
                    err, zone_info = psspy.busint(a, 'ZONE')
                    if c in [16] and zone_info == 11: psspy.bus_chng_3(a,[_i,_i,99],[],_s)
                psspy.zone_data(99, "DUB_OFFSHORE")
                '''
                
                ## Check/get offshore total
                offshore_total = 0.0
                for a, b, c, d in zip(gen_buses[0], gen_ids[0], gen_types[0], gen_pmaxs[0]):
                    if c in [16]:
                        offshore_total += d
                print " -> Offshore generation in the model =", round(offshore_total, 1), "MW"

                ## Scale the offshore wind portfolios
                new_offshore_total = 0.0
                offshore_scalar = new_offshore_wind_total / offshore_total
                for a, b, c, d in zip(gen_buses[0], gen_ids[0], gen_types[0], gen_pmaxs[0]):
                    if c in [16]:
                        psspy.machine_chng_2(a, b, [],\
                                             [_f,_f,_f,_f, d * offshore_scalar ,_f, d * 1.1 * offshore_scalar])
                        new_offshore_total += d * offshore_scalar
                        
                print " -> Offshore generation has been scaled to", round(new_offshore_total, 1), "MW"
                            
            ## Save the file prior to any islanding checks
            err = psspy.rawd_2(0,1,[1,1,1,0,0,0,0],0, \
                               filelocation + "\\Simulation " + time_stamp + "\\Debug\\" + \
                               each_raw_file[:-4] + "_connectivity_issue.raw")

            ## Due to sometimes odd arrangements - hot standbys, spares etc. need to check for isolated buses
            print "\nChecking for islanding situations - detected x", 
            err, no_of_islanded_buses = psspy.tree(1, 0)
            print no_of_islanded_buses, "islands"

            ## If not needed, remove the files used to check islanding issues
            if no_of_islanded_buses == 0:
                os.remove(filelocation + "\\Simulation " + time_stamp + \
                          "\\Debug\\" + each_raw_file[:-4] + "_connectivity_issue.raw")

            ## Otherwise deal with islands
            else:
                while 1:
                    if no_of_islanded_buses == 0:
                        break
                    else:
                        err, no_of_islanded_buses = psspy.tree(2, 1)
                        if no_of_islanded_buses> 0:
                            print "   Disconnecting islanded bus(es)"
                            check_file.write("     Islanding issue - probably with input data. Please investigate!\n")

            ## Carry out a solution to guage how the case is
            if run_n_minus_one_analysis:

                err = psspy.rawd_2(0,1,[1,1,1,0,0,0,0],0, filelocation + "\\Simulation " + \
                                   time_stamp + "\\Debug\\pre-solution_file.raw")
                psspy.fdns([0,0,0,0,1,1,0,0]) ## Flat start
                for solution_tries in range(1, 10):
                    psspy.fdns([0,0,0,0,1,0,0,0])
                    mis = psspy.sysmsm()
                    if mis < system_mismatch_target:
                        print "\nSolution indication is good! Mismatch:", round(mis, 3), "MVA" 
                        break
                else:
                    print "\nSolution is NOT good! Mismatch:", round(mis, 3), "MVA"
                    continue

                ## Intermediate load check
                err, pre_res_system_load = psspy.systot('LOAD')
                print "\nPre-RES-change check on system load:", round(pre_res_system_load.real, 1), "MW"

                ## Intermediate losses check
                err, pre_res_system_losses = psspy.systot('LOSS')
                print "\nPre-RES-change check on system losses:", round(pre_res_system_losses.real, 1), "MW"

                ## Intermediate Turlough Hill check
                pre_res_th_mw = 0.0
                for th_unit in range(1, 5):
                    err, temp = psspy.macdat(int(str(5207) + str(th_unit)), str(th_unit), "P")
                    pre_res_th_mw += temp
                print "\nPre-RES-change check on Turlough Hill:", round(pre_res_th_mw, 1), "MW"

            ## Uprate 110 kV circuits
            if uprate_all_110kv_to_standard: uprate_110kv_lines_to_standard_ratings(operational_scenario)

            ## [B] Add a station
            if add_stations_to_model:
                add_a_new_station(add_stations_dict)
                station_tag = "_" + str(len(add_stations_dict)) + "STN"
            else:
                station_tag = ""
                
            ## [A] Add a circuit
            if add_circuits_to_model:
                add_a_new_circuit(add_circuits_dict)
                circuit_tag = "_" + str(len(add_circuits_dict)) + "CKT"
            else:
                circuit_tag = ""

            ## [C] Add a load
            if add_loads_to_model:
                mw_for_tag = add_load_to_an_existing_station(add_loads_dict)
                load_tag = "_" + str(len(add_loads_dict)) + "xLD-" + str(int(connection_increment)) + "MW"       
            else:
                load_tag = ""

            ## [D] Add a generator
            if add_machines_to_model:
                mw_for_tag = add_machine_to_an_existing_station(add_machines_dict)
                generation_tag = "_" + str(len(add_machines_dict)) + "xGEN-" + str(int(connection_increment)) + "MW"    
            else:
                generation_tag = ""

            ## [E] Add a STATCOM or some reactive compensation
            if add_reactive_compensation_to_model:
                add_machine_to_an_existing_station(add_reactive_compensation_dict)
                
            ## Remove these generators
            total_removed_conventional_generators = 0 
            if remove_generators_from_model:
                print "\nRemoving these generators from the model:"
                for generators in remove_these_generators:
                    err, machine_status = psspy.macint(generators[0], generators[1], "STATUS")
                    if err in [1, 2]:
                        print "\nWarning! Machine", generators[1], "at bus", generators[0], "does not exist!"
                        quit()
                    err, machine_mw = psspy.macdat(generators[0], generators[1], "P")
                    if err in [1, 2]:
                        print "\nWarning! Machine", generators[1], "at bus", generators[0], "does not exist!"
                        quit()
                    if machine_status == 1 and machine_mw != 0:
                        total_removed_conventional_generators += machine_mw 
                    err = psspy.purgmac(generators[0], generators[1])
                    print " -", generators[0], generators[1], "->", round(machine_mw, 1) * machine_status , "MW" 
                    if err != 0:
                        quit()
                redispatch_remainder = execute_redispatch(merit_order, total_removed_conventional_generators)

            ## Alter data for some circuits
            if uprate_particular_circuits:
                print "\nChanging circuit parameters of the following circuits:"
                for k, v in update_particular_circuit_details. items():
                    if debug:
                        print " -", k
                    if 'summer' in operational_scenario:
                        err = psspy.branch_chng(v[0], v[1], v[2], [v[3]],[_f,_f,_f, v[4], v[4], v[4]])
                    else:
                        err = psspy.branch_chng(v[0], v[1], v[2], [v[3]],[_f,_f,_f, v[5], v[5], v[5]])
                    if err != 0:
                        print "***** Error! Check circuit details for", k, "! *****"
                        quit()

            ## Aghada Knockraha 2 RXB fix
            print "\nCorrecting the RXB value of Aghada Knockraha 2 220 kV"
            psspy.branch_chng(1052,3202,r"""2""",[_i,_i,_i,_i,_i,_i],[ 0.002996, 0.021869, 0.03447,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])

            ## Moneypoint sectionalising
            print "\nClosing Moneypoint 400 kV busbars - regular planning assumption"
            psspy.branch_chng(3944,3954,r"""1""",[1,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])
            psspy.branch_chng(3934,3954,r"""1""",[1,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])

            ## Maynooth sectionalising
            print "\nClosing Maynooth 110 kV and 220 kV busbars - check to make sure this is a valid assumption"
            psspy.branch_chng(3842,3852,r"""1""",[1,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])
            psspy.branch_chng(3841,3851,r"""1""",[1,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])

            ## SHL split for export scenario
            if shl_export_split:
                print "\nSplitting SHL for export"
                psspy.movebrn(50274,5022,r"""1""",4462,r"""1""")
                psspy.branch_chng(5022,5222,r"""1""",[1,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])
                psspy.branch_chng(4462,5022,r"""1""",[0,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])

            ## Deal with RES, depending on the connection type (generation or load)
            ## --------------------------------------------------------------------
            if run_n_minus_one_analysis:

                err = psspy.rawd_2(0,1,[1,1,1,0,0,0,0],0, filelocation + \
                                   "\\Simulation " + time_stamp + "\\Debug\\case_before_res_changes.raw")

                ## Minimise RES is given zones
                if option_to_set_res_to_min:
                    set_solar_and_wind_to_min(merit_order, each_raw_file, res_categories)
                    mis = general_model_solution()
                    if mis > system_mismatch_target:
                        print "\nSolution is NOT great! Mismatch:", round(mis, 3), "MVA"
                        continue

                ## Maximise RES in given zones
                if option_to_set_res_to_max:
                    
                    set_solar_and_wind_to_max(merit_order, each_raw_file, operational_scenario, res_categories)
                    mis = general_model_solution()
                    if mis > system_mismatch_target:
                        
                        print "\nSolution is NOT great! Mismatch:", round(mis, 3), "MVA"
                        print "\nNot attempting N & N-1 analysis..."

                        ## Append previous data with non-convergence indicator
                        import copy
                        temp_plot_circuit_loadings_dict = copy.deepcopy(plot_circuit_loadings_dict)
                        for k0, v0 in temp_plot_circuit_loadings_dict.items():
                            for k1, v1 in v0.items():
                                for k2, v2 in v1.items():                                    
                                    if each_raw_file == k2: 
                                        plot_circuit_loadings_dict[add_machines_dict.keys()[0]][k1][each_raw_file][connection_increment] = 66.666                               
                        continue
               
            ## Carry out a solution to guage how the case is
            if run_n_minus_one_analysis:

                err = psspy.rawd_2(0,1,[1,1,1,0,0,0,0],0, filelocation + "\\Simulation " + \
                                   time_stamp + "\\Debug\\case_before_intermediate_check.raw")
                psspy.fdns([0,0,0,0,1,1,0,0]) ## Flat start
                for solution_tries in range(1, 10):
                    psspy.fdns([0,0,0,0,1,0,0,0])
                    mis = psspy.sysmsm()
                    if mis < system_mismatch_target:
                        print "\nSolution indication is good! Mismatch:", round(mis, 3), "MVA" 
                        break
                    else:
                        print "\nSolution is NOT good! Mismatch:", round(mis, 3), "MVA"
                        continue
                    
                ## Intermediate load check
                err, post_res_system_load = psspy.systot('LOAD')
                print "\nPost-RES change check on system load:", round(post_res_system_load.real, 1), "MW"
                print " - Change due to RES/re-dispatch change:", \
                      round(post_res_system_load.real - pre_res_system_load.real, 1), "MW"

                ## Intermediate load check
                err, post_res_system_losses = psspy.systot('LOSS')
                print "\nPost-RES change check on system losses:", round(post_res_system_losses.real, 1), "MW"
                print " - Change due to RES/re-dispatch change:", \
                      round(post_res_system_losses.real - pre_res_system_losses.real, 1), "MW"
                
                ## Intermediate Turlough Hill check
                post_res_th_mw = 0.0
                for th_unit in range(1, 5):
                    err, temp = psspy.macdat(int(str(5207) + str(th_unit)), str(th_unit), "P")
                    post_res_th_mw += temp
                print "\nPost-RES change check on Turlough Hill:", round(post_res_th_mw, 1), "MW"
                print " - Change due to RES/re-dispatch change:", round(post_res_th_mw - pre_res_th_mw, 1), "MW"
                
                
            ## Carry out a solution to guage how the case is
            if run_n_minus_one_analysis:

                err = psspy.rawd_2(0,1,[1,1,1,0,0,0,0],0, filelocation + \
                                   "\\Simulation " + time_stamp + "\\Debug\\pre-solution_file.raw")

                if enhance_voltage_profile:
                    for solution_tries in range(1, 4):
                        fix_mvar_limits()
                        psspy.fdns([0,0,0,0,1,0,0,0])

                mis = general_model_solution()
                if mis > system_mismatch_target:
                    print "\nSolution is NOT great! Mismatch:", round(mis, 3), "MVA"
                    continue

                ## Final load check
                err, final_system_load = psspy.systot('LOAD')
                print "\nFinal check on system load:", round(final_system_load.real, 1), "MW"
                print " -> Change in system load:", round(final_system_load.real - initial_system_load.real, 1), "MW"

                ## Final load check
                err, final_losses = psspy.systot('LOSS')
                print "\nFinal system losses:", round(final_losses.real, 1), "MW"
                print " -> Change in system losses:", round(final_losses.real - initial_losses.real, 1), "MW"

                ## Final Turlough Hill check
                final_th_mw = 0.0
                for th_unit in range(1, 5):
                    err, temp = psspy.macdat(int(str(5207) + str(th_unit)), str(th_unit), "P")
                    final_th_mw += temp
                print "\nFinal check on Turlough Hill:", round(final_th_mw, 1), "MW"
                print " -> Change:", round(abs(final_th_mw - initial_th_mw), 1), "MW"

                ## Re-set swing bus to close 75 MW - as per KC assumption
                th_ideal_output = 75.0
                print "\nEnsuring Turlough Hill's output is close to c.", th_ideal_output, "MW"                 
                updated_th_output = final_th_mw - th_ideal_output
                if option_to_set_res_to_max: redispatch_remainder = execute_redispatch(merit_order, updated_th_output)
                if "sp" in each_raw_file.lower():
                    if option_to_set_res_to_min: redispatch_remainder = execute_redispatch(merit_order, updated_th_output)
                if "wp" in each_raw_file.lower():
                    zones_to_increase = [12]  # KC - Area k is zone 12

                    ## When redispatching for a zero RES situation, firstly assume that all interconnectors are on full

                    err, generator_buses = psspy.amachint(-1, 4, 'NUMBER')
                    err, generator_ids = psspy.amachchar(-1, 4, 'ID')
                    err, generator_status = psspy.amachint(-1, 4, 'STATUS')
                    err, generator_types = psspy.amachint(-1, 4, 'OWN1')
                    err, generator_pgen = psspy.amachreal(-1, 4, 'PGEN')
                    err, generator_pmax = psspy.amachreal(-1, 4, 'PMAX')
                    err, generator_vintage = psspy.amachint(-1, 4, 'OWN2')

                    for gen_bus, gen_id, gen_pgen, gen_type, gen_status, gen_pmax, gen_vintage in \
                            zip(generator_buses[0], generator_ids[0], generator_pgen[0], \
                                generator_types[0], generator_status[0], generator_pmax[0], generator_vintage[0]):

                        err, gen_bus_zone = psspy.busint(gen_bus, 'ZONE')  ## Identify the bus zone

                        if gen_type in res_categories and gen_bus_zone in zones_to_increase and gen_vintage != 883:

                            err, gen_name = psspy.notona(gen_bus)

                            ## Not switching off machines - just setting active power to 0.0 MW
                            if debug: print chr(27), "\nRES | Zone:", gen_bus_zone, "| Details:", gen_name, gen_bus, gen_id, \
                                    "| Re-dispatching from", round(gen_pgen, 1), "MW to", round(gen_pmax*0.4, 1), "MW"
                            err = psspy.machine_chng_2(gen_bus, gen_id,[1],[gen_pmax])

                mis = general_model_solution()
                if mis > system_mismatch_target:
                    print "\nSolution is NOT great! Mismatch:", round(mis, 3), "MVA"
                    continue

                ## Get the final-final Turlough Hill output
                final_th_mw = 0.0
                for th_unit in range(1, 5):
                    err, temp = psspy.macdat(int(str(5207) + str(th_unit)), str(th_unit), "P")
                    final_th_mw += temp
                print "\nFinal final (!) check on Turlough Hill:", round(final_th_mw, 1), "MW"

            if add_reactive_compensation_to_model:
                for k, v in add_machines_dict.items():
                    if 'statcom' in k.lower():
                        print "\n" + k + " output for intact network:", 
                        err, statcom_output = psspy.macdat(int(str(v[0]) + "7"), str(v[1]), 'Q')
                        print round(statcom_output, 1), "Mvar"
                    else:
                        statcom_output = "N/A"
            else:
                statcom_output = "N/A"            
            
            ## To avoid clutter, save the cases in a simulation folder
            if not os.path.isdir("Simulation " + time_stamp + "\\Cases"): os.makedirs("Simulation " + time_stamp + "\\Cases")

            ## Save the updated *.raw file - maybe overkill to include this?
            err = psspy.rawd_2(0,1,[1,1,1,0,0,0,0],0, filelocation + "\\Simulation " + \
                               time_stamp + "\\Cases\\" + each_raw_file[:-4] + \
                               "-MOBU" + circuit_tag + station_tag + load_tag + generation_tag + ".raw")
            if err == 0:
                print "\nSuccessfully saving the updated *.raw file"
            else:
                print "\n***** Error saving the updated *.raw file! *****"
            
            ## Save the updated *.sav file
            if run_n_minus_one_analysis:
                
                err = psspy.save(filelocation + "\\Simulation " + time_stamp + "\\Cases\\" + each_raw_file[:-4] + \
                                 "-MOBU" + circuit_tag + station_tag + load_tag + generation_tag)
                if err == 0:
                    print "\nSuccessfully saving the updated *.sav file"
                else:
                    print "\n***** Error saving the updated *.sav file! *****"

                ## Run an N-1 analysis on the planning case
                nc_list = run_n_minus_one(each_raw_file)

                ## Scrape data from the *.dat file for a main Excel output
                violations_file = open(filelocation + "\\Simulation " +  time_stamp + "\\Violations\\Violations_" + \
                                       each_raw_file[:-4] + "_" + str(int(connection_increment)) + "MW.dat", 'r')

                ## Note: ignore the Dunstown - Turlough Hill circuit            
                while 1:
                    violations_line = violations_file.readline()
                    if "Flow Violations" in violations_line:
                        violations_line = violations_file.readline()                    
                        while 1:
                            violations_line = violations_file.readline()

                            if len(violations_line) == 1:                        
                                break

                            overloaded_circuit = string.rstrip(string.lstrip(violations_line[:55]))          
                            contingency        = get_contingency_name(string.rstrip(string.lstrip(violations_line[121:150])))                        
                            rating             = string.rstrip(string.lstrip(violations_line[55:65]))
                            overload_pc        = string.rstrip(string.lstrip(violations_line[105:115]))

                            if overloaded_circuit not in ratings_dict:
                                ratings_dict[overloaded_circuit] = rating

                            ## Store data for plotting
                            if overloaded_circuit not in plot_circuit_loadings_dict[add_machines_dict.keys()[0]].keys():
                                plot_circuit_loadings_dict[add_machines_dict.keys()[0]][overloaded_circuit] = {each_raw_file: {connection_increment: overload_pc}}
                            else:
                                if each_raw_file not in plot_circuit_loadings_dict[add_machines_dict.keys()[0]][overloaded_circuit].keys():
                                    plot_circuit_loadings_dict[add_machines_dict.keys()[0]][overloaded_circuit][each_raw_file] = {connection_increment: overload_pc}
                                else:
                                    if connection_increment not in plot_circuit_loadings_dict[add_machines_dict.keys()[0]][overloaded_circuit][each_raw_file].keys():
                                        plot_circuit_loadings_dict[add_machines_dict.keys()[0]][overloaded_circuit][each_raw_file][connection_increment] = overload_pc
                                    else:
                                        plot_circuit_loadings_dict[add_machines_dict.keys()[0]][overloaded_circuit].update({each_raw_file: {connection_increment: overload_pc}})

                            ## Report on the change in demand - particularly for a load connection
                            if add_loads_to_model:
                                change_in_system_load = round(final_system_load.real - initial_system_load.real - connection_increment, 1)
                            else:
                                change_in_system_load = round(final_system_load.real - initial_system_load.real, 1)
                            
                            write_out_this_data = [each_raw_file, connection_increment, statcom_output, \
                                                   overloaded_circuit, contingency, rating, overload_pc, \
                                                   round(final_th_mw, 1), round(final_losses.real, 1), \
                                                   change_in_system_load, round(mis, 3), pst_angle_for_n, pst_angle_for_n_1]
                            col = 1
                            for wotd in write_out_this_data:
                                ws_2.Cells(row, col).Value = wotd
                                col += 1
                            row += 1

                        if len(violations_line) == 1:
                            break
                
                ## If any, write out non-converged contingency data
                col = 1
                for each_nc in nc_list:
                    ws_2.Cells(row, col).Value = each_raw_file
                    ws_2.Cells(row, col + 1).Value = connection_increment
                    ws_2.Cells(row, col + 2).Value = statcom_output
                    ws_2.Cells(row, col + 3).Value = "*** Non-converged contingency! ***"
                    ws_2.Cells(row, col + 4).Value = get_contingency_name(each_nc[0])
                    ws_2.Cells(row, col + 5).Value = each_nc[2]
                    ws_2.Cells(row, col + 6).Value = each_nc[1]
                    ws_2.Cells(row, col + 7).Value = round(final_th_mw, 1)
                    ws_2.Cells(row, col + 8).Value = round(final_losses.real, 1)
                    ws_2.Cells(row, col + 9).Value = change_in_system_load
                    ws_2.Cells(row, col + 10).Value = round(mis, 3)
                    ws_2.Cells(row, col + 11).Value = pst_angle_for_n
                    ws_2.Cells(row, col + 12).Value = pst_angle_for_n_1
                    row += 1
                
        if not add_loads_to_model and not add_machines_to_model:
            break
        else:
            print "\nFinished incrementing to", connection_increment, "MW"
            connection_increment += connection_step_size
        
    ## if not debug: os.remove(filelocation + "\\Debug\\pre-solution_file.raw")
    check_file.close()

    print "\nA friendly reminder of your case assumptions:"
    print "============================================"
    check_these_final_files = glob.glob(filelocation + \
                                        "\\Simulation " + time_stamp + "\\Cases\\*-0MW.raw")
    for ctff in check_these_final_files:

        raw_file_err = psspy.readrawversion(0, str(psse_major_version), ctff)
        if raw_file_err != 0:
            print"\nError reading the *.raw file:", ctff 
            quit()
        
        err, generator_buses = psspy.amachint(-1, 4, 'NUMBER')    
        err, generator_status = psspy.amachint(-1, 4, 'STATUS')
        err, generator_types = psspy.amachint(-1, 4, 'OWN1')
        err, generator_ids = psspy.amachchar(-1, 4, 'ID')
        err, generator_pmax = psspy.amachreal(-1, 4, 'PMAX')    
        err, generator_pmin = psspy.amachreal(-1, 4, 'PMIN')    
        err, generator_pgen = psspy.amachreal(-1, 4, 'PGEN')

        onshore_wind_check = 0.0
        for a, b in  zip(generator_types[0], generator_pmax[0]):
            if a in [17, 18, 19, 20, 21, 22]: onshore_wind_check += b

        solar_pv_check = 0.0
        for a, b in  zip(generator_types[0], generator_pmax[0]):
            if a in [23]: solar_pv_check += b

        offshore_wind_check = 0.0
        for a, b in  zip(generator_types[0], generator_pmax[0]):
            if a in [16]: offshore_wind_check += b
                
        print "\n -> " + ctff
        print "      - Onshore wind generation:", round(onshore_wind_check, 1), "MW"
        print "      - Offshore wind generation:", round(offshore_wind_check, 1), "MW"  
        print "      - Solar PV generation:", round(solar_pv_check, 1), "MW"

        err, ld_ids = psspy.aloadchar(-1, 4, 'ID')
        err, ld_status = psspy.aloadint(-1, 4, 'STATUS')
        err, ld_mw = psspy.aloadcplx(-1, 4, 'MVAACT')
        dc_load_check = 0.0
        for a, b, c, in zip(ld_ids[0], ld_status[0], ld_mw[0]):
            if a == "DC" and b == 1:
                dc_load_check += c.real
        print "      - Data centre load:", round(dc_load_check, 1), "MW"
    
    print "\n  *** ANALYSIS IS COMPLETE! ***\n"
    
    psspy.progress_output(1,"",[0,0])

    ## Add an auto-filter on results file
    if run_n_minus_one_analysis:
            
        ws_2.Range('A1', 'M1').AutoFilter(1)

        ## Auto-fit formatting
        xls_2.ActiveWorkbook.ActiveSheet.Columns.AutoFit()
        xls_2.ActiveWorkbook.ActiveSheet.Rows.AutoFit()

        ## Freeze panes formatting
        '''        
        xls_2.ActiveWorkbook.Windows(1).SplitColumn = 1     
        xls_2.ActiveWorkbook.Windows(1).SplitRow = 1
        xls_2.ActiveWorkbook.Windows(1).FreezePanes = True
        '''
        
        ## Include a time stamp on the results file
        xls_2.ActiveWorkbook.SaveAs(filelocation + "\\N-1_Results_Summary_" + time_stamp + ".xlsx")
        xls_2.Quit()

    ####################################################################################
    ##                               END OF MAIN SCRIPT                               ##
    ####################################################################################


    ## Carry out some plots of each generators before we close
    ## Note: https://pythonbasics.org/matplotlib-bar-chart/
    import re

    try:
        import matplotlib.pyplot as plt
    except:
        print "\nMatplotlib was not detected - therefore terminating script..."
        import sys
        sys.exit()

    import collections

    ## To avoid clutter, save the cases in a seperate folder
    if not os.path.isdir("Simulation " + time_stamp + "\\Plots"):
        os.makedirs("Simulation " + time_stamp + "\\Plots")

    overloading_threshold = 110.0 ## Indicate this on plots

    for k0, v0 in plot_circuit_loadings_dict.items():

        print "\nConnection:", k0 

        for k1, v1 in v0.items():
            
            ## Get base voltages of overloaded circuits
            
            ## Ignore loadings on the LV or MV grid
            if ' 10.0' in k1 or ' 10.5' in k1 or \
               ' 20.0' in k1 or ' 38.0' in k1:
                continue

            print "\n - Plot for:", k1
            
            ## Make new plot
            plt.subplots()
            plt.title("Connection location: " + k0 + "\nOverload: " + k1)

            ## "\nSummer rating: " + str(ratings_dict[k1]) + " MVA | Winter rating: TBC", \

            ## Get the maximum generation level
            for k, v in add_machines_dict.items():
                use_this_x_axis = v[2]
                break
           
            ## Loop through the results of the various cases
            for k2, v2 in v1.items():

                ## Case-specific data
                if 'sp' in k2.lower():
                    case_colour = 'red'
                    case_marker = 'o'
                elif 'sv' in k2.lower() or 'snv' in k2.lower():
                    case_colour = 'green'
                    case_marker = '^'
                elif 'wp' in k2.lower():
                    case_colour = 'blue'
                    case_marker = "s"

                ## Add a line that defines sensitivity
                ## Note: only if there is an increase in loading for at least two data points
                if len(v2) > 1:

                    ## Guage if the overload is increasing
                    loading_is_increasing = False
                    connection_iterations = sorted(v2.keys())
                    print "Connection iterations:", connection_iterations
                    if v2[connection_iterations[0]] < v2[connection_iterations[1]]:
                        loading_is_increasing = True

                    ## Define sensitivity threshold - only if loading is increading
                    if loading_is_increasing:                    
                        sensitivity_threshold = 5.0 ## %
                        if generation_increment != 100.0:                        
                            sensitivity_threshold = sensitivity_threshold * generation_increment / 100.0
                        sml_list = []
                        sml_list = [float(sorted(v2.values())[0]) * (sensitivity_threshold + 100.0) / 100.0, \
                                    float(sorted(v2.values())[-2]) * (sensitivity_threshold + 100.0) / 100.0]
                        plt.plot([sorted(v2.keys())[1], sorted(v2.keys())[-1]], sml_list, color = case_colour)

                ## Check if we need to plot - i.e. any values > 110%
                '''
                skip_plot = True
                for each_plot_value in v2:
                    if each_plot_value > overloading_threshold:
                        skip_plot = False
                        print "-> Skipping this one!"
                        break
                if skip_plot: continue
                '''

                ## Identify x & y coordinates
                plt.scatter(v2.keys(), v2.values(), s = 60.0, color = case_colour, alpha = 0.75, \
                            marker = case_marker, label = k2[:6])
    
            ## Plot axis data
            plt.xlabel('Connection size [MW]')
            plt.ylabel('Loading [% of MVA rating]')

            plt.xlim([0.0, use_this_x_axis + generation_increment])
            plt.ylim([50.0, 260.0])       

            ## Plot line to indicate 110% loading
            plt.axhline(y = 110.0, color = 'purple', linestyle = '--', linewidth = 2, label = "N-1 Limit")

            ## Add a legend (& define font size)
            plt.legend(loc = 3, prop = {'size': 12})
              
            ## Save the plot
            plt.savefig(filelocation + "\\Simulation " + time_stamp + "\\Plots\\" + k1 + ".png")

    ## Radar plot of everything - https://stackoverflow.com/questions/42886076/matplotlib-radar-chart-axis-labels


## Manage the study type
## ---------------------
def update_study_type():

    global st

    new_study_type = st.get()          ## Take new user selection    
    st.set(new_study_type)             ## Update the value
    print ""
    print chr(17) + " The study type has been updated to", new_study_type
    study_type = new_study_type


## Build the MOBU graphic user interface (GUI)
## ==========================================
def run_mobu_gui():

    global root
    from Tkinter import *

    global study_type

    mobu_name = "MOBU"
    mobu_version = 2
    
    root = Tk()
    
    # The next option specifies a title to the root or container which is displayed on top of the window.
    root.title(mobu_name + '  |  version ' + str(mobu_version) + '  |  jeff kelliher')
    root.visible = True

    ## Set the root window's height, width & x,y position
    ## x & y are the coordinates of the upper left corner
    wdth = 500 ## Width of main GUI frame
    hght = 500 ## Height of main GUI fraome
    x = 600
    y = 100
    ## Use width, height, x_offset & y_offset (no spaces!)
    root.geometry("%dx%d+%d+%d" % (wdth, hght, x, y))
    
    ## Lock application size...
    root.resizable(0, 0) #or root.resizable(width=FALSE, height=FALSE)
    ## Can also use these...
    ## root.minsize(min_x, min_y)
    ## root.maxsize(max_x, max_y)

    mobu_colour = "purple"   ## 'light sky blue' - used in first post-EirGrid version, i.e. TNEI 
    title = Label(root, text = mobu_name, fg = mobu_colour, font = ('Helvetica', 85))
    title.place(x = 10, y = 15) # Main title

    x_move = 0
    y_move = 0
 
    sim_optns_lvl = 200 ## Make number smaller to move GUI items upwards
    run_options = LabelFrame(root, text = "Feasibility Study Options", height = 300, width = 300)
    run_options.place(x = 10, y = 150)
    
    ## Define study type - either generation or load feasibility connection
    study_type = "Generation"
    st_l = Label(text = 'Study type')
    st_l.place(x = 20, y = 200) 
    st = StringVar()
    st.set(study_type)
    
    import ttk
    st_cb = ttk.Combobox(root, textvariable = st, state = NORMAL, width = 25) ## Drop-down combo box
    st_cb['values'] = ('Generation', 'Demand')
    st_cb.place(x = 120, y = 200)
    st_cb.bind(sequence = '<<ComboboxSelected>>', func = update_study_type)
    ##st_tooltip = ToolTip(mon_cb, text = """Choose either generation or demand feasibility study""")    

    ## Debug tickbox
    dg_l = Label(text = 'Debug')
    dg_l.place(x = 20, y = 250) 
    dg = StringVar()
    dg.set(study_type)

    ## Debug tickbox
    inc_l = Label(text = 'Increment (MW)')
    inc_l.place(x = 20, y = 300) 
    inc = StringVar()
    inc.set(study_type)


    run_mobu()

## run_mobu_gui()

run_mobu()


    
