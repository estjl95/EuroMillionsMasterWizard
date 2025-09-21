[Setup]
AppName=EuroMillions Master Wizard
AppVersion=1.6
AppId={{EuroMillionsMasterWizard}}
AppPublisher=José Estácio
AppComments=Programa concebido para prever números prováveis com base em estatísticas reais do EuroMilhões, utilizando métodos matemáticos para aumentar eficazmente as probabilidades de ganhar o jackpot.
AppCopyright=© 2025 José Estácio
AppPublisherURL=https://github.com/estjl95/EuroMillionsMasterWizard
DefaultDirName={pf}\EuroMillionsMasterWizard v1.6
DefaultGroupName=EuroMillions Master Wizard v1.6
OutputDir={Output}\EuroMillions Master Wizard v1.6
Uninstallable=yes
DisableDirPage=no
DisableProgramGroupPage=no
AllowNoIcons=no
PrivilegesRequired=admin
SetupIconFile=assets\icone.ico
UninstallDisplayIcon={app}\EuroMillionsMasterWizard.exe
UninstallDisplayName=EuroMillions Master Wizard v1.6
WizardStyle=modern
OutputBaseFilename=Setup
AlwaysShowComponentsList=false
ShowLanguageDialog=yes

[Languages]
Name: "pt"; MessagesFile: "compiler:Languages\Portuguese.isl"; LicenseFile: "LICENSE.txt"
Name: "en"; MessagesFile: "compiler:Default.isl"; LicenseFile: "LICENSE_English.txt"
Name: "fr"; MessagesFile: "compiler:Languages\French.isl"; LicenseFile: "LICENSE_Français.txt"
Name: "it"; MessagesFile: "compiler:Languages\Italian.isl"; LicenseFile: "LICENSE_Italiano.txt"
Name: "de"; MessagesFile: "compiler:Languages\German.isl"; LicenseFile: "LICENSE_Deutsch.txt"
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"; LicenseFile: "LICENSE_Español.txt"
Name: "tr"; MessagesFile: "compiler:Languages\Turkish.isl"; LicenseFile: "LICENSE_Türkçe.txt"

[Files]
Source: "dist\EuroMillionsMasterWizard.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\icone.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\splash.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "DejaVuSans.ttf"; DestDir: "{app}"; Flags: ignoreversion
Source: "dados\resultados_euromilhoes.xlsx"; DestDir: "{app}\dados"; Flags: ignoreversion skipifsourcedoesntexist
Source: "preferencias.json"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "dist\msgbox\msgbox.exe"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; Ficheiros de idioma
Source: "lang\pt.json"; DestDir: "{app}\lang"; Flags: ignoreversion
Source: "lang\en.json"; DestDir: "{app}\lang"; Flags: ignoreversion
Source: "lang\fr.json"; DestDir: "{app}\lang"; Flags: ignoreversion
Source: "lang\it.json"; DestDir: "{app}\lang"; Flags: ignoreversion
Source: "lang\de.json"; DestDir: "{app}\lang"; Flags: ignoreversion
Source: "lang\es.json"; DestDir: "{app}\lang"; Flags: ignoreversion
Source: "lang\tr.json"; DestDir: "{app}\lang"; Flags: ignoreversion


[Icons]
Name: "{group}\EuroMillions Master Wizard"; Filename: "{app}\EuroMillionsMasterWizard.exe"; IconFilename: "{app}\icone.ico"
Name: "{userdesktop}\EuroMillions Master Wizard"; Filename: "{app}\EuroMillionsMasterWizard.exe"; IconFilename: "{app}\icone.ico"; Tasks: desktopicon
Name: "{group}\EuroMillions Master Wizard - Página GitHub"; Filename: "https://github.com/estjl95/EuroMillionsMasterWizard"; IconFilename: "{app}\icone.ico"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho no ambiente de trabalho"; GroupDescription: "Opções adicionais:"; Flags: unchecked

[Run]
Filename: "{app}\EuroMillionsMasterWizard.exe"; Description: "Executar após instalação"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\dados"

[UninstallRun]
Filename: "{app}\msgbox.exe"; Parameters: "/lang={language} /msg=Obrigado por ter usado o EuroMillions Master Wizard!"; Flags: runhidden

[Code]
function ShouldSkipPage(PageID: Integer): Boolean;
begin
  if WizardSilent then
  begin
    if PageID = wpWelcome then Result := True;
    if PageID = wpSelectDir then Result := True;
    if PageID = wpSelectProgramGroup then Result := True;
    if PageID = wpFinished then Result := True;
  end else
    Result := False;
end;