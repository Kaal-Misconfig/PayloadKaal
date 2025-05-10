#!/usr/bin/env python3

import argparse
import base64
import os
import random
import string
import struct
import sys
import zlib

class PayloadEncoder:
    
    @staticmethod
    def xor_encode(data, key):
        if isinstance(key, str):
            key = key.encode()
            
        result = bytearray()
        for i in range(len(data)):
            result.append(data[i] ^ key[i % len(key)])
        return bytes(result)
    
    @staticmethod
    def rol_encode(data, shift):
        result = bytearray()
        for b in data:
            result.append(((b << shift) | (b >> (8 - shift))) & 0xFF)
        return bytes(result)
    
    @staticmethod
    def custom_b64encode(data):
        custom_alphabet = 'ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba9876543210+/'
        standard = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        
        b64_data = base64.b64encode(data).decode()
        
        trans_table = str.maketrans(standard, custom_alphabet)
        return b64_data.translate(trans_table).encode()
    
    @staticmethod
    def custom_b64decode(data):
        """Decode custom Base64 data"""
        if isinstance(data, bytes):
            data = data.decode()
            
        custom_alphabet = 'ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba9876543210+/'
        standard = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        
        trans_table = str.maketrans(custom_alphabet, standard)
        standard_b64 = data.translate(trans_table)
        
        return base64.b64decode(standard_b64)
    
    @staticmethod
    def multi_encode(data, key):
        compressed = zlib.compress(data)
        
        xored = PayloadEncoder.xor_encode(compressed, key)
        
        rotated = PayloadEncoder.rol_encode(xored, 3)
        
        encoded = PayloadEncoder.custom_b64encode(rotated)
        
        return encoded
    
    @staticmethod
    def multi_decode(data, key):
        decoded = PayloadEncoder.custom_b64decode(data)
        
        derotated = bytearray()
        for b in decoded:
            derotated.append(((b >> 3) | (b << (8 - 3))) & 0xFF)
        
        dexored = PayloadEncoder.xor_encode(bytes(derotated), key)
        
        decompressed = zlib.decompress(dexored)
        
        return decompressed

class PayloadGenerator:
    
    def __init__(self):
        self.windows_template = r'''
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

shellcode = b"{shellcode}"

{decode_logic}

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
'''

        self.linux_template = r'''
#!/usr/bin/env python3
import ctypes
import sys
import os
import mmap

shellcode = b"{shellcode}"

{decode_logic}

print("[*] Allocating memory...")
size = len(decoded_shellcode)
mem = mmap.mmap(
    -1,  # Anonymous mapping
    size,
    prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC,
    flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS
)

print("[*] Copying shellcode to memory...")
mem.write(decoded_shellcode)

print("[*] This is where execution would happen in a real tool")
print("[*] No actual execution is implemented")
print("[*] Demo complete")
'''

        self.demo_shellcode = (
            b"\x31\xc0\x40\xb7\x01\x31\xdb\xcd\x80"  
        )
    
    def generate_key(self, length=16):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
    
    def generate_payload(self, output_file, platform="linux", encoding="multi"):
        print(f"[+] Generating payload for {platform} with {encoding} encoding...")
        
        key = self.generate_key()
        
        shellcode = self.demo_shellcode
        
        if encoding == "xor":
            encoded_shellcode = PayloadEncoder.xor_encode(shellcode, key)
            decode_logic = f'''
key = "{key}"
key_bytes = key.encode() if isinstance(key, str) else key
decoded_shellcode = bytearray()
encoded_data = shellcode
for i in range(len(encoded_data)):
    decoded_shellcode.append(encoded_data[i] ^ key_bytes[i % len(key_bytes)])
decoded_shellcode = bytes(decoded_shellcode)
'''
        elif encoding == "b64custom":
            encoded_shellcode = PayloadEncoder.custom_b64encode(shellcode)
            decode_logic = '''
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
'''
        else:  
            encoded_shellcode = PayloadEncoder.multi_encode(shellcode, key)
            decode_logic = f'''
import zlib

key = "{key}"
key_bytes = key.encode() if isinstance(key, str) else key

def custom_b64decode(data):
    """Decode custom Base64 data"""
    if isinstance(data, bytes):
        data = data.decode()
        
    custom_alphabet = 'ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba9876543210+/'
    standard = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    
    trans_table = str.maketrans(custom_alphabet, standard)
    standard_b64 = data.translate(trans_table)
    
    import base64
    return base64.b64decode(standard_b64)

decoded = custom_b64decode(shellcode)

derotated = bytearray()
for b in decoded:
    derotated.append(((b >> 3) | (b << (8 - 3))) & 0xFF)

dexored = bytearray()
for i in range(len(derotated)):
    dexored.append(derotated[i] ^ key_bytes[i % len(key_bytes)])

decoded_shellcode = zlib.decompress(bytes(dexored))
'''
        
        shellcode_str = ", ".join([f"0x{b:02x}" for b in encoded_shellcode])
        shellcode_bytes = f"bytes([{shellcode_str}])"
        
        if platform == "windows":
            template = self.windows_template
        else:
            template = self.linux_template
        
        payload_code = template.format(
            shellcode=shellcode_bytes,
            decode_logic=decode_logic
        )
        
        with open(output_file, "w") as f:
            f.write(payload_code)
        
        if platform == "linux":
            os.chmod(output_file, 0o755)
        
        print(f"[+] Generated payload: {output_file}")
        print(f"[+] Encoding: {encoding}")
        print(f"[+] Key: {key}")

