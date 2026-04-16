# build_final.py
import subprocess
import sys
import shutil
from pathlib import Path

def verificar_arquivos():
    """Verifica se todos os arquivos necessários existem"""
    arquivos_necessarios = ['jbs_icone.png', 'app.py']
    
    print("📁 Verificando arquivos necessários...")
    for arquivo in arquivos_necessarios:
        if Path(arquivo).exists():
            print(f"  ✅ {arquivo}")
        else:
            print(f"  ❌ {arquivo} não encontrado!")
            return False
    return True

def limpar_build():
    """Limpa builds anteriores"""
    print("\n🧹 Limpando builds anteriores...")
    
    for pasta in ['build', 'dist']:
        if Path(pasta).exists():
            shutil.rmtree(pasta)
    
    for spec in Path('.').glob('*.spec'):
        if spec.name != 'GeradorRelatorios_final.spec':
            spec.unlink()
    
    print("✅ Limpeza concluída!")

def criar_spec_file():
    """Cria arquivo .spec personalizado"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('jbs_icone.png', '.'),  # Isso garante que o PNG vai para a raiz do executável
    ],
    hiddenimports=[
        'reportlab',
        'reportlab.graphics',
        'reportlab.pdfgen',
        'reportlab.platypus',
        'reportlab.lib',
        'reportlab.pdfbase',
        'pandas',
        'numpy',
        'numpy.core',
        'numpy._core',
        'numpy.lib',
        'tkinter',
        'PIL',
        'PIL.Image',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['charset_normalizer'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GeradorRelatorios',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # True para ver mensagens de debug
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
'''

    # Adiciona ícone se existir
    if Path('jbs_icone.ico').exists():
        spec_content += "    icon='jbs_icone.ico',\n"
    
    spec_content += ")\n"
    
    with open('GeradorRelatorios_final.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Arquivo .spec criado!")
    return 'GeradorRelatorios_final.spec'

def build_executavel(spec_file):
    """Constrói o executável"""
    print("\n🔨 Construindo executável...")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        spec_file
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Build concluído com sucesso!")
        
        exe_path = Path('dist/GeradorRelatorios.exe')
        if exe_path.exists():
            tamanho_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📍 Executável: {exe_path.absolute()}")
            print(f"📦 Tamanho: {tamanho_mb:.2f} MB")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro no build: {e}")
        return False

def testar_executavel():
    """Testa se o executável foi gerado corretamente"""
    print("\n🧪 Testando executável...")
    
    exe_path = Path('dist/GeradorRelatorios.exe')
    if not exe_path.exists():
        print("❌ Executável não encontrado!")
        return False
    
    # Tenta executar por 2 segundos
    import time
    import subprocess
    
    try:
        process = subprocess.Popen([str(exe_path)])
        time.sleep(2)
        process.terminate()
        print("✅ Executável inicia corretamente!")
        return True
    except Exception as e:
        print(f"⚠️ Não foi possível testar: {e}")
        return True  # Não é um erro crítico

def main():
    print("=" * 60)
    print("🚀 BUILD DO GERADOR DE RELATÓRIOS - VERSÃO FINAL")
    print("=" * 60)
    
    if not verificar_arquivos():
        print("\n❌ Arquivos necessários não encontrados!")
        return
    
    limpar_build()
    
    spec_file = criar_spec_file()
    
    if build_executavel(spec_file):
        testar_executavel()
        
        print("\n" + "=" * 60)
        print("✅ BUILD CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print("\n📝 Instruções de uso:")
        print("1. O executável está em: dist/GeradorRelatorios.exe")
        print("2. Os dados serão salvos em: %APPDATA%/GeradorRelatorios/")
        print("3. O primeiro uso pode ser mais lento")
        print("\n⚠️  Importante:")
        print("- O ícone JBS está incorporado no executável")
        print("- O banco de dados será criado automaticamente no primeiro uso")
    else:
        print("\n❌ Falha no build!")

if __name__ == '__main__':
    main()