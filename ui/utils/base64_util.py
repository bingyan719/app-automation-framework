import base64

SLASH_CHAR = '/'
UNI_CHAR = '_'
PLUS_CHAR = '+'
MINUS_SCORE = '-'


def encode(content):
    encodestr = base64.b64encode(content.encode('utf-8'))
    encode_content = str(encodestr, 'utf-8')
    if SLASH_CHAR in encode_content or PLUS_CHAR in encode_content:
        encode_content = encode_content.replace(SLASH_CHAR, UNI_CHAR).replace(PLUS_CHAR, MINUS_SCORE)
    return encode_content


def decode(content):
    if UNI_CHAR in content or MINUS_SCORE in content:
        content = content.replace(UNI_CHAR, SLASH_CHAR).replace(MINUS_SCORE, PLUS_CHAR)
    decodestr = base64.b64decode(content.encode('utf-8'))
    decode_content = str(decodestr, 'utf-8')
    return decode_content