import secrets
import subprocess

# 43 4D 50 54 20 34 30 33 
# 20 54 65 73 74 20 49 56 
# 35 13 3D 5C BD 4E 5F 1D 
# 65 CE E6 0C E2 BA C2 F2 
# EE 4C DB 6A 38 00 E8 68 
# EB 6A 34 E9 EE 0F 20 9E 

def read_binary_file(file_path):
    with open(file_path, 'rb') as file:
        return bytearray(file.read())

def xor(a, b):
    #input: two byearrays
    #output: bytearray of their xor
    if len(a) > len(b):
        temp = a
        a = b
        b = temp
    s = []
    for i in range(0, len(a)):
        s.append(a[i] ^ b[i])
    for i in range(len(a), len(b)):
        s.append(b[i])
    return s


# Decrypt Byte

i = 0
ciphertext = read_binary_file('ciphertext')
r = bytearray([secrets.randbits(8) for _ in range(15)] + [i])
yN = ciphertext[-16:]
yNm1 = ciphertext[-32:-16]
yNm1LastByte = yNm1[-1]

decryptedYNArray = [0] * 16
decryptedBytes = [0] * 16

r_yN = r + yN
f = open("crackfile", "wb")
f.write(bytes(r_yN))
f.close()

print([int(byte) for byte in r])
while (subprocess.check_output(['python', 'oracle.py', 'crackfile'])[0] != 49):
    i += 1
    r[-1] = i
    #print(i)
    r_yN = r + yN
    f = open("crackfile", "wb")
    f.write(bytes(r_yN))
    f.close()

print("hi")

#0 to 14
#r1 to r15
#replace r[k-1] with random byte
allYes = True
k = 1

while (allYes and k <= 15):
    print(k)
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

# if allYes:
#     decryptedYN = xor(bytes([i]), bytes([15]))
# else:
#     decryptedYN = xor(bytes([i]), bytes([k - 1]))

# finalByteXN = xor(bytes(decryptedYN), bytes([yNm1[-1]]))[0]
# print(finalByteXN)

if allYes:
    decryptedYN = (i ^ 15)
else:
    decryptedYN = (i ^ (k - 1))

decryptedYNArray[15] = decryptedYN
finalByteXN = (decryptedYN ^ yNm1[-1])
decryptedBytes[15] = finalByteXN
print(finalByteXN)

# Decrypt Block

k = 15
while (k >= 1):
    print([int(byte) for byte in r])
    i = 0
    rTemp = r[:(k-1)] + bytearray([i])
    for x in range(k, 16):
        rTemp = rTemp + bytearray([decryptedYNArray[x] ^ (k-1)])

    r_yN = rTemp + yN
    f = open("crackfile", "wb")
    f.write(bytes(r_yN))
    f.close()

    print([int(byte) for byte in r_yN])
    while (subprocess.check_output(['python', 'oracle.py', 'crackfile'])[0] != 49):
        i += 1
        rTemp[k-1] = i
        print(i)
        r_yN = rTemp + yN
        f = open("crackfile", "wb")
        f.write(bytes(r_yN))
        f.close()

    decryptedYN_k = i ^ (k-1)
    decryptedByte_k = decryptedYN_k ^ yNm1[k-1]

    decryptedYNArray[k-1] = decryptedYN_k
    decryptedBytes[k-1] = decryptedByte_k

    k -= 1

print(decryptedBytes)