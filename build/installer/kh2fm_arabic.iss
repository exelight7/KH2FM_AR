; KH2FM Arabic - fan translation installer (Inno Setup 6.7.3)
; Build: see BUILD_KIT.md (tools/gen_iss_files.py, tools/fetch_panacea.py, then ISCC installer/kh2fm_arabic.iss)
; Panacea files: downloaded at build time by tools/fetch_panacea.py into ../vendor (config/panacea.json)
; Test-only switches (never needed by players):
;   /STEAMROOT=<dir>  use this Steam folder instead of the registry
;   /GAMEDIR=<dir>    use this game folder (skips detection)
;   /TESTNOREG=1      no "Apps & features" entry (scratch tests)
;   /TESTCORRUPT=<n>  treat payload file number n as corrupt (tests the undo path)

#ifndef AppVer
  #define AppVer "1.0.0-beta"
#endif
#ifndef AppVerNum
  #define AppVerNum "1.0.0.0"
#endif
#define AppGuid "8F3C2A71-6E0B-4D5C-9A1E-2B7D4F60C3A9"
; Payload = installed mod files laid out as config/FROZEN_MANIFEST.tsv; supplied by the build job
#define Payload "..\payload\kh2"
#define Vendor "..\docs"
#define PanaceaDir "..\vendor\openkh-release2-1691\openkh\Apps"

