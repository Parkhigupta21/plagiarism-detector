import difflib


def highlight_similarity(text1, text2):

    matcher = difflib.SequenceMatcher(
        None,
        text1,
        text2
    )

    result = []

    for opcode in matcher.get_opcodes():

        tag, i1, i2, j1, j2 = opcode

        if tag == 'equal':

            result.append(

                f"<span style='background:#fca5a5'>"

                f"{text1[i1:i2]}"

                f"</span>"
            )

        else:

            result.append(
                text1[i1:i2]
            )

    return ''.join(result)