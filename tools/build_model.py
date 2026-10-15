from pathlib import Path
from io import BytesIO
import sys
import tarfile
import zipfile

def build(input_zip, output_tar):
    input_zip, output_tar = Path(input_zip), Path(output_tar)
    directories = {'am', 'conf', 'graph', 'ivector', 'rescore', 'rnnlm'}
    with zipfile.ZipFile(input_zip) as source:
        members = []
        for info in source.infolist():
            if info.is_dir():
                continue
            parts = Path(info.filename.replace('\\','/')).parts
            if len(parts) < 3 or parts[1] not in directories or '..' in parts:
                continue
            members.append((info, parts))
        required = ('am/final.mdl', 'conf/mfcc.conf')
        available = {'/'.join(parts[1:]) for _, parts in members}
        missing = [f for f in required if f not in available]
        if missing:
            raise SystemExit('Missing model files: '+', '.join(missing))
        output_tar.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(output_tar, 'w:gz', compresslevel=1) as target:
            for info, parts in members:
                data = source.read(info)
                tar_name = 'model/' + '/'.join(parts[1:])
                tar_info = tarfile.TarInfo(tar_name)
                tar_info.size = len(data)
                tar_info.mode = 0o644
                target.addfile(tar_info, BytesIO(data))
    print('Model ready:', output_tar.stat().st_size, 'bytes')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: python build_model.py input.zip output.tar.gz')
    build(sys.argv[1], sys.argv[2])
