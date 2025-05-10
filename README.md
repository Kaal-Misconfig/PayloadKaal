<div align="center">
  <h1>💀 PayloadKaal 💀</h1>
  <p>
    <img src="file:///D:/Downloads%20Bin/payloadkaal_logo.svg">
  </p>
  <p><strong>Multi-Encoder Payload Generator & AV Evasion Framework</strong></p>
  
  <p>
    <a href="#features">Features</a> •
    <a href="#installation">Installation</a> •
    <a href="#usage">Usage</a> •
    <a href="#encoding-methods">Encoding Methods</a> •
    <a href="#examples">Examples</a> •
    <a href="#advanced-usage">Advanced Usage</a> •
    <a href="#disclaimer">Disclaimer</a>
  </p>
  
  <p>
    <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-blue" alt="Platform">
    <img src="https://img.shields.io/badge/Language-Python%203-yellow" alt="Language">
    <img src="https://img.shields.io/badge/Purpose-Educational-red" alt="Purpose">
  </p>
</div>

## 🔥 Overview

**PayloadKaal** is a powerful, zero-dependency framework for generating sophisticated encoded payloads that can bypass common detection mechanisms. Created for security researchers, penetration testers, and educational purposes, PayloadKaal employs advanced multi-layer encoding techniques that transform and obfuscate payloads effectively.

## ✨ Features

- **Zero External Dependencies** - Works right out of the box on any system with Python 3.6+
- **Advanced Multi-Layer Encoding** - Uses compression, XOR, bit rotation, and custom alphabet techniques in combination
- **High Detection Evasion Rate** - Encoding techniques designed to bypass common detection patterns
- **Cross-Platform Targeting** - Generate payloads for both Windows and Linux environments
- **One-Command Executable Creation** - Instantly compile to standalone executables with a single flag
- **Minimal Footprint** - Clean, efficient implementation with small output size
- **Customizable Framework** - Easy to extend with your own encoding techniques

## 🚀 Installation

PayloadKaal requires zero installation! Just download and run:

```bash
# Clone the repository
git clone https://github.com/kaal-misconfig/PayloadKaal.git

# Navigate to the directory
cd PayloadKaal

# Make the script executable
chmod +x payload_generator.py
```

**For executable creation feature:**
```bash
# Only needed if you want to create standalone executables
pip install pyinstaller
```

## 📋 Usage

```bash
./payload_generator.py -o [OUTPUT] -p [PLATFORM] -e [ENCODING] -x --exe-name [NAME]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `-o, --output` | Output filename (required) |
| `-p, --platform` | Target platform: `windows` or `linux` (default: `linux`) |
| `-e, --encoding` | Encoding method: `xor`, `b64custom`, or `multi` (default: `multi`) |
| `-x, --exe` | Compile to executable (requires PyInstaller) |
| `--exe-name` | Custom name for the executable (without extension) |

## 🔐 Encoding Methods

### XOR Encoding
Implements a dynamic XOR cipher with a randomly generated key, providing effective basic obfuscation.

```bash
./payload_generator.py -o payload.py -e xor
```

### Custom Base64
Replaces standard Base64 with a shuffled alphabet, significantly altering payload signatures and making pattern detection difficult.

```bash
./payload_generator.py -o payload.py -e b64custom
```

### Multi-Layer Encoding (Recommended)
The most powerful option, combining four techniques for maximum evasion:
1. **Compression** - Alters binary patterns while reducing size
2. **XOR Encoding** - Randomized key obfuscation layer
3. **Bit Rotation** - Shifts each byte's bits for deeper transformation
4. **Custom Base64** - Final encoding with modified alphabet

```bash
./payload_generator.py -o payload.py -e multi
```

## 📊 Examples

### Generate a Linux Payload
```bash
./payload_generator.py -o linux_payload.py -p linux -e multi
```

### Generate a Windows Payload
```bash
./payload_generator.py -o windows_payload.py -p windows -e xor
```

### Create a Ready-to-Deploy Executable
```bash
./payload_generator.py -o payload.py -p linux -e multi -x --exe-name kaal_payload
```

## 🧰 Advanced Usage

### The Encoding Pipeline

PayloadKaal's multi-layer encoding follows this sequence:

```
Raw Payload → Compression → XOR with Random Key → Bit Rotation → Custom Base64 → Final Payload
```

Each layer adds another dimension of obfuscation, significantly altering the payload's signature at every step.

### Extending PayloadKaal

The framework is built to be easily extensible:

- Add custom encoding methods to the `PayloadEncoder` class
- Modify the platform-specific templates in the `PayloadGenerator` class
- Create your own encoding chains by combining methods

For example, to add a new encoding method:

```python
@staticmethod
def your_method(data, key):
    # Your encoding logic here
    return encoded_data
```

## 🔍 How It Works

### Memory Allocation Techniques

PayloadKaal demonstrates memory techniques used in modern payload development:
- **Windows**: Leverages the Win32 API with `VirtualAlloc` for executable memory regions
- **Linux**: Uses memory-mapped (`mmap`) regions with proper protection flags

### Execution Flow

1. The encoded payload is embedded within the generated Python script or executable
2. At runtime, multiple decoding layers are applied in reverse order
3. Memory is allocated with proper permissions
4. The decoded payload is loaded into memory
5. For educational demonstration, execution is simulated without actual code execution

## 🎓 Educational Value

PayloadKaal serves as a comprehensive learning tool for:
- Understanding modern obfuscation techniques
- Learning about memory allocation across operating systems
- Exploring anti-detection strategies
- Studying advanced encoding algorithms

## ⚠️ Disclaimer

**PayloadKaal** is provided for **educational and research purposes only**. This tool demonstrates payload generation and encoding techniques that security professionals need to understand. The payloads generated are non-functional demonstrations that do not execute any actual malicious code.

The author do not condone nor support any malicious use of this tool. Users are responsible for complying with all applicable laws and regulations.

## 🤝 Contributing

Contributions are welcome! Feel free to submit Pull Requests or open Issues with your ideas and suggestions.

## 📞 Support

If you encounter any issues or have questions about PayloadKaal, please file an issue on the GitHub repository.
