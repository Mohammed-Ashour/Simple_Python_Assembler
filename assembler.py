from grammer import LANG_DICT
from helpers import convert_to_hex, construct_output, out_file
import json
config = ""

#with open("config.json", "r") as f: config = json.load(f)
#print(config)
#mode = config["mode"]
colors = {
    "OKGREEN" : "\033[92m",
    "FAILRED" : "\033[91m",
    "END" : "\033[0m"
}

mem_ref_inst = LANG_DICT["MEM_REF"].keys()
reg_inst = LANG_DICT["REG_INST"].keys()
io_inst = LANG_DICT["IO"].keys()
LC = 0
locs = {}
final_code = ""
num_systems = ["DEC", "BIN", "HEX"]
errors = 0

def read_input(inp_file_location):
    with open(inp_file_location, 'r') as f:
        data = f.read().splitlines()
        return data



def make_memory(loc_line, index):
    loc_name = loc_line.split(",")[0]
    if len(loc_name) != 3 or loc_name[0].isdigit():
        error_handler(index, "Invalid Naming")
        return False
    value = convert_to_hex(loc_line.split(",")[1])
    return {loc_name : {"value": value, "index": str(index) }}

def read_from_memory(pesudo):
    if pesudo in locs.keys():
        return locs[pesudo]["value"]
    else: 
        return False


    
def memory_ref_interpreter(inst_list):
    
    line = inst_list
    inst = line[0]
    m_inst = ""
    if len(line) > 3:
        #print("heeeey" + inst_list)
        inst = line[1]
        m_inst =  LANG_DICT["MEM_REF"][inst]["1"] #TODO handle LOP (test2)

    else:
        m_inst = LANG_DICT["MEM_REF"][inst]["0"]
    m_inst = m_inst.replace("XXX", locs[line[1]]["index"])
    return m_inst

def memory_ref_validator(inst_list):
    inst_list_len = len(inst_list)
    if inst_list_len >= 2 and inst_list_len <= 3:
        #name validation

        if inst_list_len == 2:
            if inst_list[1] in locs.keys() or inst_list[1] in num_systems:
                return True
            else:
                return False
            #check if the other attr is number or stored psudo
        elif inst_list_len == 3:
            #check if the last item if it == I
            # check if the second attr is a number or stored psudo
            if inst_list[2] == "I" and (inst_list[1] in locs.keys() or inst_list[1] in num_systems):
                #print(inst_list[1])
                return True
            else:
                return False
    else : 
        return False
            #errorhandler(error_type="syntax", cur_index)

def error_handler(cur_index, msg):
    global errors
    print(colors["FAILRED"] + "[X]--> Error @ line ["+str(cur_index - LC + 2)+ "] " +msg + colors["END"])
    errors += 1

def reg_ref_interpreter(inst_list):
    inst = inst_list[0]
    return LANG_DICT["REG_INST"][inst]


def reg_ref_validator(inst_list):
    if len(inst_list) == 1: 
        return True
    else:
        return False
        
    
def io_ref_interpreter(inst_list):
    inst = inst_list[0]
    return LANG_DICT["IO"][inst]

def io_ref_validator(inst_list):
    if len(inst_list) == 1: 
        return True
    else:
        return False


def global_interpreter(inst_line, cur_index):
    global final_code
    line = ""
    #remove comments
    if "/" in inst_line : 
        inst_line = inst_line.split("/")[0].rstrip()
      

    if "," in inst_line:
        pesudo, line = inst_line.split(", ")[0], inst_line.split(", ")[1]
        inst_list = line.split(" ")
        inst = inst_list[0]
        if inst in mem_ref_inst:
            if memory_ref_validator(inst_list):
                final_code = construct_output(final_code, str(cur_index) + " " + memory_ref_interpreter(inst_list))
                #locs.update(make_memory(inst_line, cur_index))

            else:
                error_handler(cur_index, inst_line + "  >> Invalid MEM REF INST")
                exit
        elif inst in num_systems:
            #locs.update(make_memory(inst_line, cur_index))
            if read_from_memory(pesudo):
                final_code =  construct_output(final_code,str(cur_index) + " " + read_from_memory(pesudo) )
            else:
                error_handler(cur_index, inst_line + " Invalid MEM REF - Not Found!")
        elif inst in reg_inst:
            reg_ref_validator(inst_list)

    else :
        inst_list = inst_line.split(" ")
        inst = inst_list[0]
        if inst in mem_ref_inst:
            if memory_ref_validator(inst_list):
                final_code = construct_output(final_code, str(cur_index) + " " + memory_ref_interpreter(inst_list))
            else:
                error_handler(cur_index, inst_line)


        elif inst in reg_inst:
            if reg_ref_validator(inst_list):
                final_code = construct_output(final_code, str(cur_index) + " " + reg_ref_interpreter(inst_list))
            else:
                error_handler(cur_index, inst_line + " Invalid Reg REF INST")

        elif inst in io_inst:
            if io_ref_validator(inst_list):
                final_code = construct_output(final_code, str(cur_index) + " " + io_ref_interpreter(inst_list))
            else:
                error_handler(cur_index, inst_line + "Invalid IO INST")

        else:
            error_handler(cur_index, inst_line)
            


def simple_converter(data):
    #remember to upper every line
    global LC, final_code
    cur_index = 0
    for i in data:
        i = i.upper()
        cur_index += 1
        if "ORG" in i: 
            LC = int(i.split(" ")[1])
            cur_index = LC - 1  # as that location is the next instruction location
        elif "," in i:
            m = make_memory(i,cur_index)
            if m != False:
                locs.update(m)
            else:
                error_handler(cur_index, i + " Invalid Naming")
    
    for i in data:
        i = i.upper()
        cur_index += 1
        inst = i.split(" ")[0]
        if inst == "ORG":
            cur_index = LC - 1
        elif inst == "END":
            break
        else:
            global_interpreter(i, cur_index)

        # if  inst in mem_ref_inst:
        #     print(memory_ref_interpreter(i))
        #     final_code = construct_output(final_code, str(cur_index) + " " + memory_ref_interpreter(i))
        # elif inst in reg_inst:
        #     print(LANG_DICT["REG_INST"][inst])
        #     final_code = construct_output(final_code, str(cur_index) + " " + LANG_DICT["REG_INST"][inst])
        # elif inst in io_inst:
        #     final_code = construct_output(final_code, str(cur_index) + " " + LANG_DICT["IO"][inst])
        #     print(LANG_DICT["IO"][inst])
        # else:
        #     if inst == "ORG":
        #         LC = int(i.split(" ")[1])
        #         cur_index = LC - 1
        #     elif inst == "END":
        #         break
        #     elif inst in num_systems:
        #         print(i)
        #     else:
        #         final_code =  construct_output(final_code,str(cur_index) + " " + read_from_memory(i.split(",")[0]) )



color = colors["OKGREEN"]

x = read_input("test.inp")
simple_converter(x)
if errors > 0 :
    color = colors["FAILRED"]
    print(color + "Couldn't convert the file, fix the Errors first!!"  + colors["END"] )
else:
    out_file(final_code, "out.out")
    print(color + "File converted successfully, check out.out!!"  + colors["END"] )

    
print(color + "Program ended with " + str(errors) + " Errors" + colors["END"] )
#print(locs)

 
