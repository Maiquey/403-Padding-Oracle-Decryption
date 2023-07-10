import secrets
import subprocess
import time

def read_binary_file(file_path):
    with open(file_path, 'rb') as file:
        return bytearray(file.read())

def decryptBlock(ciphertext, N):
    # Decrypt Byte
    i = 0
    
    r = bytearray([secrets.randbits(8) for _ in range(15)] + [i])

    if N == 0:
        yN = ciphertext[-16:]
        yNm1 = ciphertext[-32:-16]
    else:
        yN = ciphertext[(-32*N):(-16*N)]
        yNm1 = ciphertext[(-48*N):(-32*N)]

    yNm1LastByte = yNm1[-1]

    decryptedYNArray = [0] * 16
    decryptedBytes = [0] * 16

    r_yN = r + yN
    f = open("crackfile", "wb")
    f.write(bytes(r_yN))
    f.close()

    while (subprocess.check_output(['python', 'oracle.py', 'crackfile'])[0] != 49):
        i += 1
        r[-1] = i
        r_yN = r + yN
        f = open("crackfile", "wb")
        f.write(bytes(r_yN))
        f.close()

    #0 to 14
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
        if (subprocess.check_output(['python', 'oracle.py', 'crackfile'])[0] == 48):
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

        while (subprocess.check_output(['python', 'oracle.py', 'crackfile'])[0] != 49):
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
    start_time = time.time()
    decrypted = []
    ciphertext = read_binary_file('ciphertext')
    numBlocks = len(ciphertext) / 16
    for x in range(0, int(numBlocks) - 1):
        decrypted = decryptBlock(ciphertext, x) + decrypted
    plaintext = ''.join([chr(i) for i in decrypted]).strip()
    print(plaintext)
    end_time = time.time()
    elapsed_time = end_time - start_time

    print("Elapsed time:", elapsed_time, "seconds")
    
decryptMessage()