import secrets
import subprocess

def read_binary_file(file_path):
    with open(file_path, 'rb') as file:
        return bytearray(file.read())

def decryptBlock(ciphertext, N):
    # Decrypt Byte
    i = 0
    
    r = bytearray([secrets.randbits(8) for byte in range(15)] + [i])

    if N == 0:
        yN = ciphertext[-16:]
        yNm1 = ciphertext[-32:-16]
    else:
        yN = ciphertext[(-16*(N+1)):(-16*N)]
        yNm1 = ciphertext[(-16*(N+2)):(-16*(N+1))]

    yNm1LastByte = yNm1[-1]

    decryptedYNArray = [0] * 16
    decryptedBytes = [0] * 16

    r_yN = r + yN
    f = open("crackfile", "wb")
    f.write(bytes(r_yN))
    f.close()

    while (subprocess.check_output(['python3', 'oracle.py', 'crackfile'])[0] != 49):
        i += 1
        r[-1] = i
        r_yN = r + yN
        f = open("crackfile", "wb")
        f.write(bytes(r_yN))
        f.close()

    #index 0 to 14
    #r1 to r15
    #replace r[k-1] with random byte
    allYes = True
    k = 1

    while (allYes and k <= 15):
        rTemp = r
        rTemp[k - 1] = secrets.randbits(8)
        test = rTemp + yN
        f = open("crackfile", "wb")
        f.write(bytes(test))
        f.close()
        if (subprocess.check_output(['python3', 'oracle.py', 'crackfile'])[0] == 48):
            allYes = False
        else:
            k += 1

    if allYes:
        decryptedYN = (i ^ 15)
    else:
        decryptedYN = (i ^ (k - 1))

    decryptedYNArray[15] = decryptedYN
    finalByteXN = (decryptedYN ^ yNm1[-1])
    decryptedBytes[15] = finalByteXN

    # Decrypt Block

    k = 15
    while (k >= 1):
        i = 0
        rTemp = r[:(k-1)] + bytearray([i])
        for x in range(k, 16):
            rTemp = rTemp + bytearray([decryptedYNArray[x] ^ (k-1)])

        r_yN = rTemp + yN
        f = open("crackfile", "wb")
        f.write(bytes(r_yN))
        f.close()

        while (subprocess.check_output(['python3', 'oracle.py', 'crackfile'])[0] != 49):
            i += 1
            rTemp[k-1] = i
            r_yN = rTemp + yN
            f = open("crackfile", "wb")
            f.write(bytes(r_yN))
            f.close()

        decryptedYN_k = i ^ (k-1)
        decryptedByte_k = decryptedYN_k ^ yNm1[k-1]

        decryptedYNArray[k-1] = decryptedYN_k
        decryptedBytes[k-1] = decryptedByte_k

        k -= 1

    return decryptedBytes

def decryptMessage():
    decrypted = []
    ciphertext = read_binary_file('ciphertext')

    numBlocks = len(ciphertext) / 16
    for x in range(0, int(numBlocks) - 1):
        decrypted = decryptBlock(ciphertext, x) + decrypted

    plaintext = ''.join([chr(byte) for byte in decrypted])
    while not plaintext.isprintable():
        plaintext = plaintext[:-1] #remove padding
    print(plaintext)

decryptMessage()