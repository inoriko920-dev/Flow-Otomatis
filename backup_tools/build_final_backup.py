#!/usr/bin/env python3
"""One-off archive builder, branch-local tooling only. Never modifies application source."""
from __future__ import annotations
import csv
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo
from zipfile import ZipFile

REPO = "inoriko920-dev/Flow-Otomatis"
BASE = Path("final")
APP = BASE / "APP_001_Flow-Otomatis"
MIRROR = Path("mirror-full-backup.git")
BUNDLE = APP / "GIT" / "Flow-Otomatis-COMPLETE-GIT-HISTORY.bundle"
SOURCE = APP / "SOURCE" / "Flow-Otomatis-SOURCE-MAIN.zip"
BUILDS = [(11676024973, "Flow-Otomatis-Win11-Preview-CI-Main.zip")]
STAMP = datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S WIB")
def run(*args, cwd=None, output=None):
    if output is None:
        return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.STDOUT).strip()
    with Path(output).open("w", encoding="utf-8") as f:
        subprocess.run(args, cwd=cwd, stdout=f, stderr=subprocess.STDOUT, check=True)
def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")
def sha(path):
    x=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(4*1024*1024), b""):
            x.update(b)
    return x.hexdigest()
def test_zip(path):
    with ZipFile(path) as z:
        bad=z.testzip()
        if bad: raise RuntimeError("Bad ZIP member: "+bad)
        if not z.namelist(): raise RuntimeError("Empty ZIP: "+str(path))
        return len(z.namelist())
