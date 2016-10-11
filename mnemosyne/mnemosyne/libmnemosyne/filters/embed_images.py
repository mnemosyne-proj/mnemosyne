#
# embed_images.py <Peter.Bienstman@UGent.be>
#

import re, base64

from mnemosyne.libmnemosyne.filter import Filter

re_img = re.compile(r"""<img src=\"file:///(.+?)\"""", re.DOTALL | re.IGNORECASE)


class EmbedImages(Filter):
    
    """Embed images directly in html, to get around bugs involving permission
    issues with webcomponents.
    
    """
    
    def run(self, text, card, fact_key, **render_args):
        if not re_img.search(text):
            return text
        starts, replacements, ends = [], [], []
        for match in re_img.finditer(text): 
            starts.append(match.start(0))
            f = open(match.group(1), 'rb')
            encoded = str(base64.b64encode(f.read()), "ascii")
            replacements.append("""<img src="data:image;base64,%s" alt="%s" """ 
                    % (encoded, match.group(1)))
            ends.append(match.end(0))
        starts.append(len(text))
        new_text = text[:starts[0]]
        for i in range(len(replacements)):
            new_text += replacements[i] + text[ends[i]:starts[i+1]]
        return new_text
    