def compile_to_exe(input_file, output_name):
    try:
        import PyInstaller
    except ImportError:
        print("[!] PyInstaller is not installed. Installing now...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    import subprocess
    print(f"[*] Compiling {input_file} to executable...")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        f"--name={output_name}",
        input_file
    ]
    
    try:
        subprocess.check_call(cmd)
        exe_path = os.path.join("dist", output_name)
        if os.path.exists(exe_path):
            print(f"[+] Successfully created executable: {exe_path}")
            return True
        else:
            print(f"[!] Failed to create executable at expected path: {exe_path}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"[!] Error during compilation: {e}")
        return False

def main():
    print("""
    
███████   ███████   ██     ██  ██         ██████   ███████ ██████████
 ██   ██   ██   ██    ██   ██   ██        ██    ██  ██   ██   ██    ██
 ███████   ███████      ███     ██        ██    ██  ███████   ██    ██
 ██        ██   ██      ███     ██        ██    ██  ██   ██   ██    ██
 ██        ██   ██      ███     ████████   ██████   ██   ██ ██████████
   
    """)
    
    parser = argparse.ArgumentParser(description="Simple Payload Generator - Educational Tool")
    parser.add_argument("-o", "--output", required=True, help="Output filename (.py or .exe)")
    parser.add_argument("-p", "--platform", choices=["windows", "linux"], default="linux", 
                        help="Target platform (windows or linux)")
    parser.add_argument("-e", "--encoding", choices=["xor", "b64custom", "multi"], default="multi",
                        help="Encoding method to use")
    parser.add_argument("-x", "--exe", action="store_true", help="Compile to executable (requires PyInstaller)")
    parser.add_argument("--exe-name", help="Name for the executable (without extension)")
    
    args = parser.parse_args()
    
    generator = PayloadGenerator()
    
    if args.output.endswith('.py'):
        output_py = args.output
    else:
        output_py = args.output + '.py'
    
    generator.generate_payload(output_py, args.platform, args.encoding)
    
    if args.exe:
        exe_name = args.exe_name or os.path.splitext(os.path.basename(args.output))[0]
        if compile_to_exe(output_py, exe_name):
            print(f"[+] Executable created: dist/{exe_name}")
        else:
            print("[!] Failed to create executable")
    
    print("\n[+] Done! For educational purposes only.")

if __name__ == "__main__":
    main()
