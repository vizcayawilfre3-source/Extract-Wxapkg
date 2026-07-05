import struct, os, sys, re, json
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA1


def decrypt(wxid, path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:6] != b'V1MMWX':
        return data
    enc = data[6:]
    key = PBKDF2(wxid, b'saltiest', dkLen=32, count=1000, hmac_hash_module=SHA1)
    aes = AES.new(key, AES.MODE_CBC, b'the iv: 16 bytes').decrypt(enc[:1024])
    pad = aes[-1]
    if 1 <= pad <= 16:
        aes = aes[:-pad]
    xor_key = ord(wxid[-2]) if len(wxid) >= 2 else 0x66
    return aes + bytes(b ^ xor_key for b in enc[1024:])


def unpack(raw, out):
    mk, _, ilen, dlen, lk = struct.unpack_from('>BIIIB', raw)
    if mk != 0xBE or lk != 0xED:
        raise ValueError(f'bad wxapkg: mk=0x{mk:x} lk=0x{lk:x}')

    pos, end = 18, 14 + ilen
    files = []
    while pos + 8 <= end:
        if pos + 4 > len(raw):
            break
        nl = struct.unpack_from('>I', raw, pos)[0]
        pos += 4
        if nl > 4096 or pos + nl > end:
            break
        name = raw[pos:pos + nl].decode('utf-8', errors='replace')
        pos += nl
        if pos + 8 > end:
            break
        off, size = struct.unpack_from('>II', raw, pos)
        pos += 8
        if off + size <= len(raw):
            files.append((name, off, size))

    for name, off, size in files:
        p = os.path.join(out, name.lstrip('/'))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'wb') as f:
            f.write(raw[off:off + size])

    return files, out


def split_js(app_service):
    if not os.path.exists(app_service):
        return 0
    with open(app_service, 'r', encoding='utf-8') as f:
        code = f.read()
    base = os.path.dirname(app_service)
    n = 0
    for m in re.finditer(r'define\("([^"]+)",\s*function\s*\(', code):
        mp = m.group(1)
        i, d, s = m.end(), 0, False
        while i < len(code):
            c = code[i]
            if c == '{':
                d += 1; s = True
            elif c == '}':
                d -= 1
                if s and d == 0:
                    break
            elif c in '"\'':
                q = c; i += 1
                while i < len(code) and code[i] != q:
                    if code[i] == '\\': i += 1
                    i += 1
            i += 1
        body = code[m.start():i + 1]
        inner = body[body.index('{') + 1:body.rindex('}')].strip()
        p = os.path.join(base, mp + '.js')
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(inner)
        n += 1
    return n


def split_config(ac_path):
    if not os.path.exists(ac_path):
        return
    with open(ac_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    out = os.path.dirname(ac_path)
    app = {k: v for k, v in cfg.items() if k != 'pages'}
    with open(os.path.join(out, 'app.json'), 'w', encoding='utf-8') as f:
        json.dump(app, f, ensure_ascii=False, indent=2)
    for p in cfg.get('pages', []):
        pp = p if isinstance(p, str) else p.get('path', '')
        pc = {} if isinstance(p, str) else {k: v for k, v in p.items() if k != 'path'}
        if pp:
            fp = os.path.join(out, pp + '.json')
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            with open(fp, 'w', encoding='utf-8') as f:
                json.dump(pc, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    pkg = input('wxapkg路径: ').strip().strip('"')
    wxid = input('wxid (密钥): ').strip()
    out = input(f'输出目录 (回车={os.path.dirname(os.path.abspath(__file__))}\\output): ').strip()
    if not out:
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

    print()
    raw = decrypt(wxid, pkg)
    print(f'[+] 解密完成: {len(raw)} 字节')

    files, _ = unpack(raw, out)
    print(f'[+] 解包: {len(files)} 个文件')

    n1 = split_config(os.path.join(out, 'app-config.json'))
    n2 = split_js(os.path.join(out, 'app-service.js'))
    print(f'[+] JS模块: {n2}')

    print(f'\n完成 -> {out}')
