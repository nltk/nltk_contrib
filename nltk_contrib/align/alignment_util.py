

# Utility Functions

def readlines(filename):  
    """ 
    Return an array of strings, one string for each line of the file
    set len_ptr to the number of lines in the file.
    
    @type filename: C{string}
    @param filename: 
        
    @return: lines
    @rtype: C{list}  
    
    @return: len_ptr
    @rtype: C{int}  
    
    """
    lines = []
    
    input_file = file(filename, "r")
    substrings = []
    file_text = input_file.read()
    
    raw_lines = file_text.split('\n')
    lines = [line for line in raw_lines if not(line.strip() == '')]
                
    len_ptr = len(lines)
    
    return (lines, len_ptr)
    
def get_test_values(alignments):
    """ 
    
    @type alignments: C{dict}
    @param alignments: 
        
    @return: 
    @rtype: C{list}    
    
    """
    test_values = []
    for hard_regions_index in alignments.keys():
        soft_regions_list = []
        for soft_regions_index in alignments[hard_regions_index].keys():
            soft_regions_list.extend(alignments[hard_regions_index][soft_regions_index].alignment_mappings) 
        soft_regions_list.reverse()
        test_values.extend(soft_regions_list)
        
    return test_values
    
def get_reference_values(filename):
    """ 
    
    @type filename: C{string}
    @param filename: 
        
    @return: 
    @rtype: C{list}    
    
    """
    
    input_file = file(filename, "r")
    reference_values = []
    
    raw_lines = input_file.read().split('\n')
    lines = [line for line in raw_lines if not(line.strip() == '')]
    
    for line in lines:                
        line_parts = line.split(',')        
        reference_values.append((int(line_parts[0]),int(line_parts[1]),int(line_parts[2])))
    
    return reference_values
    
    