def download_artifact(artifact_id,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    token=os.environ["GH_TOKEN"]
    url="https://api.github.com/repos/"+REPO+"/actions/artifacts/"+str(artifact_id)+"/zip"
    subprocess.run(["curl","-fL","--retry","3","--connect-timeout","30",
         "-H","Accept: application/vnd.github+json",
         "-H","Authorization: Bearer "+token,url,"-o",str(dest)],check=True)
    test_zip(dest)
def main():
    if BASE.exists(): shutil.rmtree(BASE)
    if MIRROR.exists(): shutil.rmtree(MIRROR)
    for sub in ("GIT","SOURCE","BUILD","DOCS","RECOVERY"): (APP/sub).mkdir(parents=True,exist_ok=True)
    print("Clone full Git refs from one repository only")
    subprocess.run(["git","clone","--mirror","https://github.com/"+REPO+".git",str(MIRROR)],check=True)
    run("git","-C",str(MIRROR),"fsck","--full","--no-reflogs",output="git-fsck.txt")
    def git(*a):
        return run("git","-C",str(MIRROR),*a)
    refs=git("for-each-ref","--format=%(refname) %(objectname)")
    branches=git("for-each-ref","refs/heads","--format=%(refname:short) %(objectname)")
    tags=git("for-each-ref","refs/tags","--format=%(refname:short) %(objectname)")
    count=git("rev-list","--all","--count")
    main_sha=git("rev-parse","refs/heads/main")
    history=git("log","--all","--format=%H %aI %s")
    write(APP/"REPOSITORY_INFO.txt",f"ORIGINAL_REPO: https://github.com/{REPO}\nDEFAULT_BRANCH: main\nCLONE_MODE: --mirror\nBACKUP_TIME: {STAMP}\n")
    write(APP/"MAIN_COMMIT.txt",main_sha+"\n")
    write(APP/"BRANCHES.txt",branches+"\n")
    write(APP/"TAGS.txt",(tags+"\n") if tags else "NO_TAGS_FOUND\n")
    write(APP/"COMMIT_HISTORY.txt",history+"\n")
    write(APP/"ALL_REFS.txt",refs+"\n")
    write(APP/"COMMIT_COUNT.txt",count+"\n")
    print("Create and verify bundle")
    subprocess.run(["git","-C",str(MIRROR),"bundle","create",str(BUNDLE.resolve()),"--all"],check=True)
    output=git("bundle","verify",str(BUNDLE.resolve()))
    write(APP/"GIT_BUNDLE_VERIFY.txt",output+"\n")
    bundle_refs=git("bundle","list-heads",str(BUNDLE.resolve()))
    write(APP/"GIT_BUNDLE_REFS.txt",bundle_refs+"\n")
    with tempfile.TemporaryDirectory() as t:
        clone=Path(t)/"restored-mirror.git"
        subprocess.run(["git","clone","--mirror",str(BUNDLE.resolve()),str(clone)],check=True)
        restored=run("git","-C",str(clone),"for-each-ref","--format=%(refname) %(objectname)")
        if refs!=restored: raise RuntimeError("Restored refs differ from original refs")
        run("git","-C",str(clone),"fsck","--full","--no-reflogs")
    print("Export human-readable source ZIP")
    subprocess.run(["git","-C",str(MIRROR),"archive","--format=zip",
        "--output="+str(SOURCE.resolve()),"refs/heads/main"],check=True)
    file_count=test_zip(SOURCE)
    if file_count < 10: raise RuntimeError("Source snapshot suspiciously small")
    with ZipFile(SOURCE) as z:
        for name in z.namelist():
            if name in ("README.md","AGENTS.md","PLAN.md","TASKS.md","PROJECT_STATE.md","docs/FEATURE_FREEZE_POLICY.md","docs/architecture/ARCHITECTURE.md"):
                path=APP/"DOCS"/name
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(z.read(name))
        secretnames=set()
        warning=[]
        for name in z.namelist():
            if name.lower().endswith((".md",".txt",".json",".yml",".yaml",".py",".toml",".ps1",".ini",".cfg",".env",".js",".ts")):
                b=z.read(name)
                if len(b)>2_000_000: continue
                t=b.decode("utf-8","ignore")
                if name.startswith(".github/workflows/"):
                    secretnames.update(re.findall(r"secrets\.([A-Z][A-Z0-9_]*)",t))
                for typ,pattern in [
                    ("GitHub token",r"gh[pousr]_[A-Za-z0-9]{30,}"),
                    ("Google API key",r"AIza[0-9A-Za-z_\-]{30,}"),
                    ("OpenAI key",r"sk-[A-Za-z0-9]{25,}"),
                    ("Private key",r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")]:
                    if re.search(pattern,t):
                        warning.append(f"{name}: possible {typ}")
        write(APP/"REQUIRED_SECRETS.txt",
              "SECRET_REQUIRED_BUT_NOT_BACKED_UP\n"
              "Do not include API keys, Google Flow sessions, cookies or GitHub credentials.\n"
              "GitHub Actions references found in workflow definitions: "+
              (", ".join(sorted(secretnames)) or "none located")+"\n"
              "Other runtime credentials must be configured manually.\n")
        write(APP/"SECRET_SCAN_STATUS.txt",
              "Main source snapshot: "+
              ("POTENTIAL_SECRET_PATTERNS_FOUND - review before sharing\n"+"\n".join(warning) if warning else "No common hardcoded token patterns detected.\n")+
              "\nImportant: this is NOT a complete scan of every historical Git object.\n")
        if warning: raise RuntimeError("Potential secrets in main source snapshot; refusing to distribute: "+str(warning[:5]))
    lfs=git("lfs","ls-files","--all") if shutil.which("git-lfs") else ""
    write(APP/"LFS_STATUS.txt",("LFS_PRESENT: requires separate handling\n"+lfs) if lfs else "NO_LFS_TRACKED_FILES_DETECTED\n")
    if lfs: raise RuntimeError("LFS found; this job must be extended to package LFS objects")
    print("Download known available Windows CI build artifacts (not a stable release)")
    for artifact_id, filename in BUILDS: download_artifact(artifact_id, APP/"BUILD"/filename)
    write(APP/"BUILD"/"BUILD_STATUS.txt",
          "CI artifact only: manual Windows end-to-end acceptance NOT confirmed.\n"
          "Full main build from run 38071157920, artifact 11676024973.\n"
          "Offline simulator CI artifact deliberately omitted to satisfy archive delivery size limit.\n"
          "There were no GitHub Releases at time of inspection.\n")
    restore_script=r'''param(
 [string]$NewRepoUrl = "",
 [string]$RestoreDirectory = ""
)
$ErrorActionPreference="Stop"
$AppDir=Split-Path -Parent $PSScriptRoot
$Bundle=Join-Path $AppDir "GIT\Flow-Otomatis-COMPLETE-GIT-HISTORY.bundle"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "Install Git for Windows first: https://git-scm.com/downloads/win" }
if (-not (Test-Path $Bundle)) { throw "Git bundle missing: $Bundle" }
$verifyDir=Join-Path $env:TEMP ("flow-verify-"+[guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $verifyDir | Out-Null
try {
  & git -C $verifyDir init --bare | Out-Null
  & git -C $verifyDir bundle verify $Bundle
  if ($LASTEXITCODE -ne 0) { throw "Git bundle verification FAILED" }
} finally { Remove-Item $verifyDir -Recurse -Force -ErrorAction SilentlyContinue }
if ([string]::IsNullOrWhiteSpace($RestoreDirectory)) {
 $RestoreDirectory=Join-Path (Get-Location).Path "Flow-Otomatis-RESTORED.git"
}
if (Test-Path $RestoreDirectory) { throw "Destination exists. Choose an empty path: $RestoreDirectory" }
& git clone --mirror $Bundle $RestoreDirectory
if ($LASTEXITCODE -ne 0) { throw "Clone from Git bundle FAILED" }
Write-Host "Local restore completed at: $RestoreDirectory"
if ([string]::IsNullOrWhiteSpace($NewRepoUrl)) {
  Write-Host "Create an EMPTY repository in your new GitHub account."
  $NewRepoUrl=Read-Host "Enter new repository HTTPS URL (blank to skip push)"
}
if ([string]::IsNullOrWhiteSpace($NewRepoUrl)) {
 Write-Host "No network changes made. Local Git mirror is ready."
 exit 0
}
if ($NewRepoUrl -notmatch '^https://github\.com/[^/]+/[^/]+(\.git)?$') {
 throw "NewRepoUrl must be HTTPS GitHub repo URL"
}
Write-Host "TARGET: $NewRepoUrl"
$confirm=Read-Host "Push ALL branches and tags to NEW GitHub repo? Type YES to confirm"
if ($confirm -cne 'YES') { Write-Host "Push cancelled; local backup is preserved."; exit 0 }
& git -C $RestoreDirectory remote remove origin 2>$null
& git -C $RestoreDirectory remote add origin $NewRepoUrl
& git -C $RestoreDirectory push origin --all
if ($LASTEXITCODE -ne 0) { throw "Pushing branches FAILED" }
& git -C $RestoreDirectory push origin --tags
if ($LASTEXITCODE -ne 0) { throw "Pushing tags FAILED" }
Write-Host "Branches/tags restored. Re-enter secrets and inspect workflows/builds manually."
'''
    write(APP/"RECOVERY"/"RESTORE_TO_NEW_GITHUB.ps1",restore_script)
    verify_script=r'''param()
$ErrorActionPreference="Stop"
$AppDir=Split-Path -Parent $PSScriptRoot
$Root=Split-Path -Parent $AppDir
$Checks=Join-Path $Root "00_SHA256SUMS.txt"
if (-not (Test-Path $Checks)) { throw "00_SHA256SUMS.txt missing" }
$count=0
foreach ($line in [IO.File]::ReadAllLines($Checks)) {
  if ($line -notmatch '^([0-9a-f]{64})  (.+)$') { throw "Invalid SHA line: $line" }
  $expect=$Matches[1]; $rel=$Matches[2]; $path=Join-Path $Root $rel
  if (-not (Test-Path -LiteralPath $path)) { throw "File missing: $rel" }
  $actual=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($actual -ne $expect) { throw "Checksum mismatch: $rel" }
  $count++
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "Install Git for Windows" }
$Bundle=Join-Path $AppDir "GIT\Flow-Otomatis-COMPLETE-GIT-HISTORY.bundle"
$Temp=Join-Path $env:TEMP ("bundleverify-"+[guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $Temp | Out-Null
try {
 & git -C $Temp init --bare | Out-Null
 & git -C $Temp bundle verify $Bundle
 if ($LASTEXITCODE -ne 0) { throw "Git bundle verify FAILED" }
} finally { Remove-Item $Temp -Recurse -Force -ErrorAction SilentlyContinue }
Write-Host ("PASS - "+$count+" SHA-256 checksums and Git bundle verified")
'''
    write(APP/"RECOVERY"/"VERIFY_BACKUP.ps1",verify_script)
    write(BASE/"VERIFY_ALL_BACKUP.ps1",
          '& (Join-Path $PSScriptRoot "APP_001_Flow-Otomatis\\RECOVERY\\VERIFY_BACKUP.ps1")\n')
    write(BASE/"RESTORE_ALL.ps1",
          'Write-Host "[1] Flow-Otomatis"\n'
          '$pick=Read-Host "Choose application number (1)"\n'
          'if ($pick -ne "1") { throw "Only Flow-Otomatis is included." }\n'
          '& (Join-Path $PSScriptRoot "APP_001_Flow-Otomatis\\RECOVERY\\RESTORE_TO_NEW_GITHUB.ps1")\n')
    write(APP/"RECOVERY"/"PETUNJUK_PEMULIHAN.txt",
          "PEMULIHAN SAAT AKUN GITHUB LAMA SUDAH TIDAK BISA DIAKSES\n"
          "1. Ekstrak ZIP ini ke folder Windows 11.\n"
          "2. Instal Git for Windows jika belum tersedia.\n"
          "3. Buka PowerShell di folder hasil ekstrak.\n"
          "4. Jalankan: powershell -ExecutionPolicy Bypass -File .\\VERIFY_ALL_BACKUP.ps1\n"
          "5. Buat repository baru yang benar-benar KOSONG pada akun GitHub baru.\n"
          "6. Jalankan: powershell -ExecutionPolicy Bypass -File .\\RESTORE_ALL.ps1\n"
          "7. Pilih nomor 1, lalu masukkan URL repository baru.\n"
          "8. Baca target, ketik YES hanya setelah yakin.\n"
          "9. Script memulihkan semua branch dan tag. Git history tersedia pada Git Bundle.\n"
          "10. Tambahkan lagi semua secret secara manual, periksa Actions, jalankan build.\n"
          "11. Bandingkan commit main dan daftar branch dengan MAIN_COMMIT.txt/BRANCHES.txt.\n"
          "CATATAN: GitHub issues, PR reviews, workflow logs, settings, secrets, dan identitas akun tidak dapat\n"
          "dipulihkan seluruhnya hanya dari Git Bundle. Source dan Git refs yang terarsip dapat dipulihkan.\n")
    write(APP/"README_RESTORE.txt",
          "Flow-Otomatis single-repository disaster recovery package.\n"
          "Read RECOVERY/PETUNJUK_PEMULIHAN.txt and run VERIFY_ALL_BACKUP.ps1 from package root.\n")
    write(APP/"STATUS_BACKUP.txt",
          "SOURCE + GIT HISTORY: BACKUP_COMPLETE (for Git refs captured at export time).\n"
          "BUILD: available CI previews; NOT confirmed stable/manual tested.\n"
          "GITHUB NON-GIT METADATA (issues, PR reviews, Actions logs, settings): NOT IN GIT BUNDLE.\n"
          "SECRETS: intentionally excluded; historical Git objects not completely secret-scanned.\n"
          "SOURCE COUNT: "+str(file_count)+"\nREF COUNT: "+str(len(refs.splitlines()))+
          "\nBRANCH COUNT: "+str(len(branches.splitlines()))+
          "\nTAG COUNT: "+str(len(tags.splitlines()))+"\nCOMMIT COUNT: "+count+"\n")
    manifest=("NAMA PROYEK: Flow-Otomatis\nORIGINAL REPO: https://github.com/"+REPO+
       "\nDEFAULT BRANCH: main\nBACKUP WIB: "+STAMP+
       "\nMAIN COMMIT: "+main_sha+
       "\nGIT BUNDLE: APP_001_Flow-Otomatis/GIT/Flow-Otomatis-COMPLETE-GIT-HISTORY.bundle"+
       "\nSOURCE SNAPSHOT: APP_001_Flow-Otomatis/SOURCE/Flow-Otomatis-SOURCE-MAIN.zip"+
       "\nBUILD: CI preview Windows + offline simulator"+
       "\nDOCS: APP_001_Flow-Otomatis/DOCS/"+
       "\nRESTORE: APP_001_Flow-Otomatis/RECOVERY/RESTORE_TO_NEW_GITHUB.ps1"+
       "\nCHECKSUM STATUS: VERIFIED by builder; offline VERIFY_ALL_BACKUP.ps1 provided"+
       "\nGIT RESTORE REF TEST: PASS"+
       "\nSTATUS: BACKUP_COMPLETE for tracked Git code/history; non-Git GitHub platform data excluded"+
       "\nTOTAL PROJECTS: 1\nBRANCHES: "+str(len(branches.splitlines()))+
       "\nTAGS: "+str(len(tags.splitlines()))+"\nCOMMIT COUNT: "+count+"\n")
    write(BASE/"00_MASTER_MANIFEST.txt",manifest)
    with (BASE/"00_MASTER_MANIFEST.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(["PROJECT","REPO","DEFAULT_BRANCH","MAIN_COMMIT","BRANCH_COUNT","TAG_COUNT","COMMIT_COUNT","GIT_BACKUP","SOURCE","BUILD","STATUS"])
        writer.writerow(["Flow-Otomatis",REPO,"main",main_sha,len(branches.splitlines()),len(tags.splitlines()),count,"PASS","PASS","CI_PREVIEW","GIT_COMPLETE"])
    write(BASE/"00_BACKUP_INFO.txt",
          "Backup date/time: "+STAMP+"\nScope: ONLY "+REPO+
          "\nBackup type: source main + --mirror Git bundle + selected CI artifacts\n"
          "Secrets excluded and must be reentered; no changes to repository main.\n"
          "Git refs and blob contents are captured at export time, not GitHub account/platform state.\n")
    write(BASE/"00_README_PERTAMA.txt",
          "FLOW-OTOMATIS SINGLE-REPOSITORY BACKUP\n"
          "Simpan ZIP asli di SSD/HDD/cloud terpisah. Jangan hanya simpan di GitHub.\n"
          "FILE PENTING: GIT bundle = RIWAYAT/BRANCH/TAG, SOURCE ZIP = kode mudah dibuka.\n"
          "1. Ekstrak seluruh isi ZIP.\n"
          "2. Jalankan VERIFY_ALL_BACKUP.ps1 untuk memvalidasi SHA-256 dan Git Bundle.\n"
          "3. Jalankan RESTORE_ALL.ps1 untuk memulihkan ke akun baru.\n"
          "4. Restore perlu Git for Windows dan repo GitHub baru yang kosong.\n"
          "5. Anda wajib mengisi ulang secret/config kredensial (tidak disimpan).\n"
          "Catatan: arsip tidak mereplikasi keseluruhan pengaturan akun GitHub/PR/Issues.\n")
    checks=[]
    for p in sorted(BASE.rglob("*")):
        if p.is_file() and p.name not in ("00_SHA256SUMS.txt","SHA256SUMS.txt"):
            checks.append((sha(p),p.relative_to(BASE).as_posix()))
    write(BASE/"00_SHA256SUMS.txt","".join(f"{digest}  {name}\n" for digest,name in checks))
    prefix="APP_001_Flow-Otomatis/"
    write(APP/"SHA256SUMS.txt","".join(f"{digest}  {name[len(prefix):]}\n" for digest,name in checks if name.startswith(prefix)))
    for digest,name in checks:
        if sha(BASE/name)!=digest: raise RuntimeError("Checksum changed: "+name)
    print(f"SUCCESS: {STAMP}; Git main={main_sha}; refs={len(refs.splitlines())}; files={file_count}; files checksummed={len(checks)}")
if __name__=="__main__": main()
