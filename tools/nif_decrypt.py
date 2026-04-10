#!/usr/bin/env python3
"""Decrypt SMT:Imagine encrypted NIF files."""
import struct, zlib, sys, os

# Keys extracted from ImagineClient.exe v1.666
XOR_KEY1 = 0x3548F8DA
XOR_KEY2 = 0xA86D8CB5
NIF_MAGIC = 0x35305AFF

def decrypt_nif(data):
    """Decrypt an encrypted NIF file, returns decrypted bytes."""
    if len(data) < 12:
        return None

    magic = struct.unpack_from('<I', data, 0)[0]
    if magic != NIF_MAGIC:
        # Not encrypted, check if it's a plain NIF
        if data[:20].startswith(b'Gamebryo File Format'):
            return data
        return None

    # Header: magic(4) + compressed_size(4) ^ XOR_KEY1 + uncompressed_size(4) ^ XOR_KEY2
    comp_size = struct.unpack_from('<I', data, 4)[0] ^ XOR_KEY1
    uncomp_size = struct.unpack_from('<I', data, 8)[0] ^ XOR_KEY2

    compressed = data[12:12 + comp_size]

    try:
        decompressed = zlib.decompress(compressed)
    except zlib.error as e:
        print(f"  Decompression failed: {e}", file=sys.stderr)
        return None

    if len(decompressed) != uncomp_size:
        print(f"  Size mismatch: got {len(decompressed)}, expected {uncomp_size}", file=sys.stderr)

    return decompressed

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input.nif> <output.nif>")
        print(f"       {sys.argv[0]} <input_dir> <output_dir>  (batch mode)")
        sys.exit(1)

    src, dst = sys.argv[1], sys.argv[2]

    if os.path.isdir(src):
        os.makedirs(dst, exist_ok=True)
        count = 0
        for fname in sorted(os.listdir(src)):
            if not fname.lower().endswith('.nif'):
                continue
            in_path = os.path.join(src, fname)
            out_path = os.path.join(dst, fname)
            with open(in_path, 'rb') as f:
                data = f.read()
            result = decrypt_nif(data)
            if result:
                with open(out_path, 'wb') as f:
                    f.write(result)
                count += 1
                print(f"  {fname} ({len(data)//1024}K -> {len(result)//1024}K)")
        print(f"Decrypted {count} files to {dst}")
    else:
        with open(src, 'rb') as f:
            data = f.read()
        result = decrypt_nif(data)
        if result is None:
            print("Failed to decrypt (not an encrypted NIF?)")
            sys.exit(1)
        with open(dst, 'wb') as f:
            f.write(result)
        print(f"Decrypted: {len(data)//1024}K -> {len(result)//1024}K")

if __name__ == '__main__':
    main()