[Setup]
AppId={{{#AppGuid}}
AppName=KH2FM Arabic
AppVersion={#AppVer}
AppVerName=KH2FM Arabic {#AppVer}
AppPublisher=KH2FM Arabic fan project (unofficial)
UninstallDisplayName=KH2FM Arabic - تعريب Kingdom Hearts II Final Mix ({#AppVer})
DefaultDirName={localappdata}\KH2FM-Arabic
DisableDirPage=yes
DisableProgramGroupPage=yes
DisableReadyPage=no
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=commandline
UsedUserAreasWarning=no
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CreateUninstallRegKey=not IsTestMode
ShowLanguageDialog=yes
WizardStyle=modern
#ifdef FAST
Compression=none
#else
Compression=lzma2/max
SolidCompression=yes
LZMAUseSeparateProcess=yes
#endif
OutputDir=..\dist
OutputBaseFilename=KH2FM-Arabic-Setup-{#AppVer}
VersionInfoVersion={#AppVerNum}
VersionInfoProductVersion={#AppVerNum}
VersionInfoDescription=KH2FM Arabic fan translation installer
CloseApplications=no
SetupLogging=yes

[Languages]
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
arabic.WelcomeLabel1=تعريب Kingdom Hearts II Final Mix
arabic.WelcomeLabel2=هذا المثبِّت يضيف الترجمة العربية إلى Kingdom Hearts II Final Mix ضمن KINGDOM HEARTS -HD 1.5+2.5 ReMIX- على Steam.%n%n• تحتاج نسخة أصلية من اللعبة على Steam.%n• هذه ترجمة هواة غير رسمية، لا علاقة لها بـ Square Enix أو Disney.%n• ملفات اللعبة الأصلية لا تتغيّر؛ يمكنك الإزالة في أي وقت من «التطبيقات» في ويندوز.%n%nاضغط «التالي» للمتابعة.
english.WelcomeLabel1=Arabic translation for Kingdom Hearts II Final Mix
english.WelcomeLabel2=This installer adds the Arabic fan translation to Kingdom Hearts II Final Mix in KINGDOM HEARTS -HD 1.5+2.5 ReMIX- on Steam.%n%n• You need a legal Steam copy of the game.%n• This is an unofficial fan translation, not affiliated with Square Enix or Disney.%n• The original game files are not changed; uninstall any time from Windows "Apps & features".%n%nClick Next to continue.
arabic.FinishedHeadingLabel=اكتمل التثبيت
arabic.FinishedLabelNoIcons=تم تثبيت التعريب.%n%nشغّل اللعبة من Steam كالمعتاد: المكتبة ← KINGDOM HEARTS -HD 1.5+2.5 ReMIX- ← تشغيل ← Kingdom Hearts II Final Mix.
arabic.FinishedLabel=تم تثبيت التعريب.%n%nشغّل اللعبة من Steam كالمعتاد: المكتبة ← KINGDOM HEARTS -HD 1.5+2.5 ReMIX- ← تشغيل ← Kingdom Hearts II Final Mix.
english.FinishedHeadingLabel=Installation complete
english.FinishedLabelNoIcons=The Arabic translation is installed.%n%nLaunch the game from Steam as usual: Library > KINGDOM HEARTS -HD 1.5+2.5 ReMIX- > Play > Kingdom Hearts II Final Mix.
english.FinishedLabel=The Arabic translation is installed.%n%nLaunch the game from Steam as usual: Library > KINGDOM HEARTS -HD 1.5+2.5 ReMIX- > Play > Kingdom Hearts II Final Mix.

[CustomMessages]
arabic.GameCaption=مجلد اللعبة
arabic.GameDesc=لم نعثر على اللعبة تلقائياً.
arabic.GameHint=اختر مجلد «KINGDOM HEARTS -HD 1.5+2.5 ReMIX-». تجده عادةً في:%nC:\Program Files (x86)\Steam\steamapps\common\KINGDOM HEARTS -HD 1.5+2.5 ReMIX-%n(أو في Steam: كليك يمين على اللعبة ← إدارة ← تصفّح الملفات المحلية).
arabic.GameBad=هذا المجلد لا يحتوي على «KINGDOM HEARTS II FINAL MIX.exe». اختر مجلد اللعبة الصحيح.
arabic.LangCaption=تنبيه: لغة اللعبة في Steam
arabic.LangDesc=التعريب يعمل فقط عندما تكون لغة اللعبة «English».
arabic.LangText=لغة اللعبة في Steam الآن: %1%n%nغيّرها إلى الإنجليزية بثلاث خطوات (يمكنك فعلها بعد انتهاء التثبيت):%n%n1) في Steam افتح «المكتبة» واضغط بالزر الأيمن على KINGDOM HEARTS -HD 1.5+2.5 ReMIX- ثم «خصائص».%n2) افتح تبويب «اللغة» واختر English.%n3) انتظر حتى ينتهي Steam من التحديث، ثم شغّل اللعبة.%n%nالمثبِّت لا يغيّر إعدادات Steam بنفسه.
arabic.TaskOpenKH=تثبيت OpenKH Mod Manager (للمتقدمين فقط) مع اختصار على سطح المكتب. تحذير: زر Build فيه يحذف مجلد المود ويعيد بناءه، فيُمسح التعريب حتى تعيد تشغيل هذا المثبِّت.
arabic.ReadyGame=مجلد اللعبة:
arabic.ReadyPanNew=Panacea (محمِّل المودات من OpenKH): سيُثبَّت الآن.
arabic.ReadyPanOld=Panacea (محمِّل المودات من OpenKH): موجود مسبقاً، سيبقى كما هو.
arabic.ReadyMod=مجلد ملفات التعريب:
arabic.ReadyBuildWarn=تنبيه: إذا كنت تستعمل OpenKH Mod Manager فإن زر Build يحذف هذه الملفات؛ أعد تشغيل هذا المثبِّت بعده.
arabic.ReadyLang=لغة اللعبة في Steam:
arabic.ErrNoGame=لم نعثر على مجلد اللعبة (KINGDOM HEARTS II FINAL MIX.exe). لم يتغيّر شيء.
arabic.ErrUnknownDll=في مجلد اللعبة ملف %1 لا يخص Panacea. لن نكتب فوقه. أزله أو انقله ثم أعد المحاولة. لم يتغيّر شيء.
arabic.ErrLongPath=مسار مجلد المود طويل جداً (%1 حرفاً، الحد 180). لم يتغيّر شيء.
arabic.ErrVerify=فشل التحقق من %1 ملفاً بعد النسخ (ربما القرص ممتلئ أو برنامج الحماية حجز ملفاً).%n%nأُعيد كل شيء كما كان، ولم يتغيّر شيء في اللعبة أو مجلد المود.%nأعد تنزيل المثبِّت وجرّب مرة أخرى.
english.GameCaption=Game folder
english.GameDesc=The game was not found automatically.
english.GameHint=Choose the "KINGDOM HEARTS -HD 1.5+2.5 ReMIX-" folder. It is usually:%nC:\Program Files (x86)\Steam\steamapps\common\KINGDOM HEARTS -HD 1.5+2.5 ReMIX-%n(or in Steam: right-click the game > Manage > Browse local files).
english.GameBad=This folder does not contain "KINGDOM HEARTS II FINAL MIX.exe". Choose the game folder.
english.LangCaption=Warning: game language in Steam
english.LangDesc=The translation only works when the game language is English.
english.LangText=The game language in Steam is now: %1%n%nSwitch it to English in three steps (you can do it after setup finishes):%n%n1) In Steam open Library, right-click KINGDOM HEARTS -HD 1.5+2.5 ReMIX- and choose Properties.%n2) Open the Language tab and choose English.%n3) Wait until Steam finishes updating, then start the game.%n%nSetup does not change Steam settings itself.
english.TaskOpenKH=Install OpenKH Mod Manager (advanced users only) with a desktop shortcut. Warning: its Build button deletes and rebuilds the mod folder, which removes the translation until you run this setup again.
english.ReadyGame=Game folder:
english.ReadyPanNew=Panacea (OpenKH mod loader): will be installed now.
english.ReadyPanOld=Panacea (OpenKH mod loader): already installed, kept as is.
english.ReadyMod=Translation files folder:
english.ReadyBuildWarn=Note: if you use OpenKH Mod Manager, its Build button deletes these files; run this setup again afterwards.
english.ReadyLang=Steam game language:
english.ErrNoGame=The game folder (KINGDOM HEARTS II FINAL MIX.exe) was not found. Nothing was changed.
english.ErrUnknownDll=The game folder contains a %1 that is not Panacea. Setup will not overwrite it. Remove or move it and try again. Nothing was changed.
english.ErrLongPath=The mod folder path is too long (%1 characters, limit 180). Nothing was changed.
english.ErrVerify=%1 file(s) failed verification after copying (disk full, or an antivirus locked a file?).%n%nEverything was put back as it was; nothing changed in the game or the mod folder.%nDownload the installer again and retry.

[Tasks]
Name: "openkh"; Description: "{cm:TaskOpenKH}"; Flags: unchecked

[Files]
; Panacea = official OpenKH release2-1691, installed exactly like the OpenKH Mod Manager does (only when missing)
Source: "{#PanaceaDir}\OpenKH.Panacea.dll"; DestDir: "{code:GameDirC}"; DestName: "DBGHELP.dll"; Flags: ignoreversion; Check: NeedPanacea; BeforeInstall: BackupIfNeeded('ea8eb87b45194927898e3084aecb5f36d3b4c1e2bfd7262b85c11d3e603b52ea'); AfterInstall: VerifyFile('ea8eb87b45194927898e3084aecb5f36d3b4c1e2bfd7262b85c11d3e603b52ea', False)
Source: "{#PanaceaDir}\avcodec-vgmstream-59.dll"; DestDir: "{code:GameDirC}\dependencies"; Flags: ignoreversion; Check: NeedPanacea; BeforeInstall: BackupIfNeeded('4d6cf54e7b3c26ef06e95bdb515a10d1e1bed3ec1ffd87ec3e5c4fbcd2a883f6'); AfterInstall: VerifyFile('4d6cf54e7b3c26ef06e95bdb515a10d1e1bed3ec1ffd87ec3e5c4fbcd2a883f6', False)
Source: "{#PanaceaDir}\avformat-vgmstream-59.dll"; DestDir: "{code:GameDirC}\dependencies"; Flags: ignoreversion; Check: NeedPanacea; BeforeInstall: BackupIfNeeded('0dde66ea268cccb67b1aa219c1ce879602b839e561a79a00c8215e2688f1a4b2'); AfterInstall: VerifyFile('0dde66ea268cccb67b1aa219c1ce879602b839e561a79a00c8215e2688f1a4b2', False)
Source: "{#PanaceaDir}\avutil-vgmstream-57.dll"; DestDir: "{code:GameDirC}\dependencies"; Flags: ignoreversion; Check: NeedPanacea; BeforeInstall: BackupIfNeeded('a999856c17cfdce3c22b92b6640a7ada6c4ab4c3c6841a863770b72fa0bc19b4'); AfterInstall: VerifyFile('a999856c17cfdce3c22b92b6640a7ada6c4ab4c3c6841a863770b72fa0bc19b4', False)
Source: "{#PanaceaDir}\bass.dll"; DestDir: "{code:GameDirC}\dependencies"; Flags: ignoreversion; Check: NeedPanacea; BeforeInstall: BackupIfNeeded('4bbb323f48fa7ea549abd59ecfc30e71b574d20f52e295b7e3ebf19f07f53efe'); AfterInstall: VerifyFile('4bbb323f48fa7ea549abd59ecfc30e71b574d20f52e295b7e3ebf19f07f53efe', False)
Source: "{#PanaceaDir}\bass_vgmstream.dll"; DestDir: "{code:GameDirC}\dependencies"; Flags: ignoreversion; Check: NeedPanacea; BeforeInstall: BackupIfNeeded('1612c3500436302e0fc3c6e9b1f359c8d38f52304c59d2ae0aeadd12207caabc'); AfterInstall: VerifyFile('1612c3500436302e0fc3c6e9b1f359c8d38f52304c59d2ae0aeadd12207caabc', False)
Source: "{#PanaceaDir}\libatrac9.dll"; DestDir: "{code:GameDirC}\dependencies"; Flags: ignoreversion; Check: NeedPanacea; BeforeInstall: BackupIfNeeded('fe82f1ae13a798337e03942c35351997c23caadb5eb0c6b7a2dc2a521ed8b02e'); AfterInstall: VerifyFile('fe82f1ae13a798337e03942c35351997c23caadb5eb0c6b7a2dc2a521ed8b02e', False)
Source: "{#PanaceaDir}\libcelt-0061.dll"; DestDir: "{code:GameDirC}\dependencies"; Flags: ignoreversion; Check: NeedPanacea; BeforeInstall: BackupIfNeeded('542254723d9100f91cbf18e41c4aff80287c22a9859e9e545c413d984df440ad'); AfterInstall: VerifyFile('542254723d9100f91cbf18e41c4aff80287c22a9859e9e545c413d984df440ad', False)
Source: "{#PanaceaDir}\libcelt-0110.dll"; DestDir: "{code:GameDirC}\dependencies"; Flags: ignoreversion; Check: NeedPanacea; BeforeInstall: BackupIfNeeded('bfcc51d865bb3b6a2793381bf535f23ec423feb722b46333fa8556ccdcafa61a'); AfterInstall: VerifyFile('bfcc51d865bb3b6a2793381bf535f23ec423feb722b46333fa8556ccdcafa61a', False)
Source: "{#PanaceaDir}\libg719_decode.dll"; DestDir: "{code:GameDirC}\dependencies"; Flags: ignoreversion; Check: NeedPanacea; BeforeInstall: BackupIfNeeded('aad61f205ce1f1b61285f6b37b90a331ec8c6ae2f94f361714dc21a12c236960'); AfterInstall: VerifyFile('aad61f205ce1f1b61285f6b37b90a331ec8c6ae2f94f361714dc21a12c236960', False)
Source: "{#PanaceaDir}\libmpg123-0.dll"; DestDir: "{code:GameDirC}\dependencies"; Flags: ignoreversion; Check: NeedPanacea; BeforeInstall: BackupIfNeeded('db9eb1d91b8eb9f47b0968201dbf6c51a9627e539a78afd9ad5f59c5d18fe4df'); AfterInstall: VerifyFile('db9eb1d91b8eb9f47b0968201dbf6c51a9627e539a78afd9ad5f59c5d18fe4df', False)
Source: "{#PanaceaDir}\libspeex-1.dll"; DestDir: "{code:GameDirC}\dependencies"; Flags: ignoreversion; Check: NeedPanacea; BeforeInstall: BackupIfNeeded('04dbc85fcec6c54671535bf39937a70f2dd040a81ad670a0b84de6ca17b39bff'); AfterInstall: VerifyFile('04dbc85fcec6c54671535bf39937a70f2dd040a81ad670a0b84de6ca17b39bff', False)
Source: "{#PanaceaDir}\libvorbis.dll"; DestDir: "{code:GameDirC}\dependencies"; Flags: ignoreversion; Check: NeedPanacea; BeforeInstall: BackupIfNeeded('5f330a20b19b3c70dc43eedcc95891e65940fca04a77155c573efcdd4c2ca665'); AfterInstall: VerifyFile('5f330a20b19b3c70dc43eedcc95891e65940fca04a77155c573efcdd4c2ca665', False)
Source: "{#PanaceaDir}\swresample-vgmstream-4.dll"; DestDir: "{code:GameDirC}\dependencies"; Flags: ignoreversion; Check: NeedPanacea; BeforeInstall: BackupIfNeeded('688a81d31ef98a9a6143e1075b2f4c5b79bdfa51e7a14d50d662a0e916dac739'); AfterInstall: VerifyFile('688a81d31ef98a9a6143e1075b2f4c5b79bdfa51e7a14d50d662a0e916dac739', False)
; documents for the player (kept in the install folder, removed on uninstall)
Source: "..\docs\README.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\docs\KNOWN_ISSUES.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\docs\CREDITS.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\docs\THIRD_PARTY_LICENSES.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\docs\DISCLAIMER.txt"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\docs\CHANGELOG.md"; DestDir: "{app}\docs"; Flags: ignoreversion skipifsourcedoesntexist
Source: "{#Vendor}\licenses\*"; DestDir: "{app}\docs\licenses"; Flags: ignoreversion
; optional: the full official OpenKH release (Mod Manager), own folder
Source: "..\vendor\openkh-release2-1691\openkh\*"; DestDir: "{app}\OpenKH"; Flags: ignoreversion recursesubdirs createallsubdirs; Tasks: openkh

[Icons]
Name: "{autodesktop}\OpenKH Mod Manager"; Filename: "{app}\OpenKH\OpenKh.Tools.ModsManager.exe"; WorkingDir: "{app}\OpenKH"; Tasks: openkh

#include "payload_files.iss"

[Code]
const
  KH2Exe = 'KINGDOM HEARTS II FINAL MIX.exe';
  GameSub = 'steamapps\common\KINGDOM HEARTS -HD 1.5+2.5 ReMIX-';
  AppManifest = 'appmanifest_2552430.acf';
  BakExt = '.kh2ar.bak';
  MaxModLen = 180;
  StateFile = 'kh2ar_state.txt';
  BackupList = 'kh2ar_backups.txt';
  DirList = 'kh2ar_dirs.txt';

var
  GameDir, ModRoot, ManifestPath, SteamLang, PanaceaDll: String;
  GameFound, PanaceaPresent, InstallStarted, InstallOK, UndoDone, SettingsWritten: Boolean;
  GamePage: TInputDirWizardPage;
  LangPage: TOutputMsgWizardPage;
  Installed, Backups, CreatedDirs: TStringList;
  FailCount, PayloadDone, CorruptAt: Integer;

{ ---------- small helpers ---------- }

function IsTestMode: Boolean;
begin
  Result := ExpandConstant('{param:TESTNOREG|0}') = '1';
end;

{ test mode may only touch the scratch tree that holds the fake Steam folder }
function InTestRoot(P: String): Boolean;
var r: String;
begin
  r := ExtractFileDir(RemoveBackslashUnlessRoot(ExpandConstant('{param:STEAMROOT|}')));
  Result := (Length(r) > 3) and (Pos(LowerCase(AddBackslash(r)), LowerCase(AddBackslash(P))) = 1);
end;

function GameDirC(Param: String): String;
begin
  Result := GameDir;
end;

function ModKh2Dir(Param: String): String;
begin
  Result := ModRoot + '\kh2';
end;

function NeedPanacea: Boolean;
begin
  Result := not PanaceaPresent;
end;

{ all double-quoted tokens of a VDF/ACF line }
function QuotedTokens(Line: String): TArrayOfString;
var i, p: Integer; inq: Boolean; cur: String;
begin
  SetArrayLength(Result, 0); inq := False; cur := '';
  for i := 1 to Length(Line) do begin
    if Line[i] = '"' then begin
      if inq then begin
        p := GetArrayLength(Result); SetArrayLength(Result, p + 1); Result[p] := cur; cur := '';
      end;
      inq := not inq;
    end else if inq then cur := cur + Line[i];
  end;
end;

function VdfValue(Line, Key: String): String;
var t: TArrayOfString;
begin
  Result := '';
  t := QuotedTokens(Line);
  if (GetArrayLength(t) >= 2) and (CompareText(t[0], Key) = 0) then begin
    Result := t[1];
    StringChangeEx(Result, '\\', '\', True);
  end;
end;

function IsGameDir(D: String): Boolean;
begin
  Result := (D <> '') and FileExists(AddBackslash(D) + KH2Exe);
end;

{ ---------- detection ---------- }

procedure AddUnique(L: TStringList; S: String);
begin
  S := RemoveBackslashUnlessRoot(S);
  if (S <> '') and (L.IndexOf(S) < 0) then L.Add(S);
end;

function FindGame: Boolean;
var roots, libs: TStringList; s, v: String; lines: TArrayOfString; i, j: Integer;
begin
  Result := False;
  roots := TStringList.Create; libs := TStringList.Create;
  try
    s := ExpandConstant('{param:STEAMROOT|}');
    if s <> '' then AddUnique(roots, s)
    else begin
      if RegQueryStringValue(HKCU, 'Software\Valve\Steam', 'SteamPath', s) then begin
        StringChangeEx(s, '/', '\', True); AddUnique(roots, s);
      end;
      if RegQueryStringValue(HKLM32, 'SOFTWARE\Valve\Steam', 'InstallPath', s) then AddUnique(roots, s);
      if RegQueryStringValue(HKLM64, 'SOFTWARE\Valve\Steam', 'InstallPath', s) then AddUnique(roots, s);
      AddUnique(roots, ExpandConstant('{commonpf32}\Steam'));
    end;
    for i := 0 to roots.Count - 1 do begin
      AddUnique(libs, roots[i]);
      if LoadStringsFromFile(roots[i] + '\steamapps\libraryfolders.vdf', lines) then
        for j := 0 to GetArrayLength(lines) - 1 do begin
          v := VdfValue(lines[j], 'path');
          if v <> '' then AddUnique(libs, v);
        end;
    end;
    for i := 0 to libs.Count - 1 do
      if IsGameDir(libs[i] + '\' + GameSub) then begin
        GameDir := libs[i] + '\' + GameSub;
        ManifestPath := libs[i] + '\steamapps\' + AppManifest;
        Result := True;
        Log('KH2AR: game found in library ' + libs[i]);
        Exit;
      end;
    Log(Format('KH2AR: game not found (%d roots, %d libraries)', [roots.Count, libs.Count]));
  finally
    roots.Free; libs.Free;
  end;
end;

{ read-only: "language" from appmanifest_2552430.acf (first one = UserConfig) }
procedure ReadSteamLanguage;
var lines: TArrayOfString; i: Integer; v: String;
begin
  SteamLang := '';
  if ManifestPath = '' then
    ManifestPath := ExpandFileName(AddBackslash(GameDir) + '..\..\' + AppManifest);
  if LoadStringsFromFile(ManifestPath, lines) then
    for i := 0 to GetArrayLength(lines) - 1 do begin
      v := VdfValue(lines[i], 'language');
      if v <> '' then begin SteamLang := v; Break; end;
    end;
  Log(Format('KH2AR: steam language=[%s] warn=%d manifest=%s', [SteamLang, Ord((SteamLang <> '') and (CompareText(SteamLang, 'english') <> 0)), ManifestPath]));
end;

function LangWarn: Boolean;
begin
  Result := (SteamLang <> '') and (CompareText(SteamLang, 'english') <> 0);
end;

function IsPanaceaFile(F: String): Boolean;
var s: AnsiString;
begin
  Result := LoadStringFromFile(F, s) and (Pos('panacea_settings.txt', s) > 0);
end;

{ Panacea present? which mod folder? (PANACEA_NOTES 2-4) }
procedure DetectPanacea;
var lines: TArrayOfString; i: Integer; v, f: String;
begin
  PanaceaPresent := False; PanaceaDll := '';
  for i := 0 to 1 do begin
    if i = 0 then f := 'DBGHELP.dll' else f := 'version.dll';
    if FileExists(AddBackslash(GameDir) + f) then begin
      if IsPanaceaFile(AddBackslash(GameDir) + f) then PanaceaPresent := True
      else if PanaceaDll = '' then PanaceaDll := f;   { unknown DLL with Panacea's name }
    end;
  end;
  if PanaceaPresent then PanaceaDll := '';
  if PanaceaPresent then begin
    v := './mod';   { Panacea default }
    if LoadStringsFromFile(AddBackslash(GameDir) + 'panacea_settings.txt', lines) then
      for i := 0 to GetArrayLength(lines) - 1 do
        if (Copy(lines[i], 1, 9) = 'mod_path=') and (Length(Trim(lines[i])) > 9) then
          v := Copy(lines[i], 10, Length(lines[i]));
    StringChangeEx(v, '/', '\', True);
    if not ((Length(v) >= 2) and (v[2] = ':')) and (Copy(v, 1, 2) <> '\\') then
      v := AddBackslash(GameDir) + v;
    ModRoot := RemoveBackslashUnlessRoot(ExpandFileName(v));
  end else
    ModRoot := ExpandConstant('{app}') + '\mod';
  Log(Format('KH2AR: panacea present=%d unknown=[%s] mod_root=%s', [Ord(PanaceaPresent), PanaceaDll, ModRoot]));
end;

{ ---------- wizard ---------- }

function InitializeSetup: Boolean;
begin
  Installed := TStringList.Create; Backups := TStringList.Create; CreatedDirs := TStringList.Create;
  CorruptAt := StrToIntDef(ExpandConstant('{param:TESTCORRUPT|0}'), 0);
  GameDir := ExpandConstant('{param:GAMEDIR|}');
  if GameDir <> '' then GameFound := IsGameDir(GameDir) else GameFound := FindGame;
  if GameFound then ReadSteamLanguage;
  Result := True;
end;

procedure InitializeWizard;
begin
  GamePage := CreateInputDirPage(wpWelcome, CustomMessage('GameCaption'), CustomMessage('GameDesc'),
    CustomMessage('GameHint'), False, '');
  GamePage.Add('');   { no default: a pre-filled path could be accepted without the player choosing it }
  LangPage := CreateOutputMsgPage(GamePage.ID, CustomMessage('LangCaption'), CustomMessage('LangDesc'), '');
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
  if PageID = GamePage.ID then Result := GameFound or WizardSilent   { silent: PrepareToInstall reports "not found" }
  else if PageID = LangPage.ID then begin
    Result := not LangWarn;
    if not Result then LangPage.MsgLabel.Caption := FmtMessage(CustomMessage('LangText'), [SteamLang]);
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = GamePage.ID then begin
    if not IsGameDir(GamePage.Values[0]) then begin
      SuppressibleMsgBox(CustomMessage('GameBad'), mbError, MB_OK, IDOK);
      Result := False;
    end else begin
      GameDir := RemoveBackslashUnlessRoot(GamePage.Values[0]); GameFound := True;
      ManifestPath := ''; ReadSteamLanguage;
    end;
  end;
end;

function UpdateReadyMemo(Space, NewLine, MemoUserInfoInfo, MemoDirInfo, MemoTypeInfo, MemoComponentsInfo, MemoGroupInfo, MemoTasksInfo: String): String;
var lang: String;
begin
  DetectPanacea;
  Result := CustomMessage('ReadyGame') + NewLine + Space + GameDir + NewLine + NewLine;
  if PanaceaPresent then
    Result := Result + CustomMessage('ReadyPanOld') + NewLine + NewLine
  else
    Result := Result + CustomMessage('ReadyPanNew') + NewLine + NewLine;
  Result := Result + CustomMessage('ReadyMod') + NewLine + Space + ModRoot + '\kh2' + NewLine;
  if PanaceaPresent then Result := Result + Space + CustomMessage('ReadyBuildWarn') + NewLine;
  lang := SteamLang; if lang = '' then lang := '?';
  Result := Result + NewLine + CustomMessage('ReadyLang') + ' ' + lang + NewLine;
  if MemoTasksInfo <> '' then Result := Result + NewLine + MemoTasksInfo;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  if not GameFound or not IsGameDir(GameDir) then begin
    Result := CustomMessage('ErrNoGame'); Log('KH2AR: ' + Result); Exit;
  end;
  DetectPanacea;
  if IsTestMode and not (InTestRoot(GameDir) and InTestRoot(ModRoot) and InTestRoot(ExpandConstant('{app}'))) then begin
    Result := 'TEST MODE: game, mod and install folders must all be inside /STEAMROOT''s parent folder.';
    Log('KH2AR: ' + Result); Exit;
  end;
  if PanaceaDll <> '' then begin
    Result := FmtMessage(CustomMessage('ErrUnknownDll'), [PanaceaDll]); Log('KH2AR: ' + Result); Exit;
  end;
  if Length(ModRoot) > MaxModLen then begin
    Result := FmtMessage(CustomMessage('ErrLongPath'), [IntToStr(Length(ModRoot))]); Log('KH2AR: ' + Result);
  end;
end;

{ ---------- install: backup, verify, undo ---------- }

procedure NoteDir(D: String);
begin
  if (D <> '') and not DirExists(D) and (CreatedDirs.IndexOf(D) < 0) then CreatedDirs.Add(D);
end;

{ remember every folder this run will create, so undo/uninstall can remove exactly those }
procedure CollectNewDirs;
var L: TStringList; i: Integer; k: String;
begin
  NoteDir(ExpandConstant('{app}'));
  NoteDir(ModRoot); k := ModRoot + '\kh2'; NoteDir(k);
  if not PanaceaPresent then NoteDir(GameDir + '\dependencies');
  NoteDir(ExpandConstant('{app}') + '\docs'); NoteDir(ExpandConstant('{app}') + '\docs\licenses');
  L := TStringList.Create;
  try
    AddPayloadDirs(L);
    for i := 0 to L.Count - 1 do NoteDir(k + '\' + L[i]);
  finally
    L.Free;
  end;
end;

procedure BackupIfNeeded(Sha: String);
var t: String;
begin
  t := ExpandConstant(CurrentFileName);
  if not FileExists(t) then Exit;
  if LowerCase(GetSHA256OfFile(t)) = Sha then Exit;      { already our file (re-install) }
  if FileExists(t + BakExt) then Exit;                    { original already saved by an earlier install }
  if RenameFile(t, t + BakExt) then begin
    Backups.Add(t); Log('KH2AR: backup ' + t);
  end else
    Log('KH2AR: BACKUP FAILED ' + t);
end;

procedure VerifyFile(Sha: String; IsPayload: Boolean);
var t, got: String;
begin
  t := ExpandConstant(CurrentFileName);
  Installed.Add(t);
  if IsPayload then PayloadDone := PayloadDone + 1;
  try
    got := LowerCase(GetSHA256OfFile(t));
  except
    got := '';
  end;
  if IsPayload and (PayloadDone = CorruptAt) then got := 'test-corrupt';
  if got <> Sha then begin
    FailCount := FailCount + 1; Log('KH2AR: VERIFY FAIL ' + t);
  end;
end;

procedure RestoreBackupList(L: TStringList);
var i: Integer;
begin
  for i := L.Count - 1 downto 0 do
    if FileExists(L[i] + BakExt) then begin
      if FileExists(L[i]) then DeleteFile(L[i]);
      if RenameFile(L[i] + BakExt, L[i]) then Log('KH2AR: restored ' + L[i])
      else Log('KH2AR: RESTORE FAILED ' + L[i]);
    end;
end;

{ deepest first; RemoveDir only succeeds on empty folders }
procedure RemoveDirList(L: TStringList);
var i, j: Integer; s: String;
begin
  for i := 0 to L.Count - 2 do
    for j := i + 1 to L.Count - 1 do
      if Length(L[j]) > Length(L[i]) then begin s := L[i]; L[i] := L[j]; L[j] := s; end;
  for i := 0 to L.Count - 1 do RemoveDir(L[i]);
end;

function UninstKey: String;
begin
  Result := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppGuid}_is1';
end;

procedure Undo;
var i: Integer; a: String;
begin
  if UndoDone then Exit;
  UndoDone := True;
  Log(Format('KH2AR: UNDO (%d files, %d backups)', [Installed.Count, Backups.Count]));
  for i := 0 to Installed.Count - 1 do DeleteFile(Installed[i]);
  if SettingsWritten then DeleteFile(GameDir + '\panacea_settings.txt');
  RestoreBackupList(Backups);
  a := ExpandConstant('{app}');
  if CreatedDirs.IndexOf(a) >= 0 then begin   { first install: drop the uninstaller and our docs too }
    DeleteFile(a + '\unins000.exe'); DeleteFile(a + '\unins000.dat'); DeleteFile(a + '\unins000.msg');
    DelTree(a + '\docs', True, True, True);
    if not IsTestMode then RegDeleteKeyIncludingSubkeys(HKA, UninstKey);
  end;
  RemoveDirList(CreatedDirs);
end;

{ UTF-8 without BOM so Arabic letters in paths survive (TStringList.SaveToFile and INI files would not) }
procedure SaveListUTF8(FileName: String; L: TStringList);
var a: TArrayOfString; i: Integer;
begin
  SetArrayLength(a, L.Count);
  for i := 0 to L.Count - 1 do a[i] := L[i];
  SaveStringsToUTF8FileWithoutBOM(FileName, a, False);
end;

function StateGet(FileName, Key, Def: String): String;
var lines: TArrayOfString; i: Integer;
begin
  Result := Def;
  if LoadStringsFromFile(FileName, lines) then
    for i := 0 to GetArrayLength(lines) - 1 do
      if Copy(lines[i], 1, Length(Key) + 1) = Key + '=' then
        Result := Copy(lines[i], Length(Key) + 2, Length(lines[i]));
end;

procedure MergeListFile(FileName: String; L: TStringList);
var old: TArrayOfString; m: TStringList; i: Integer;
begin
  m := TStringList.Create;
  try
    if LoadStringsFromFile(FileName, old) then
      for i := 0 to GetArrayLength(old) - 1 do AddUnique(m, old[i]);
    for i := 0 to L.Count - 1 do AddUnique(m, L[i]);
    SaveListUTF8(FileName, m);
  finally
    m.Free;
  end;
end;

function WriteSettings: Boolean;
var s: TArrayOfString; f: String;
begin
  f := GameDir + '\panacea_settings.txt';
  if FileExists(f) and not FileExists(f + BakExt) then
    if RenameFile(f, f + BakExt) then Backups.Add(f);
  SetArrayLength(s, 2);
  s[0] := 'mod_path=' + ModRoot;
  s[1] := 'show_console=false';
  Result := SaveStringsToUTF8FileWithoutBOM(f, s, False);
  SettingsWritten := Result;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var a: String; st: TStringList;
begin
  if CurStep = ssInstall then begin
    DetectPanacea;
    CollectNewDirs;
    InstallStarted := True;
  end else if CurStep = ssPostInstall then begin
    if (FailCount = 0) and (PayloadDone = {#PayloadCount}) and not PanaceaPresent then
      if not WriteSettings then FailCount := FailCount + 1;
    if (FailCount = 0) and (PayloadDone = {#PayloadCount}) then begin
      a := ExpandConstant('{app}');
      st := TStringList.Create;
      try
        st.Add('GameDir=' + GameDir);
        st.Add('ModRoot=' + ModRoot);
        if SettingsWritten then st.Add('SettingsByUs=1')   { keep the flag across re-installs }
        else st.Add('SettingsByUs=' + StateGet(a + '\' + StateFile, 'SettingsByUs', '0'));
        SaveListUTF8(a + '\' + StateFile, st);
      finally
        st.Free;
      end;
      MergeListFile(a + '\' + BackupList, Backups);
      MergeListFile(a + '\' + DirList, CreatedDirs);
      InstallOK := True;
      Log(Format('KH2AR: INSTALL OK payload=%d/%d backups=%d', [PayloadDone, {#PayloadCount}, Backups.Count]));
    end else begin
      if FailCount = 0 then FailCount := {#PayloadCount} - PayloadDone;
      Log(Format('KH2AR: INSTALL FAILED fails=%d payload=%d/%d', [FailCount, PayloadDone, {#PayloadCount}]));
      Undo;
      SuppressibleMsgBox(FmtMessage(CustomMessage('ErrVerify'), [IntToStr(FailCount)]), mbCriticalError, MB_OK, IDOK);
    end;
  end;
end;

function GetCustomSetupExitCode: Integer;
begin
  if InstallStarted and not InstallOK then Result := 9 else Result := 0;
end;

procedure DeinitializeSetup;
begin
  { cancel/abort during copying: Inno already rolled back its own files; put the originals back }
  if InstallStarted and not InstallOK then Undo;
end;

{ ---------- uninstall ---------- }

var
  UGameDir: String;
  UBackups, UDirs: TStringList;
  USettings: Boolean;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var a: String; lines: TArrayOfString; i: Integer;
begin
  a := ExpandConstant('{app}');
  if CurUninstallStep = usUninstall then begin
    UBackups := TStringList.Create; UDirs := TStringList.Create;
    UGameDir := StateGet(a + '\' + StateFile, 'GameDir', '');
    USettings := StateGet(a + '\' + StateFile, 'SettingsByUs', '0') = '1';
    if LoadStringsFromFile(a + '\' + BackupList, lines) then
      for i := 0 to GetArrayLength(lines) - 1 do AddUnique(UBackups, lines[i]);
    if LoadStringsFromFile(a + '\' + DirList, lines) then
      for i := 0 to GetArrayLength(lines) - 1 do AddUnique(UDirs, lines[i]);
  end else if CurUninstallStep = usPostUninstall then begin
    if USettings and (UGameDir <> '') then DeleteFile(UGameDir + '\panacea_settings.txt');
    RestoreBackupList(UBackups);
    DeleteFile(a + '\' + StateFile); DeleteFile(a + '\' + BackupList); DeleteFile(a + '\' + DirList);
    RemoveDirList(UDirs);
  end;
end;
