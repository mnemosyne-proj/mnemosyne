
# Still needed if we work with css?

# This was a hack anyway...

##############################################################################
#
# set_non_latin_font_size
#
#   Useful to increase size of non-latin unicode characters.
#
##############################################################################

def set_non_latin_font_size(old_string, font_size):

    def in_latin_plane(ucode):
        
        # Basic Latin (US-ASCII): {U+0000..U+007F}
        # Latin-1 (ISO-8859-1): {U+0080..U+00FF}
        # Latin Extended: {U+0100..U+024F}
        # IPA Extensions: {U+0250..U+02AF}\
        # Spacing Modifier Letters: {U+02B0..U+02FF}
        # Combining Diacritical Marks: {U+0300..U+036F}  
        # Greek: {U+0370..U+03FF}
        # Cyrillic: {U+0400..U+04FF}
        # Latin Extended Additional
        # Greek Extended
        
        plane = ((0x0000,0x04FF), (0x1E00,0x1EFF), (0x1F00,0x1FFF))
        for i in plane:
            if ucode > i[0] and ucode < i[1]:
                return True
        return False

    if old_string == "":
        return old_string
    
    new_string = ""
    in_tag = False
    in_protect = 0
    in_unicode_substring = False
    
    for i in range(len(old_string)):
        if not in_latin_plane(ord(old_string[i])) and not in_protect:

            # Don't substitute within XML tags, or file names get messed up.
            
            if in_tag or in_unicode_substring == True:
                new_string += old_string[i]
            else:
                in_unicode_substring = True
                new_string += '<font style=\"font-size:' + str(font_size) +\
                              'pt\">' + old_string[i]
        else:
            
            # First check for tag start/end.
            
            if old_string[i] == '<':
                in_tag = True
            elif old_string[i] == '>':
                in_tag = False

            # Test for <protect> tags.

            if old_string[i:].startswith('<protect>'):
                in_protect += 1
            elif old_string[i:].startswith('</protect>'):
                in_protect = max(0, in_protect - 1)

            # Close tag.
               
            if in_unicode_substring == True:
                in_unicode_substring = False
                new_string += '</font>' + old_string[i]
            else:
                new_string += old_string[i]
                
    # Make sure to close the last tag.
              
    if not in_latin_plane(ord(old_string[-1])) and not in_protect:
        new_string += '</font>'

    # Now we can strip all the <protect> tags.

    new_string = new_string.replace('<protect>', '').replace('</protect>', '')
    
    return new_string

